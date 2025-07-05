
import pytest


@pytest.fixture
def case(given_user_has_session, client_notifier):
    client_notifier.clear(given_user_has_session.connection_id)
    given_user_has_session.with_invalid_game()
    yield given_user_has_session


def test_it_sends_a_notification(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.connection_id]
        if n['action'] == 'joinGame'
    ]
    assert len(notifications) == 1
    assert notifications[0]['error'] == f'Unable to join game: {case.game_id}'
    