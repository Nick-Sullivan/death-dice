
import pytest


@pytest.fixture
def case(given_user_is_connected, client_notifier):
    client_notifier.clear(given_user_is_connected.connection_id)
    given_user_is_connected.with_invalid_session()
    yield given_user_is_connected


def test_it_sends_a_notification(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.connection_id]
        if n['action'] == 'setSession'
    ]
    assert len(notifications) == 1
    assert notifications[0]['error'] == 'Invalid session ID'
    