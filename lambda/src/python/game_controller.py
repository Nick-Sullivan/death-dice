

import uuid
from botocore.exceptions import ClientError
from copy import deepcopy
from dataclasses import dataclass
from typing import List

import game_logic
from client_notifier import ClientNotifier
from connection import DatabaseReader, DatabaseWriter, transaction_fail_logs, transaction_retry
from dao.game_dao import GameDao, GameItem
from dao.player_dao import PlayerDao, PlayerItem
from dao.roll_dao import RollDao, RollItem
from dao.turn_dao import TurnDao, TurnItem


@dataclass
class GameState:
  game : GameItem
  players : List[PlayerItem]
  turns : List[TurnItem]
  rolls: List[RollItem]


class GameController:
  """Responsible for game logic and state change"""

  client_notifier = ClientNotifier()
  player_dao = PlayerDao()
  game_dao = GameDao()
  roll_dao = RollDao()
  turn_dao = TurnDao()
  db_writer = DatabaseWriter()
  db_reader = DatabaseReader()

  @staticmethod
  def create_unique_id():
    return str(uuid.uuid4())

  def get_state(self, player_id=None, game_id=None):
    """Gets the game state.
    Important for it to read the game state first, because the optimistic locking uses that version.
    """
    assert (player_id is None) ^ (game_id is None)

    if player_id is not None:
      with self.db_reader as conn:
        player = self.player_dao.get(conn, player_id)

      game_id = player.game_id

      if not game_id:
        state = GameState(game=None, players=[player], turns=[], rolls=[])
        print(f'state: {state}')
        return state

    with self.db_reader as conn:
      state = GameState(
        game=self.game_dao.get(conn, game_id),
        players=self.player_dao.get_items_with_game_id(conn, game_id),
        turns=self.turn_dao.get_items_with_game_id(conn, game_id),
        rolls=self.roll_dao.get_items_with_game_id(conn, game_id)
      )

    print(f'state: {state}')
    return state

  def save_state(self, old_state, new_state):
    """Limited by a transaction of 25 items
    
    player leaves, causing recalculation:
      1 game + 3 player(leave and new winner) + N turns <= 25
      N <= 21

    new round:
      1 game + N turns + N*5 rolls <= 25
      N*6 <= 24
      N <= 4               
    """
    print(f'old_state: {old_state}')
    print(f'new_state: {new_state}')

    with self.db_writer as conn:
      self._save_state_game(conn, old_state.game, new_state.game)
      self._save_state_players(conn, old_state.players, new_state.players)
      self._save_state_turns(conn, old_state.turns, new_state.turns)
      self._save_state_rolls(conn, old_state.rolls, new_state.rolls)

  def _save_state_game(self, conn, old_game, new_game):
    """Updates the game state.
    Updates the version even if the game state is unchanged
    e.g. player A and player B roll at the same time - both can update the database concurrently, but they will send inconsistent 
    messages to the front end.
    """
    if old_game is None and new_game is None:
      return
    elif old_game is None:
      self.game_dao.create(conn, new_game)
    elif new_game is None:
      self.game_dao.delete(conn, old_game.id)
    else:
      self.game_dao.set(conn, new_game)
    
  def _save_state_players(self, conn, olds, news):
    assert all(isinstance(x, PlayerItem) for x in olds + news)

    all_ids = {x.id for x in olds + news}
    for id in all_ids:
      old = next((x for x in olds if x.id == id), None)
      new = next((x for x in news if x.id == id), None)

      # a new player is created before being part of a game state - so we don't create it here
      if new is None:
        self.player_dao.delete(conn, old.id)
      elif new != old:
        self.player_dao.set(conn, new)

  def _save_state_turns(self, conn, olds, news):
    assert all(isinstance(x, TurnItem) for x in olds + news)

    all_ids = {x.id for x in olds + news}
    for id in all_ids:
      old = next((x for x in olds if x.id == id), None)
      new = next((x for x in news if x.id == id), None)

      if old is None:
        self.turn_dao.create(conn, new)
      elif new is None:
        self.turn_dao.delete(conn, old.id)
      elif new != old:
        self.turn_dao.set(conn, new)

  def _save_state_rolls(self, conn, olds, news):
    assert all(isinstance(x, RollItem) for x in olds + news)

    all_ids = {x.id for x in olds + news}
    for id in all_ids:
      old = next((x for x in olds if x.id == id), None)
      new = next((x for x in news if x.id == id), None)

      if old is None:
        self.roll_dao.create(conn, new)
      elif new is None:
        self.roll_dao.delete(conn, old.id)
      elif new != old:
        self.roll_dao.set(conn, new)

  # Player

  def create_player(self, player_id):
    """Create a new player object for a new browser session"""
    with self.db_writer as conn:
      self.player_dao.create(conn, PlayerItem(id=player_id, win_counter=0, ))

  @transaction_retry
  def delete_player(self, player_id):
    """Remove the player from the database, and any games/turns/rolls they are part of
    Transaction retry for if a player joins the game as we try to leave it.
    """
    state = self.get_state(player_id=player_id)
    old_state = deepcopy(state)

    if state.game is None:
      with self.db_writer as conn:
        self.player_dao.delete(conn, player_id)
      return

    if state.game.num_players == 1:
      self.save_state(old_state, GameState(game=None, players=[], turns=[], rolls=[]))
      return
    
    state.game.num_players -= 1
    state.players = [p for p in state.players if p.id != player_id]
    state.turns = [t for t in state.turns if t.player_id != player_id]
    remaining_turn_ids = [t.id for t in state.turns]
    state.rolls = [r for r in state.rolls if r.turn_id in remaining_turn_ids]

    self.save_state(old_state, state)
    self.send_game_state_update(state)

  def set_nickname(self, player_id, nickname):
    """Sets a player's name, as seen by other players"""

    if not self._is_valid_nickname(nickname):
      self.client_notifier.send_notification(
        [player_id], 
        {'action': 'setNickname', 'error': 'Invalid nickname'}
      )
      return

    with self.db_reader as conn:
      player = self.player_dao.get(conn, player_id)
      
    player.nickname = nickname

    with self.db_writer as conn:
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
      and nickname.upper != 'MR ELEVEN')

  # Games

  @transaction_retry
  def create_game(self, player_id):
    """Creates a new game, and adds this player to it
    Transaction retry for if two players try to create the same unique ID.
    """    
    state = self.get_state(player_id=player_id)
    old_state = deepcopy(state)

    game_id = self.game_dao.create_unique_id(None)
    state.game = GameItem(id=game_id, num_players=1, mr_eleven='', round_finished=True)

    turn_item = TurnItem(id=self.create_unique_id(), game_id=game_id, player_id=player_id, finished=False, outcome='')
    state.turns.append(turn_item)

    player = next(p for p in state.players if p.id == player_id)
    player.game_id = game_id
    player.win_counter = 0

    self.save_state(old_state, state)

    self.client_notifier.send_notification([player_id], {
      'action': 'joinGame',
      'data': game_id,
    })

    self.send_game_state_update(state)
  
  @transaction_retry
  def join_game(self, player_id, game_id):
    """Adds this player to an existing game.
    Transaction exception if trying to join a game that is deleted.
    """
    bad_message = {
      'action': 'joinGame',
      'error': f'Unable to join game: {game_id}',
    }
    try:
      state = self.get_state(game_id=game_id)
      old_state = deepcopy(state)

      if state.game.id is None:
        self.client_notifier.send_notification([player_id], bad_message)
        return 

      with self.db_reader as conn:
        player_item = self.player_dao.get(conn, player_id)

      state.game.num_players += 1

      player_item.game_id = game_id
      player_item.win_counter = 0
      state.players.append(player_item)

      turn_item = TurnItem(id=self.create_unique_id(), game_id=game_id, player_id=player_id, finished=False, outcome='')
      state.turns.append(turn_item)

      self.save_state(old_state, state)
      self.client_notifier.send_notification([player_id], {
        'action': 'joinGame',
        'data': game_id,
      })

      self.send_game_state_update(state)

    except ClientError as e:
      if e.response['Error']['Code'] == 'TransactionCanceledException':
        print(f'TransactionCanceledException')
        print(e.response)
        return self.client_notifier.send_notification([player_id], bad_message)
      else:
        raise e

  # Rounds

  @transaction_retry
  def new_round(self, player_id):
    """The previous round is complete, clear the rolls.
    Transaction retry if updating turns that are deleted from a player leaving
    """
    state = self.get_state(player_id=player_id)
    old_state = deepcopy(state)

    state.game.round_finished = False

    for turn in state.turns:
      turn.outcome = game_logic.RollResult.NONE.value
      turn.finished = False

    state.rolls = []

    self.save_state(old_state, state)
    self.send_game_state_update(state)

  @transaction_retry
  def roll_dice(self, player_id):
    """Create a new roll for this player, and mark their turn as finished. If this is the last turns, calculate results for the round.
    Transaction retry so players don't think they are both the second-to-last roll.
    """
    print('roll_dice()')

    state = self.get_state(player_id=player_id)
    old_state = deepcopy(state)

    player = next(p for p in state.players if p.id == player_id)
    player_turn = [t for t in state.turns if t.player_id == player_id][0]  # only one turn per player right now
    player_rolls = [r for r in state.rolls if r.turn_id == player_turn.id]

    if not player_rolls:
      roll, finished = game_logic.initial_roll(player.win_counter)
    else:
      roll, finished = game_logic.extra_roll([game_logic.get_roll(r.dice) for r in player_rolls])

    player_turn.finished = finished

    state.rolls.append(
      RollItem(id=self.create_unique_id(), turn_id=player_turn.id, game_id=state.game.id, dice=roll)
    )

    is_last_roll = all([t.finished for t in state.turns])
    if is_last_roll:
      state = self._calculate_turn_results(state)
      
    self.save_state(old_state, state)
    self.send_game_state_update(state)

  def _calculate_turn_results(self, state):
    turn_rolls = {t.id: [] for t in state.turns}
    for r in state.rolls:
      turn_rolls[r.turn_id].append(r)

    player_rolls = {t.player_id: turn_rolls[t.id] for t in state.turns} # assumes 1 turn per player
    player_rolls = {p_id: [game_logic.get_roll(r.dice) for r in rolls] for p_id, rolls in player_rolls.items()}

    print(f'player_rolls: {player_rolls}')

    results, mr_eleven = game_logic.calculate_turn_results(player_rolls, state.game.mr_eleven)
    print(f'results: {results}')

    state.game.mr_eleven = mr_eleven if mr_eleven is not None else ''
    state.game.round_finished = True

    for turn in state.turns:
      player = next(p for p in state.players if p.id == turn.player_id)
      turn.outcome = results[player.id].value

      if results[player.id] == game_logic.RollResult.WINNER:
        player.win_counter += 1
      else:
        player.win_counter = 0

    return state

  # Notifications
  
  def send_game_state_update(self, state):
    print('send_game_state_update()')

    # Player and turn info
    player_output = []
    for turn in state.turns:
      player = next(p for p in state.players if p.id == turn.player_id)
      entry = {
        'id': player.id,
        'nickname': 'Mr Eleven' if player.id == state.game.mr_eleven else player.nickname,
        'turnFinished': turn.finished,
        'winCount': player.win_counter
      }
      if state.game.round_finished:
        entry['rollResult'] = turn.outcome

      # Combine dice rolls into one
      rolls = [r for r in state.rolls if r.turn_id == turn.id]
      if rolls:
        dice_rolls = [game_logic.get_roll(r.dice) for r in rolls]

        dice_roll = dice_rolls[0]
        for dr in dice_rolls[1:]:
          dice_roll += dr

        entry['rollTotal'] = sum(dice_roll.values)
        entry['diceValue'] = dice_roll.to_json()

      player_output.append(entry)

    # Order by player joined time TODO
    player_output.sort(key=lambda x: x['id'])
      
    # Send it
    message = {
      'action': 'gameState',
      'data': {
        'players': player_output,
        'round': {'complete': state.game.round_finished},
      },
    }
    print(f'message: {message}')
    self.client_notifier.send_notification([p.id for p in state.players], message)
