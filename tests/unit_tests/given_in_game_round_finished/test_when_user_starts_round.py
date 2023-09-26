
import pytest
from domain_models import GameAction, RollResultNote


@pytest.fixture
def case(given_two_player_game, client_notifier):
    client_notifier.clear(given_two_player_game.connection_id)
    client_notifier.clear(given_two_player_game.second_connection_id)
    given_two_player_game.with_new_round()
    yield given_two_player_game


def test_it_updates_game_state(case, game_store):
    game = game_store.get(case.game_id)
    assert game.modified_action == GameAction.NEW_ROUND
    assert game.modified_by == case.session_id
    assert game.round_finished is False


def test_it_updates_players(case, game_store):
    game = game_store.get(case.game_id)
    for player in game.players:
        assert player.outcome == RollResultNote.NONE
        assert player.finished is False
        assert player.rolls == []
  

def test_it_notifies_players(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.connection_id]
        if n['action'] == 'gameState'
    ]
    assert len(notifications) == 1
