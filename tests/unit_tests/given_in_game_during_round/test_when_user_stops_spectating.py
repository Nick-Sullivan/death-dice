
import pytest
from domain_models import GameAction


@pytest.fixture
def game(game_id, game_store, stop_spectating):
   yield game_store.get(game_id)


def test_it_updates_game_state(session_id, game):
  assert game.modified_action == GameAction.STOP_SPECTATING
  assert game.modified_by == session_id


def test_it_removes_connection_from_spectators(game):
  assert len(game.spectators) == 0


def test_it_adds_connection_to_players(game):
  assert len(game.players) == 2


def test_it_doesnt_start_a_new_round(game):
  assert game.round_finished is True
  

def test_it_notifies_existing_player(stop_spectating, client_notifier, connection_id_b):
    notifications = [
        n for n in client_notifier.notifications[connection_id_b]
        if n['action'] == 'gameState'
    ]
    assert len(notifications) == 1

def test_it_notifies_new_player(stop_spectating, client_notifier, connection_id):
    notifications = [
        n for n in client_notifier.notifications[connection_id]
        if n['action'] == 'gameState'
    ]
    assert len(notifications) == 1
