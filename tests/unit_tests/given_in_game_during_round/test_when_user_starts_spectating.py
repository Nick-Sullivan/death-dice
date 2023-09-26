
import pytest
from domain_models import GameAction


@pytest.fixture
def game(game_id, game_store, start_spectating):
   yield game_store.get(game_id)


def test_it_updates_game_state(session_id, game):
  assert game.modified_action == GameAction.START_SPECTATING
  assert game.modified_by == session_id


def test_it_removes_connection_from_players(game):
  assert len(game.players) == 1


def test_it_adds_connection_to_spectators(game):
  assert len(game.spectators) == 1


def test_it_ends_the_game_round_if_finished(game):
  assert game.round_finished is True


def test_it_notifies_existing_playerr(start_spectating, client_notifier, connection_id_b):
    notifications = [
        n for n in client_notifier.notifications[connection_id_b]
        if n['action'] == 'gameState'
    ]
    assert len(notifications) == 1


def test_it_notifies_spectating_player(start_spectating, client_notifier, connection_id):
    notifications = [
        n for n in client_notifier.notifications[connection_id]
        if n['action'] == 'gameState'
    ]
    assert len(notifications) == 1
