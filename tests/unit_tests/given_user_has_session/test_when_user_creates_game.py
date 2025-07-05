
import pytest
from domain_models import GameAction, SessionAction


@pytest.fixture
def case(given_user_has_session):
    given_user_has_session.with_game()
    yield given_user_has_session


def test_it_creates_a_game(case, game_store):
    game = game_store.get(case.game_id)
    assert game.id is not None
    assert game.modified_action == GameAction.CREATE_GAME


def test_it_modifies_session(case, session_store):
    session = session_store.get(case.session_id)
    assert session.modified_action == SessionAction.JOIN_GAME


def test_it_publishes_an_event(case, event_publisher):
    events = [
        e for e in event_publisher.events['GameCreated']
        if e['game_id'] == case.game_id
    ]
    assert len(events) == 1


def test_it_sends_a_notification(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.connection_id]
        if n['action'] == 'joinGame'
    ]
    assert len(notifications) == 1
    assert notifications[0]['data'] == case.game_id
