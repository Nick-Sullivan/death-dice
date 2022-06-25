

import random
import string
import uuid
from botocore.exceptions import ClientError
from copy import deepcopy

import game_logic
from client_notifier import ClientNotifier
from dao.connection import ConnectionDao
from dao.game import GameDao
from db_wrapper import DatabaseReader, DatabaseWriter, transaction_fail_logs, transaction_retry
from model.game_items import ItemType, ConnectionItem, GameItem, GameState, PlayerItem, RollItem, lookup_item_class


class GameController:
  """Responsible for game logic and state change"""

  client_notifier = ClientNotifier()
  connection_dao = ConnectionDao()
  game_dao = GameDao()


  @staticmethod
  def create_unique_id():
    return str(uuid.uuid4())

  @staticmethod
  def create_unique_game_id():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

  # State

  def get_state(self, game_id):

    with DatabaseReader() as conn: # lazy loads, so create GameState object later 
      items = self.game_dao.get_items_with_game_id(conn, game_id)

    state = GameState(game=None, players=[], rolls=[])
    for item_json in items:
      print(f'item_json: {item_json}')
      cls = lookup_item_class(ItemType(item_json['item_type']['S']))
      item = cls.from_query(item_json)

      if cls == GameItem:
        state.game = item
      elif cls == PlayerItem:
        state.players.append(item)
      elif cls == RollItem:
        state.rolls.append(item)
    
    state.players = sorted(state.players, key=lambda x: x.created_on)
    state.rolls = sorted(state.rolls, key=lambda x: x.created_on)

    print(f'state: {state}')
    return state

  def save_state(self, conn, old_state, new_state):
    """Limited by a transaction of 25 items
    
    player leaves, causing recalculation:
      1 game + 3 player(leave and new winner) + N turns <= 25
      N <= 21

    new round:
      1 game + N turns + N*5 rolls <= 25
      N*6 <= 24
      N <= 4               
    """
    if old_state is None:
      old_state = GameState(game=None, players=[], rolls=[])
    if new_state is None:
      new_state = GameState(game=None, players=[], rolls=[])
      
    print(f'new_state: {new_state}')

    old_state_flat = old_state.flatten()
    new_state_flat = new_state.flatten()

    all_ids = {x.id for x in old_state_flat + new_state_flat}

    for id in all_ids:
      old = next((x for x in old_state_flat if x.id == id), None)
      new = next((x for x in new_state_flat if x.id == id), None)

      if old is None:
        self.game_dao.create(conn, new)
      elif new is None:
        self.game_dao.delete(conn, old)
      else:
        self.game_dao.set(conn, new)

  # Connecting

  def connect(self, connection_id):
    """Create a new connection object for a new browser session"""
    with DatabaseWriter() as conn:
      self.connection_dao.create(conn, ConnectionItem(id=connection_id))

  @transaction_retry
  def disconnect(self, connection_id):
    """Remove the player from the database, and any games/turns/rolls they are part of
    Transaction retry for if a player joins the game as we try to leave it.
    """
    with DatabaseReader() as conn:
      connection = self.connection_dao.get(conn, connection_id)

    if connection.game_id is None:
      with DatabaseWriter() as conn:
        self.connection_dao.delete(conn, connection_id)
        return

    state = self.get_state(connection.game_id)
    old_state = deepcopy(state)

    if len(state.players) <= 1:
      with DatabaseWriter() as conn:
        self.connection_dao.delete(conn, connection_id)
        self.save_state(conn, old_state, None)
        return
    
    state.players = [p for p in state.players if p.id != connection_id]
    state.rolls = [r for r in state.rolls if r.player_id != connection_id]

    is_last_roll = all([p.finished for p in state.players])
    if is_last_roll:
      state = self._calculate_turn_results(state)

    with DatabaseWriter() as conn:
      self.connection_dao.delete(conn, connection_id)
      self.save_state(conn, old_state, state)
      
    self.send_game_state_update(state)

  # Player

  def set_nickname(self, connection_id, nickname):
    """Sets a connections's name, as seen by other players"""

    if not self._is_valid_nickname(nickname):
      self.client_notifier.send_notification(
        [connection_id], 
        {'action': 'setNickname', 'error': 'Invalid nickname'}
      )
      return

    with DatabaseReader() as conn:
      connection = self.connection_dao.get(conn, connection_id)
      
    connection.nickname = nickname

    with DatabaseWriter() as conn:
      self.connection_dao.set(conn, connection)

    self.client_notifier.send_notification([connection_id], {
      'action': 'setNickname',
      'data': {
        'nickname': nickname,
        'playerId': connection_id,
      },
    })

  def _is_valid_nickname(self, nickname):
    return (
      2 <= len(nickname) <= 20
      and nickname.upper not in ['MR ELEVEN', 'MRELEVEN', 'MR 11', 'MR11'])

  # Games

  @transaction_retry
  def create_game(self, connection_id):
    """Creates a new game, and adds this player to it
    Transaction retry for if two players try to create the same unique ID.
    """    
    with DatabaseReader() as conn:
      connection = self.connection_dao.get(conn, connection_id)

    game_id = self.create_unique_game_id()

    state = GameState(
      game=GameItem(game_id=game_id, id=game_id, mr_eleven='', round_finished=True),
      players=[PlayerItem(game_id=game_id, id=connection_id, nickname=connection.nickname, win_counter=0, finished=False, outcome='')],
      rolls=[],
    )
    connection.game_id = game_id

    with DatabaseWriter() as conn:
      self.save_state(conn, None, state)
      self.connection_dao.set(conn, connection)

    self.client_notifier.send_notification([connection_id], {
      'action': 'joinGame',
      'data': game_id,
    })

    self.send_game_state_update(state)
  
  @transaction_retry
  def join_game(self, connection_id, game_id):
    """Adds this player to an existing game.
    Transaction exception if trying to join a game that is deleted.
    """
    bad_message = {
      'action': 'joinGame',
      'error': f'Unable to join game: {game_id}',
    }
    if len(game_id) != 4:
      return self.client_notifier.send_notification([connection_id], bad_message)

    try:
      state = self.get_state(game_id=game_id)
      old_state = deepcopy(state)

      if state.game.id is None:
        self.client_notifier.send_notification([connection_id], bad_message)
        return 

      with DatabaseReader() as conn:
        connection = self.connection_dao.get(conn, connection_id)

      connection.game_id = game_id
      state.players.append(PlayerItem(game_id=game_id, id=connection_id, nickname=connection.nickname, win_counter=0, finished=False, outcome=''))

      with DatabaseWriter() as conn:
        self.save_state(conn, old_state, state)
        self.connection_dao.set(conn, connection)

      self.client_notifier.send_notification([connection_id], {
        'action': 'joinGame',
        'data': game_id,
      })

      self.send_game_state_update(state)

    except ClientError as e:
      if e.response['Error']['Code'] == 'TransactionCanceledException':
        print(f'TransactionCanceledException')
        print(e.response)
        return self.client_notifier.send_notification([connection_id], bad_message)
      else:
        raise e

  # Rounds

  @transaction_retry
  def new_round(self, connection_id):
    """The previous round is complete, clear the rolls.
    Transaction retry if updating turns that are deleted from a player leaving
    """
    with DatabaseReader() as conn:
      connection = self.connection_dao.get(conn, connection_id)
    
    state = self.get_state(connection.game_id)
    old_state = deepcopy(state)

    state.game.round_finished = False

    for player in state.players:
      player.outcome = game_logic.RollResult.NONE.value
      player.finished = False

    state.rolls = []

    with DatabaseWriter() as conn:
      self.save_state(conn, old_state, state)
    
    self.send_game_state_update(state)

  @transaction_retry
  def roll_dice(self, connection_id):
    """Create a new roll for this player, and mark their turn as finished. If all players are finished, calculate results for the round.
    Transaction retry so players don't think they are both the second-to-last roll.
    """
    with DatabaseReader() as conn:
      connection = self.connection_dao.get(conn, connection_id)

    state = self.get_state(connection.game_id)
    old_state = deepcopy(state)

    player = next(p for p in state.players if p.id == connection_id)
    player_rolls = [r for r in state.rolls if r.player_id == connection_id]

    if not player_rolls:
      roll, finished = game_logic.initial_roll(player.win_counter, player.nickname)
    else:
      roll, finished = game_logic.extra_roll([game_logic.get_roll(r.dice) for r in player_rolls], player.nickname)

    player.finished = finished

    state.rolls.append(
      RollItem(game_id=state.game.id, id=self.create_unique_id(), player_id=player.id, dice=roll)
    )

    is_last_roll = all([p.finished for p in state.players])
    if is_last_roll:
      state = self._calculate_turn_results(state)
    
    with DatabaseWriter() as conn:
      self.save_state(conn, old_state, state)
    self.send_game_state_update(state)

  def _calculate_turn_results(self, state):

    player_rolls = {p.id: [] for p in state.players}
    for r in state.rolls:
      roll_obj = game_logic.get_roll(r.dice)
      player_rolls[r.player_id].append(roll_obj)

    results, mr_eleven, round_finished = game_logic.calculate_turn_results(player_rolls, state.game.mr_eleven)

    state.game.mr_eleven = mr_eleven if mr_eleven is not None else ''
    state.game.round_finished = round_finished

    if not round_finished:
      for player in state.players:
        player.outcome = results[player.id].value
        player.finished = False
      return state
    
    for player in state.players:
      player.outcome = results[player.id].value

      if results[player.id] == game_logic.RollResult.WINNER:
        player.win_counter += 1
      else:
        player.win_counter = 0

    return state

  # Notifications
  
  def send_game_state_update(self, state):

    # Player and turn info
    player_output = []
    for player in state.players:
      entry = {
        'id': player.id,
        'nickname': 'Mr Eleven' if player.id == state.game.mr_eleven else player.nickname,
        'turnFinished': player.finished,
        'winCount': player.win_counter,
        'rollResult': player.outcome,
      }

      # Combine dice rolls into one
      rolls = [r for r in state.rolls if r.player_id == player.id]
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
    print(f'game_state_update: {message}')
    self.client_notifier.send_notification([p.id for p in state.players], message)
