

from client_notifier import ClientNotifier
from game_dao import GameDao, GameAttribute
from player_dao import PlayerDao, PlayerAttribute
from roll_dao import RollDao, RollAttribute
from turn_dao import TurnDao, TurnAttribute
from connection import DatabaseConnection
import game_logic
import uuid


class GameController:
  """Responsible for game logic and state change"""
  
  client_notifier = ClientNotifier()
  player_dao = PlayerDao()
  game_dao = GameDao()
  roll_dao = RollDao()
  turn_dao = TurnDao()
  connection = DatabaseConnection()

  def create_unique_id(self):
    return str(uuid.uuid4())

  # Players

  def create_player(self, player_id):
    """Create a new connection, with no other information"""
    with self.connection as conn:
      self.player_dao.create(conn, player_id)

  def delete_player(self, player_id):
    """Remove the player from the database, and any games/turns/rolls they are part of"""

    with self.connection as conn:

      self.player_dao.delete(conn, player_id)

      game_id = self.player_dao.get_attribute(conn, player_id, PlayerAttribute.GAME_ID)
      
      for turn in self.turn_dao.get_turns_with_player_id(conn, player_id):
        turn_id = turn[TurnAttribute.ID.key]

        self.turn_dao.delete(conn, turn_id)

        for roll in self.roll_dao.get_rolls_with_turn_id(conn, turn_id):
          self.roll_dao.delete(conn, roll[RollAttribute.ID.key])

      if not game_id:
        return

      if len(self.player_dao.get_players_with_game_id(conn, game_id)) == 1:
        self.game_dao.delete(conn, game_id)
        return

    self.send_game_state_update(game_id)

  def set_nickname(self, player_id, nickname):
    """Sets a player's name, as seen by other players"""

    if not self._is_valid_nickname(nickname):
      self.client_notifier.send_notification([player_id], {
        'action': 'setNickname',
        'error': 'Invalid nickname',
      })
      return

    with self.connection as conn:
      self.player_dao.set_attributes(conn, player_id, {PlayerAttribute.NICKNAME: nickname})

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

  def get_game_id(self, player_id):
    with self.connection as conn:
      return self.player_dao.get_attribute(conn, player_id, PlayerAttribute.GAME_ID)

  # Games

  def create_game(self, player_id):
    """Creates a new game, and adds this player to it"""
    with self.connection as conn:
      game_id = self.game_dao.create_unique_id(conn)

      self.game_dao.create(conn, game_id)

      self._join_game(conn, player_id, game_id)

    self.client_notifier.send_notification([player_id], {
      'action': 'joinGame',
      'data': game_id,
    })

    self.send_game_state_update(game_id)
  
  def join_game(self, player_id, game_id):
    """Adds this player to an existing game"""

    with self.connection as conn:
      if not self.game_dao.exists(conn, game_id):
        self.client_notifier.send_notification([player_id], {
          'action': 'joinGame',
          'error': f'Game ID does not exist: {game_id}',
        })
        return

      self._join_game(conn, player_id, game_id)

    self.client_notifier.send_notification([player_id], {
      'action': 'joinGame',
      'data': game_id,
    })

    self.send_game_state_update(game_id)

  def _join_game(self, conn, player_id, game_id):
    """Common logic for both creating or joining a game"""
    self.player_dao.set_attributes(conn, player_id, {PlayerAttribute.GAME_ID: game_id, PlayerAttribute.WIN_COUNTER: '0'})
    self.turn_dao.create(conn, self.create_unique_id(), game_id, player_id)

  # Rounds

  def new_round(self, game_id):
    """The previous round is complete, clear the rolls"""
    print('new_round()')

    with self.connection as conn:

      for turn in self.turn_dao.get_turns_with_game_id(conn, game_id):
        turn_id = turn[TurnAttribute.ID.key]

        for roll in self.roll_dao.get_rolls_with_turn_id(conn, turn_id):
          self.roll_dao.delete(conn, roll[RollAttribute.ID.key])

        self.turn_dao.set_attributes(conn, turn_id, {
          TurnAttribute.OUTCOME: game_logic.RollResult.NONE.value, 
          TurnAttribute.FINISHED: False
        })
      
    self.send_game_state_update(game_id)

  def roll_dice(self, player_id):
    """Create a new roll for this player, and mark their turn as finished. If this is the last turns, calculate results for the round."""
    print('roll_dice()')

    with self.connection as conn:
      player = self.player_dao.get(conn, player_id)
      game_id = player[PlayerAttribute.GAME_ID.key]

      turn = self.turn_dao.get_turns_with_player_id(conn, player_id)[0]  # right now theres only one turn per player
      turn_id = turn[TurnAttribute.ID.key]

      roll = game_logic.roll_dice(player[PlayerAttribute.WIN_COUNTER.key])

      self.roll_dao.create(conn, self.create_unique_id(), turn_id, roll)
      self.turn_dao.set_attributes(conn, turn_id, {TurnAttribute.FINISHED: True})

    # TODO - same transaction as the roll
    if self._is_round_complete(game_id):
      self.calculate_turn_results(game_id)

    self.send_game_state_update(game_id)

  def _count_unfinished_turns(self, conn, game_id):
    turns = self.turn_dao.get_turns_with_game_id(conn, game_id)
    return sum([turn[TurnAttribute.FINISHED.key] for turn in turns])

  def _is_round_complete(self, game_id):
    """Round is complete if all players turns are complete"""
    print('_is_round_complete()')
    with self.connection as connection:
      for turn in self.turn_dao.get_turns_with_game_id(connection, game_id):
        print(f'turn: {turn}')
        if not turn[TurnAttribute.FINISHED.key]:
          print(False)
          return False
      print(True)
      return True

  def calculate_turn_results(self, game_id):
    print('calculate_turn_results()')
    with self.connection as connection:

      player_rolls = {}
      player_turn_map = {}

      for turn in self.turn_dao.get_turns_with_game_id(connection, game_id):
        print(f'turn: {turn}')
        player_id = turn[TurnAttribute.PLAYER_ID.key]
        turn_id = turn[TurnAttribute.ID.key]
        player_turn_map[player_id] = turn_id

        roll = self.roll_dao.get_rolls_with_turn_id(connection, turn_id)[0]
        print(f'roll: {roll}')
        player_rolls[player_id] = roll[RollAttribute.DICE.key]

      mr_eleven = self.game_dao.get_attribute(connection, game_id, GameAttribute.MR_ELEVEN)

      results, new_mr_eleven = game_logic.calculate_turn_results(player_rolls, mr_eleven)
      print(f'results: {results}')

      for player_id, result in results.items():
        self.turn_dao.set_attributes(connection, player_turn_map[player_id], {TurnAttribute.OUTCOME: result.value})

        if result == game_logic.RollResult.WINNER:
          win_counter = self.player_dao.get_attribute(connection, player_id, PlayerAttribute.WIN_COUNTER)
          self.player_dao.set_attributes(connection, player_id, {PlayerAttribute.WIN_COUNTER: str(win_counter + 1)})
        else:
          self.player_dao.set_attributes(connection, player_id, {PlayerAttribute.WIN_COUNTER: '0'})

      self.game_dao.set_attributes(connection, game_id, {GameAttribute.MR_ELEVEN: new_mr_eleven if new_mr_eleven is not None else ''})

  # Notifications
  
  def send_game_state_update(self, game_id):
    print('send_game_state_update()')

    # Player info
    with self.connection as connection:
      players = self.player_dao.get_players_with_game_id(connection, game_id)
      print(f'players: {players}')
      mr_eleven = self.game_dao.get_attribute(connection, game_id, GameAttribute.MR_ELEVEN)

      player_states = {
        p[PlayerAttribute.ID.key]: {
          'id': p[PlayerAttribute.ID.key],
          'nickname': 'Mr Eleven' if p[PlayerAttribute.ID.key] == mr_eleven else p[PlayerAttribute.NICKNAME.key],
          'turnFinished': False,
          'winCount': p[PlayerAttribute.WIN_COUNTER.key]
        }
        for p in players
      }

    # Round info
    is_round_complete = self._is_round_complete(game_id)
    round_state = {
      'complete': is_round_complete
    }

    with self.connection as connection:
      # Turn info
      for turn in self.turn_dao.get_turns_with_game_id(connection, game_id):
        print(f'turn: {turn}')
        player_id = turn[TurnAttribute.PLAYER_ID.key]
        player_states[player_id]['turnFinished'] = turn[TurnAttribute.FINISHED.key]
        if is_round_complete:
          player_states[player_id]['rollResult'] = turn[TurnAttribute.OUTCOME.key]

        rolls = self.roll_dao.get_rolls_with_turn_id(connection, turn[TurnAttribute.ID.key])
        if rolls:
          roll = rolls[0]
          print(f'roll: {roll}')
          values = game_logic.get_values(roll[RollAttribute.DICE.key])
          print(f'values: {values}')
          player_states[player_id]['rollTotal'] = sum(values)
          player_states[player_id]['diceValue'] = roll[RollAttribute.DICE.key]
        
    # Send it
    message = {
      'action': 'gameState',
      'data': {
        'players': list(player_states.values()),
        'round': round_state,
      },
    }
    print(f'message: {message}')
    self.client_notifier.send_notification([p[PlayerAttribute.ID.key] for p in players], message)

  # def send_chat(self, player_id, game_id, message):
  #   self.client_notifier.send_notification(
  #     self.get_player_ids_in_game(game_id),
  #     {
  #       'action': 'sendMessage',
  #       'author': self.player_dao.get_attribute(player_id, PlayerAttribute.NICKNAME),
  #       'data': message,
  #     }
  #   )