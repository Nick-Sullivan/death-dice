
import pytest
from domain_services.interfaces import SessionNotFoundException


@pytest.fixture
def case(given_two_player_game, client_notifier):
    given_two_player_game.with_destroyed_connection()
    client_notifier.clear(given_two_player_game.connection_id)
    client_notifier.clear(given_two_player_game.second_connection_id)
    given_two_player_game.with_timed_out_session()
    yield given_two_player_game


def test_it_destroys_session(case, session_store):
    with pytest.raises(SessionNotFoundException):
        session_store.get(case.session_id)


def test_it_notifies_remaining_connections(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.second_connection_id]
        if n['action'] == 'gameState'
    ]
    assert len(notifications) == 1
    assert notifications[0]['action'] == 'gameState'


def test_it_doesnt_destroy_the_game(case, game_store):
    game = game_store.get(case.game_id)
    assert game is not None


def test_it_ends_the_round_if_finished(case, game_store):
    game = game_store.get(case.game_id)
    assert game.round_finished is True
  