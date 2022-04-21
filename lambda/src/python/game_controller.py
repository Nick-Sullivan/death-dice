import random
import string

from db_interactor import DatabaseInteractor
from player_interactor import PlayerInteractor
import game_logic


class GameController:
  """Responsible for game logic and state change"""
  
  def __init__(self):
    self.db = DatabaseInteractor()
    self.player_interactor = PlayerInteractor()

  # Players

  def create_player(self, player_id):
    self.db.create_player(player_id)

  def delete_player(self, player_id):
    """Remove the player from the database, and any games they are part of"""
    game_id = self.get_game_id(player_id)

    self.db.delete_player(player_id)

    if not game_id:
      return

    if self.get_player_ids_in_game(game_id):
      self.send_game_state_update(game_id)
    else:
      self._delete_game(game_id)

  def set_nickname(self, player_id, nickname):
    self.db.update_player_attribute(player_id, 'Nickname', nickname)

    message = {
      'action': 'setNickname',
      'data': {
        'nickname': nickname,
        'playerId': player_id,
      },
    }
    self.player_interactor.send_notification([player_id], message)

  def get_nickname(self, player_id):
    return self.db.get_player_attribute(player_id, 'Nickname')

  def get_game_id(self, player_id):
    return self.db.get_player_attribute(player_id, 'GameId')

  # Games

  def create_game(self, player_id):
    """Creates a new game, and adds this player to it"""
    game_id = self._create_unique_game_id()

    self.db.create_game(game_id)

    self.join_game(player_id, game_id)

    return game_id

  def _create_unique_game_id(self):
    """Creates a unique game ID that doesn't yet exist in the database"""
    # gen = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    gen = lambda: ''.join(random.choices(string.ascii_uppercase, k=4))

    game_id = gen()
    while self.db.game_exists(game_id):
      game_id = gen()

    return game_id
  
  def _delete_game(self, game_id):
    self.db.delete_rolls_in_game(game_id)
    self.db.delete_game(game_id)

  def join_game(self, player_id, game_id):
    if not self.db.game_exists(game_id):
      message = {
        'action': 'joinGame',
        'error': f'Game ID does not exist: {game_id}',
      }
      self.player_interactor.send_notification([player_id], message)
      return

    self.db.update_player_attribute(player_id, 'GameId', game_id)

    message = {
      'action': 'joinGame',
      'data': game_id,
    }
    self.player_interactor.send_notification([player_id], message)

    self.send_game_state_update(game_id)

  def get_player_ids_in_game(self, game_id):
    return self.db.get_player_ids_in_game(game_id)

  # Rolls

  def new_round(self, game_id):
    self.db.delete_rolls_in_game(game_id)

    self.db.update_game_attribute(game_id, 'IsRoundComplete', False)

    self.send_game_state_update(game_id)

  def get_dice_value(self, roll_id):
    return self.db.get_roll_attribute(roll_id, 'DiceValue')

  def get_roll_result(self, roll_id):
    return self.db.get_roll_attribute(roll_id, 'RollResult')

  def get_player_id(self, roll_id):
    return self.db.get_roll_attribute(roll_id, 'PlayerId')

  def roll_dice(self, player_id):
    dice_value = random.randint(1, 6)
    game_id = self.get_game_id(player_id)

    self.db.create_roll(game_id, player_id, dice_value)

    if self._is_round_complete(game_id):
      self.calculate_roll_results(game_id)

    self.send_game_state_update(game_id)

  def calculate_roll_results(self, game_id):
    roll_ids = self.db.get_roll_ids_in_game(game_id)
    values = {r: self.get_dice_value(r) for r in roll_ids}
    results = game_logic.calculate_roll_results(values)

    for roll_id, result in results.items():
      self.db.update_roll_attribute(roll_id, 'RollResult', result.value)


  def _is_round_complete(self, game_id):
    """Round is complete if all players have rolled"""
    print('_is_round_complete()')
    roll_ids = self.db.get_roll_ids_in_game(game_id)
    player_ids = self.get_player_ids_in_game(game_id)

    if len(roll_ids) == len(player_ids):
      return True
    
    return False

  # Notifications

  def send_chat(self, player_id, game_id, message):
    self.player_interactor.send_notification(
      self.get_player_ids_in_game(game_id),
      {
        'action': 'sendMessage',
        'author': self.get_nickname(player_id),
        'data': message,
      }
    )
  
  def send_game_state_update(self, game_id):
    # Player info
    player_ids = self.get_player_ids_in_game(game_id)

    player_states = {
      player_id: {
        'id': player_id,
        'nickname': self.get_nickname(player_id),
        'hasRolled': False,
      }
      for player_id in player_ids
    }

    # Round info
    is_round_complete = self._is_round_complete(game_id)
    round_state = {
      'complete': is_round_complete
    }

    # Roll info
    roll_ids = self.db.get_roll_ids_in_game(game_id)

    for roll_id in roll_ids:
      player_id = self.get_player_id(roll_id)
      dice_value = self.get_dice_value(roll_id)
      player_states[player_id]['hasRolled'] = True
      player_states[player_id]['diceValue'] = str(dice_value)
      if is_round_complete:
        player_states[player_id]['rollResult'] = self.get_roll_result(roll_id)
        
    # Send it
    message = {
      'action': 'gameState',
      'data': {
        'players': list(player_states.values()),
        'round': round_state,
      },
    }
    self.player_interactor.send_notification(player_ids, message)
