
import pytest
from domain_models import GameAction, SessionAction


@pytest.fixture
def case(given_user_has_session, client_notifier):
    other_session_id = given_user_has_session.with_second_session()
    game_id = given_user_has_session.with_game(session_id=other_session_id)

    client_notifier.clear(given_user_has_session.connection_id)
    client_notifier.clear(given_user_has_session.second_connection_id)
    given_user_has_session.with_game(given_user_has_session.session_id, game_id)
    yield given_user_has_session


def test_it_updates_game_state(case, game_store):
    game = game_store.get(case.game_id)
    assert game.modified_action == GameAction.JOIN_GAME


def test_it_modifies_session(case, session_store):
    connection = session_store.get(case.session_id)
    assert connection.modified_action == SessionAction.JOIN_GAME


def test_it_notifies_connecting_player(case, client_notifier):
    actions = [n['action'] for n in client_notifier.notifications[case.connection_id]]
    assert 'joinGame' in actions
    assert 'gameState' in actions
    assert len(actions) == 2

  
def test_it_notifies_existing_player(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.second_connection_id]
        if n['action'] == 'gameState'
    ]
    assert len(notifications) == 1