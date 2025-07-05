
import pytest


@pytest.fixture
def case(given_user_is_connected):
    given_user_is_connected.with_session()
    yield given_user_is_connected


def test_it_creates_session_in_database(case, session_store):
    session = session_store.get(case.session_id)
    assert session is not None


def test_it_updates_connection_in_database(case, websocket_store):
    connection = websocket_store.get(case.connection_id)
    assert connection.session_id == case.session_id


def test_it_sends_a_notification(case, client_notifier):
    actions = [n['action'] for n in client_notifier.notifications[case.connection_id]]
    assert 'getSession' in actions
    assert len(actions) == 1
