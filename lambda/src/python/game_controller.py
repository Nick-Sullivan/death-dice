

from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List
import uuid
from botocore.exceptions import ClientError

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
  players : Dict[str, PlayerItem]
  turns : Dict[str, TurnItem]
  rolls: Dict[str, RollItem]


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
    assert (player_id is None) ^ (game_id is None)

    if player_id is not None:
      with self.db_reader as conn:
        player = self.player_dao.get(conn, player_id)

      game_id = player.game_id

      if not game_id:
        state = GameState(
          game=None,
          players={player.id: player},
          turns={},
          rolls={},
        )
        print(f'state: {state}')
        return state

    with self.db_reader as conn:
      game = self.game_dao.get(conn, game_id)
      players = self.player_dao.get_players_with_game_id(conn, game_id)
      turns = self.turn_dao.get_turns_with_game_id(conn, game_id)
      rolls = self.roll_dao.get_rolls_with_game_id(conn, game_id)

    state = GameState(
      game=game,
      players={p.id: p for p in players},
      turns={t.id: t for t in turns},
      rolls={r.id: r for r in rolls},
    )
    print(f'state: {state}')
    return state

  def save_state(self, old_state, new_state):
    print(f'old_state: {old_state}')
    print(f'new_state: {new_state}')

    with self.db_writer as conn:

      if old_state.game is None and new_state.game is None:
        pass
      elif old_state.game is None:
        self.game_dao.create(conn, new_state.game)
      elif new_state.game is None:
        self.game_dao.delete(conn, old_state.game.id)
      elif old_state.game != new_state.game:
        self.game_dao.set(conn, new_state.game)

      all_player_ids = set(old_state.players) | set(new_state.players)
      players_combined = [(old_state.players.get(i), new_state.players.get(i)) for i in all_player_ids]
      print(f'players_combined: {players_combined}')
      for old, new in players_combined:
        # if old is None:
        #   self.player_dao.create(conn, new)
        if new is None:
          self.player_dao.delete(conn, old.id)
        elif new != old:
          self.player_dao.set(conn, new)

      all_turn_ids = set(old_state.turns) | set(new_state.turns)
      turns_combined = [(old_state.turns.get(i), new_state.turns.get(i)) for i in all_turn_ids]
      print(f'turns_combined: {turns_combined}')
      for old, new in turns_combined:
        if old is None:
          self.turn_dao.create(conn, new)
        elif new is None:
          self.turn_dao.delete(conn, old.id)
        elif new != old:
          self.turn_dao.set(conn, new)

      all_roll_ids = set(old_state.rolls) | set(new_state.rolls)
      rolls_combined = [(old_state.rolls.get(i), new_state.rolls.get(i)) for i in all_roll_ids]
      print(f'rolls_combined: {rolls_combined}')
      for old, new in rolls_combined:
        if old is None:
          self.roll_dao.create(conn, new)
        elif new is None:
          self.roll_dao.delete(conn, old.id)
        elif new != old:
          self.roll_dao.set(conn, new)

  def create_player(self, player_id):
    """Create a new player object for a new browser session"""
    with self.db_writer as conn:
      self.player_dao.create(conn, PlayerItem(id=player_id, win_counter=0))

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
      state.game = None
      state.players = {}
      state.turns = {}
      state.rolls = {}
      self.save_state(old_state, state)
      return
    
    state.game.version += 1
    state.game.num_players -= 1
    state.players.pop(player_id)
    turns_to_remove = [t.id for t in state.turns.values() if t.player_id == player_id]
    rolls_to_remove = [r.id for r in state.rolls.values() if r.turn_id in turns_to_remove]
    _ = [state.turns.pop(t_id) for t_id in turns_to_remove]
    _ = [state.rolls.pop(r_id) for r_id in rolls_to_remove]

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
      and nickname.upper != 'MR ELEVEN'
    )

  # Games

  @transaction_retry
  def create_game(self, player_id):
    """Creates a new game, and adds this player to it
    Transaction retry for if two players try to create the same unique ID.
    """    
    state = self.get_state(player_id=player_id)
    old_state = deepcopy(state)

    game_id = self.game_dao.create_unique_id(None)
    state.game = GameItem(id=game_id, num_players=1, mr_eleven='', round_finished=True, version=0)
    turn_item = TurnItem(id=self.create_unique_id(), game_id=game_id, player_id=player_id, finished=False, outcome='')
    state.turns[turn_item.id] = turn_item
    state.players[player_id].game_id = game_id
    state.players[player_id].win_counter = 0

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

      turn_item = TurnItem(id=self.create_unique_id(), game_id=game_id, player_id=player_id, finished=False, outcome='')
      state.game.num_players += 1
      state.game.version += 1
      player_item.game_id = game_id
      player_item.win_counter = 0
      state.players[player_id] = player_item
      state.turns[turn_item.id] = turn_item

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

    state.game.version += 1
    state.game.round_finished = False

    for turn in state.turns.values():
      turn.outcome = game_logic.RollResult.NONE.value
      turn.finished = False

    state.rolls = {}

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

    player_turn = [t for t in state.turns.values() if t.player_id == player_id][0]  # only one turn per player right now
    player_turn.finished = True
    roll = game_logic.roll_dice(state.players[player_id].win_counter)
    roll_item = RollItem(id=self.create_unique_id(), turn_id=player_turn.id, game_id=state.game.id, dice=roll)
    state.rolls[roll_item.id] = roll_item
    state.game.version += 1

    is_last_roll = all([t.finished for t in state.turns.values()])
    if not is_last_roll:
      self.save_state(old_state, state)
      self.send_game_state_update(state)
      return

    # Calculate turn results
    turn_player_map = {t.id: t.player_id for t in state.turns.values()}
    player_turn_map = {t.player_id: t for t in state.turns.values()}
    print(f'turn_player_map: {turn_player_map}')

    player_rolls = {turn_player_map[r.turn_id]: r.dice for r in state.rolls.values()}
    print(f'player_rolls: {player_rolls}')

    results, mr_eleven = game_logic.calculate_turn_results(player_rolls, state.game.mr_eleven)
    print(f'results: {results}')

    state.game.mr_eleven = mr_eleven if mr_eleven is not None else ''
    state.game.round_finished = True
    for p in state.players.values():
      turn = player_turn_map[p.id]
      turn.outcome = results[p.id].value

      if results[p.id] == game_logic.RollResult.WINNER:
        p.win_counter += 1
      else:
        p.win_counter = 0

    self.save_state(old_state, state)
    self.send_game_state_update(state)

  # Notifications
  
  def send_game_state_update(self, state):
    print('send_game_state_update()')

    # Player info
    player_states = {
      p.id: {
        'id': p.id,
        'nickname': 'Mr Eleven' if p.id == state.game.mr_eleven else p.nickname,
        'turnFinished': False,
        'winCount': p.win_counter
      }
      for p in state.players.values()
    }

    # Turn info
    for turn in state.turns.values():
      player_id = turn.player_id
      player_states[player_id]['turnFinished'] = turn.finished
      if state.game.round_finished:
        player_states[player_id]['rollResult'] = turn.outcome #if turn.outcome.get(TurnAttribute.OUTCOME.key, 'SIP_DRINK') # workaround for players that join end of round

      matching_rolls = [r for r in state.rolls.values() if r.turn_id == turn.id]
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
        'round': {'complete': state.game.round_finished},
      },
    }
    print(f'message: {message}')
    self.client_notifier.send_notification(list(state.players), message)
