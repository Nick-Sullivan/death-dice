

from client_notifier import ClientNotifier
from game_dao import GameDao, GameAttribute
from player_dao import PlayerDao, PlayerAttribute
from roll_dao import RollDao, RollAttribute
from turn_dao import TurnDao, TurnAttribute
import game_logic
import uuid


class GameController:
  """Responsible for game logic and state change"""
  
  client_notifier = ClientNotifier()
  player_dao = PlayerDao()
  game_dao = GameDao()
  roll_dao = RollDao()
  turn_dao = TurnDao()

  def create_unique_id(self):
    return str(uuid.uuid4())

  # Players

  def create_player(self, player_id):
    self.player_dao.create(player_id)

  def delete_player(self, player_id):
    """Remove the player from the database, and any games they are part of"""
    game_id = self.player_dao.get_attribute(player_id, PlayerAttribute.GAME_ID)

    self.player_dao.delete(player_id)

    if not game_id:
      return

    for turn in self.turn_dao.get_turns_with_player_id(player_id):
      print(f'turn: {turn}')
      turn_id = turn[TurnAttribute.ID.value]
      for roll in self.roll_dao.get_rolls_with_turn_id(turn_id):
        self.roll_dao.delete(roll[RollAttribute.ID.value])
      self.turn_dao.delete(turn_id)

    if self.player_dao.get_players_with_game_id(game_id):
      self.send_game_state_update(game_id)
    else:
      self.game_dao.delete(game_id)

  def set_nickname(self, player_id, nickname):
    self.player_dao.set_attribute(player_id, PlayerAttribute.NICKNAME, nickname)

    message = {
      'action': 'setNickname',
      'data': {
        'nickname': nickname,
        'playerId': player_id,
      },
    }
    self.client_notifier.send_notification([player_id], message)

  def get_game_id(self, player_id):
    return self.player_dao.get_attribute(player_id, PlayerAttribute.GAME_ID)

  # Games

  def create_game(self, player_id):
    """Creates a new game, and adds this player to it"""
    game_id = self.game_dao.create_unique_id()

    self.game_dao.create(game_id)

    self.join_game(player_id, game_id)

    return game_id
  
  def join_game(self, player_id, game_id):
    if not self.game_dao.game_exists(game_id):
      message = {
        'action': 'joinGame',
        'error': f'Game ID does not exist: {game_id}',
      }
      self.client_notifier.send_notification([player_id], message)
      return

    self.player_dao.set_attribute(player_id, PlayerAttribute.GAME_ID, game_id)
    self.player_dao.set_attribute(player_id, PlayerAttribute.WIN_COUNTER, 0)
    self.turn_dao.create(self.create_unique_id(), game_id, player_id)

    message = {
      'action': 'joinGame',
      'data': game_id,
    }
    self.client_notifier.send_notification([player_id], message)

    self.send_game_state_update(game_id)

  # Rounds

  def new_round(self, game_id):
    print('new_round()')
    for turn in self.turn_dao.get_turns_with_game_id(game_id):
      print(f'turn: {turn}')
      turn_id = turn[TurnAttribute.ID.value]

      for roll in self.roll_dao.get_rolls_with_turn_id(turn_id):
        print(f'roll: {roll}')
        roll_id = roll[RollAttribute.ID.value]
        self.roll_dao.delete(roll_id)

      self.turn_dao.set_attribute(turn_id, TurnAttribute.OUTCOME, game_logic.RollResult.NONE.value)
      self.turn_dao.set_attribute(turn_id, TurnAttribute.FINISHED, False)
      
    self.send_game_state_update(game_id)

  def roll_dice(self, player_id):
    print('roll_dice()')

    player = self.player_dao.get(player_id)
    print(f'player: {player}')
    game_id = player[PlayerAttribute.GAME_ID.value]

    turn = self.turn_dao.get_turns_with_player_id(player_id)[0]
    print(f'turn: {turn}')
    turn_id = turn[TurnAttribute.ID.value]

    roll = game_logic.roll_dice(player[PlayerAttribute.WIN_COUNTER.value])
    print(f'roll: {roll}')

    self.roll_dao.create(self.create_unique_id(), turn_id, roll)
    self.turn_dao.set_attribute(turn_id, TurnAttribute.FINISHED, True)

    if self._is_round_complete(game_id):
      self.calculate_turn_results(game_id)

    self.send_game_state_update(game_id)

  def _is_round_complete(self, game_id):
    """Round is complete if all players turns are complete"""
    print('_is_round_complete()')
    for turn in self.turn_dao.get_turns_with_game_id(game_id):
      print(f'turn: {turn}')
      if not turn[TurnAttribute.FINISHED.value]:
        print(False)
        return False
    print(True)
    return True

  def calculate_turn_results(self, game_id):
    print('calculate_turn_results()')
    player_rolls = {}
    player_turn_map = {}

    for turn in self.turn_dao.get_turns_with_game_id(game_id):
      print(f'turn: {turn}')
      player_id = turn[TurnAttribute.PLAYER_ID.value]
      turn_id = turn[TurnAttribute.ID.value]
      player_turn_map[player_id] = turn_id

      roll = self.roll_dao.get_rolls_with_turn_id(turn_id)[0]
      print(f'roll: {roll}')
      player_rolls[player_id] = roll[RollAttribute.DICE.value]

    mr_eleven = self.game_dao.get_attribute(game_id, GameAttribute.MR_ELEVEN)

    results, new_mr_eleven = game_logic.calculate_turn_results(player_rolls, mr_eleven)
    print(f'results: {results}')

    for player_id, result in results.items():
      self.turn_dao.set_attribute(player_turn_map[player_id], TurnAttribute.OUTCOME, result.value)

      if result == game_logic.RollResult.WINNER:
        win_counter = self.player_dao.get_attribute(player_id, PlayerAttribute.WIN_COUNTER)
        self.player_dao.set_attribute(player_id, PlayerAttribute.WIN_COUNTER, win_counter + 1)
      else:
        self.player_dao.set_attribute(player_id, PlayerAttribute.WIN_COUNTER, 0)

    self.game_dao.set_attribute(game_id, GameAttribute.MR_ELEVEN, new_mr_eleven)

  # Notifications
  
  def send_game_state_update(self, game_id):
    print('send_game_state_update()')

    # Player info
    players = self.player_dao.get_players_with_game_id(game_id)
    print(f'players: {players}')
    mr_eleven = self.game_dao.get_attribute(game_id, GameAttribute.MR_ELEVEN)

    player_states = {
      p[PlayerAttribute.ID.value]: {
        'id': p[PlayerAttribute.ID.value],
        'nickname': 'Mr Eleven' if p[PlayerAttribute.ID.value] == mr_eleven else p[PlayerAttribute.NICKNAME.value],
        'turnFinished': False,
        'winCount': p[PlayerAttribute.WIN_COUNTER.value]
      }
      for p in players
    }

    # Round info
    is_round_complete = self._is_round_complete(game_id)
    round_state = {
      'complete': is_round_complete
    }

    # Turn info
    for turn in self.turn_dao.get_turns_with_game_id(game_id):
      print(f'turn: {turn}')
      player_id = turn[TurnAttribute.PLAYER_ID.value]
      player_states[player_id]['turnFinished'] = turn[TurnAttribute.FINISHED.value]
      if is_round_complete:
        player_states[player_id]['rollResult'] = turn[TurnAttribute.OUTCOME.value]

      rolls = self.roll_dao.get_rolls_with_turn_id(turn[TurnAttribute.ID.value])
      if rolls:
        roll = rolls[0]
        print(f'roll: {roll}')
        values = game_logic.get_values(roll[RollAttribute.DICE.value])
        print(f'values: {values}')
        player_states[player_id]['rollTotal'] = sum(values)
        player_states[player_id]['diceValue'] = str(values)
        
    # Send it
    message = {
      'action': 'gameState',
      'data': {
        'players': list(player_states.values()),
        'round': round_state,
      },
    }
    print(f'message: {message}')
    self.client_notifier.send_notification([p[PlayerAttribute.ID.value] for p in players], message)

  # def send_chat(self, player_id, game_id, message):
  #   self.client_notifier.send_notification(
  #     self.get_player_ids_in_game(game_id),
  #     {
  #       'action': 'sendMessage',
  #       'author': self.player_dao.get_attribute(player_id, PlayerAttribute.NICKNAME),
  #       'data': message,
  #     }
  #   )