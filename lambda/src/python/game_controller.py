

import uuid
from botocore.exceptions import ClientError

import game_logic
from client_notifier import ClientNotifier
from connection import DatabaseConnection, transaction_retry
from dao.game_dao import GameDao, GameItem
from dao.player_dao import PlayerDao, PlayerItem
from dao.roll_dao import RollDao, RollItem
from dao.turn_dao import TurnDao, TurnItem


class GameController:
  """Responsible for game logic and state change"""
  
  client_notifier = ClientNotifier()
  player_dao = PlayerDao()
  game_dao = GameDao()
  roll_dao = RollDao()
  turn_dao = TurnDao()
  connection = DatabaseConnection()

  @staticmethod
  def create_unique_id():
    return str(uuid.uuid4())

  # Players

  def create_player(self, player_id):
    """Create a new player object for a new browser session"""
    with self.connection as conn:
      self.player_dao.create(conn, PlayerItem(id=player_id, win_counter=0))

  # @transaction_retry
  def delete_player(self, player_id):
    """Remove the player from the database, and any games/turns/rolls they are part of
    Transaction retry for if a player joins the game as we try to leave it.
    """
    with self.connection as conn:
      player_item = self.player_dao.get(conn, player_id)

    with self.connection as conn:
      turn_items = self.turn_dao.get_turns_with_player_id(conn, player_id)
      roll_items = self.roll_dao.get_rolls_with_game_id(conn, player_item.game_id) if player_item.game_id else []
      game_item = self.game_dao.get(conn, player_item.game_id) if player_item.game_id else None

    with self.connection as conn:
      self.player_dao.delete(conn, player_id)

      for turn_item in turn_items:
        self.turn_dao.delete(conn, turn_item.id)

      turn_ids = [t.id for t in turn_items]
      for roll_item in roll_items:
        if roll_item.turn_id in turn_ids:
          self.roll_dao.delete(conn, roll_item.id)

      if game_item is not None:
        game_item.num_players -= 1
        if game_item.num_players > 0:
          self.game_dao.set(conn, game_item)
        else:
          self.game_dao.delete_if_attribute_has_value(conn, game_item.id, 'num_players', '1')

    if game_item is not None:
      self.send_game_state_update(game_item.id)

  def set_nickname(self, player_id, nickname):
    """Sets a player's name, as seen by other players"""

    if not self._is_valid_nickname(nickname):
      self.client_notifier.send_notification(
        [player_id], 
        {'action': 'setNickname', 'error': 'Invalid nickname'}
      )
      return

    with self.connection as conn:
      player = self.player_dao.get(conn, player_id)
      
    player.nickname = nickname

    with self.connection as conn:
      self.player_dao.set(conn, player)

    self.client_notifier.send_notification([player_id], {
      'action': 'setNickname',
      'data': {
        'nickname': nickname,
        'playerId': player_id,
      },
    })

  def _is_valid_nickname(self, nickname):
    return (
      2 <= len(nickname) <= 20
      and nickname.upper != 'MR ELEVEN'
    )

  # Games

  @transaction_retry
  def create_game(self, player_id):
    """Creates a new game, and adds this player to it
    Transaction retry for if two players try to create the same unique ID.
    """
    with self.connection as conn:
      player_item = self.player_dao.get(conn, player_id)
      game_id = self.game_dao.create_unique_id(conn)

    game_item = GameItem(id=game_id, num_players=1, mr_eleven='', round_finished=True)
    turn_item = TurnItem(id=self.create_unique_id(), game_id=game_item.id, player_id=player_item.id, finished=False, outcome='')
    player_item.game_id = game_id
    player_item.win_counter = 0

    with self.connection as conn:
      self.game_dao.create(conn, game_item)
      self.turn_dao.create(conn, turn_item)
      self.player_dao.set(conn, player_item)

    self.client_notifier.send_notification([player_id], {
      'action': 'joinGame',
      'data': game_id,
    })

    self.send_game_state_update(game_id)
  
  def join_game(self, player_id, game_id):
    """Adds this player to an existing game.
    Transaction exception if trying to join a game that is deleted.
    """
    bad_message = {
      'action': 'joinGame',
      'error': f'Unable to join game: {game_id}',
    }
    try:
      with self.connection as conn:
        game_item = self.game_dao.get(conn, game_id)
        player_item = self.player_dao.get(conn, player_id)

      if not game_item:
        self.client_notifier.send_notification([player_id], bad_message)
        return 

      turn_item = TurnItem(id=self.create_unique_id(), game_id=game_item.id, player_id=player_item.id, finished=False, outcome='')
      game_item.num_players += 1
      player_item.game_id = game_id
      player_item.win_counter = 0

      with self.connection as conn:
        self.game_dao.set(conn, game_item)
        self.player_dao.set(conn, player_item)
        self.turn_dao.create(conn, turn_item)

    except ClientError as e:
      if e.response['Error']['Code'] == 'TransactionCanceledException':
        return self.client_notifier.send_notification([player_id], bad_message)
      else:
        raise e

    self.client_notifier.send_notification([player_id], {
      'action': 'joinGame',
      'data': game_id,
    })

    self.send_game_state_update(game_id)

  # Rounds

  # @transaction_retry
  def new_round(self, player_id):
    """The previous round is complete, clear the rolls.
    Transaction retry if updating turns that are deleted from a player leaving
    """
    with self.connection as conn:
      player_item = self.player_dao.get(conn, player_id)

    with self.connection as conn:
      turn_items = self.turn_dao.get_turns_with_game_id(conn, player_item.game_id)
      game_item = self.game_dao.get(conn, player_item.game_id)
      roll_items = self.roll_dao.get_rolls_with_game_id(conn, player_item.game_id)

    with self.connection as conn:

      game_item.round_finished = False
      self.game_dao.set(conn, game_item)

      for turn_item in turn_items:
        turn_item.outcome = game_logic.RollResult.NONE.value
        turn_item.finished = False
        self.turn_dao.set(conn, turn_item)

      for roll in roll_items:
        self.roll_dao.delete(conn, roll.id)
        
    self.send_game_state_update(game_item.id)

  def roll_dice(self, player_id):
    """Create a new roll for this player, and mark their turn as finished. If this is the last turns, calculate results for the round."""
    print('roll_dice()')

    with self.connection as conn:
      player_item = self.player_dao.get(conn, player_id)

    with self.connection as conn:
      game_item = self.game_dao.get(conn, player_item.game_id)
      player_items = self.player_dao.get_players_with_game_id(conn, player_item.game_id)
      turn_items = self.turn_dao.get_turns_with_game_id(conn, player_item.game_id)
      roll_items = self.roll_dao.get_rolls_with_game_id(conn, player_item.game_id)

    player_turn = [t for t in turn_items if t.player_id == player_id][0]  # only one turn per player right now
    player_turn.finished = True
    roll = game_logic.roll_dice(player_item.win_counter)
    roll_item = RollItem(id=self.create_unique_id(), turn_id=player_turn.id, game_id=game_item.id, dice=roll)
    roll_items.append(roll_item)

    with self.connection as conn:
      self.roll_dao.create(conn, roll_item)
      self.turn_dao.set(conn, player_turn)

    if not all([t.finished for t in turn_items]):
      self.send_game_state_update(game_item.id)
      return

    # Calculate turn results - chance of multiple lambda's trying to calculate turn results
    turn_player_map = {t.id: t.player_id for t in turn_items}
    player_turn_map = {t.player_id: t for t in turn_items}
    print(f'turn_player_map: {turn_player_map}')

    player_rolls = {turn_player_map[r.turn_id]: r.dice for r in roll_items}
    print(f'player_rolls: {player_rolls}')

    results, mr_eleven = game_logic.calculate_turn_results(player_rolls, game_item.mr_eleven)
    print(f'results: {results}')

    with self.connection as conn:

      game_item.mr_eleven = mr_eleven if mr_eleven is not None else ''
      game_item.round_finished = True
      self.game_dao.set(conn, game_item)

      for p in player_items:
        turn = player_turn_map[p.id]
        turn.outcome = results[p.id].value
        
        self.turn_dao.set(conn, turn)

        if results[p.id] == game_logic.RollResult.WINNER:
          p.win_counter += 1
        else:
          p.win_counter = 0

        self.player_dao.set(conn, p)

    self.send_game_state_update(game_item.id)

  # Notifications
  
  def send_game_state_update(self, game_id):
    print('send_game_state_update()')

    with self.connection as conn:
      game_item = self.game_dao.get(conn, game_id)
      player_items = self.player_dao.get_players_with_game_id(conn, game_id)
      turn_items = self.turn_dao.get_turns_with_game_id(conn, game_id)
      roll_items = self.roll_dao.get_rolls_with_game_id(conn, game_id)

    # Player info
    player_states = {
      p.id: {
        'id': p.id,
        'nickname': 'Mr Eleven' if p.id == game_item.mr_eleven else p.nickname,
        'turnFinished': False,
        'winCount': p.win_counter
      }
      for p in player_items
    }

    # Turn info
    for turn in turn_items:
      player_id = turn.player_id
      player_states[player_id]['turnFinished'] = turn.finished
      if game_item.round_finished:
        player_states[player_id]['rollResult'] = turn.outcome #if turn.outcome.get(TurnAttribute.OUTCOME.key, 'SIP_DRINK') # workaround for players that join end of round

      matching_rolls = [r for r in roll_items if r.turn_id == turn.id]
      if matching_rolls:
        roll = matching_rolls[0]
        values = game_logic.get_values(roll.dice)
        player_states[player_id]['rollTotal'] = sum(values)
        player_states[player_id]['diceValue'] = roll.dice
      
    # Send it
    message = {
      'action': 'gameState',
      'data': {
        'players': list(player_states.values()),
        'round': {'complete': game_item.round_finished},
      },
    }
    print(f'message: {message}')
    self.client_notifier.send_notification([p.id for p in player_items], message)
