
from client_interactor import ClientNotifier, lambda_handler
from dao import ConnectionDao, GameDao, TransactionWriter, concurrency_retry
from model import ConnectionAction, GameAction, GameState, Player, RollResultNote

connection_dao = ConnectionDao()
client_notifier = ClientNotifier()
game_dao = GameDao()


@lambda_handler
def create_game(connection_id, request):
  """Called by the WebSocketAPI when a player wants to create a new game"""

  connection = connection_dao.get(connection_id)

  game = _create_game(connection)
  
  client_notifier.send_notification([connection_id], {
    'action': 'joinGame',
    'data': game.id,
  })

  client_notifier.send_game_state_update(game)


@concurrency_retry
def _create_game(connection) -> GameState:
  
  game_id = game_dao.create_unique_game_id()

  connection.game_id = game_id
  connection.modified_action = ConnectionAction.JOIN_GAME

  game = GameState(
    id=game_id,
    mr_eleven='',
    round_id=0,
    round_finished=True,
    players=[Player(
      id=connection.id,
      account_id=connection.account_id,
      nickname=connection.nickname,
      win_counter=0,
      finished=False,
      outcome=RollResultNote.NONE,
      rolls=[]
    )],
    modified_action=GameAction.CREATE_GAME,
    modified_by=connection.id,
  )

  with TransactionWriter() as transaction:
    connection_dao.set(connection, transaction)
    game_dao.create(game, transaction)
  
  return game


if __name__ == '__main__':
  create_game({
    'requestContext': {
      'connectionId': 'nicks_connection_id'
    }
  }, None)
