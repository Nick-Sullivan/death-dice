
import pytest
from domain_models import SessionAction


@pytest.fixture
def case(given_user_has_session, client_notifier):
    client_notifier.clear(given_user_has_session.connection_id)
    given_user_has_session.with_nickname('a nickname')
    yield given_user_has_session


def test_it_updates_session(case, session_store):
    item = session_store.get(case.session_id)
    assert item.nickname == case.nickname
    assert item.modified_action == SessionAction.SET_NICKNAME


def test_it_sends_a_notification(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.connection_id]
        if n['action'] == 'setNickname'
    ]
    assert len(notifications) == 1
    assert notifications[0]['data']['nickname'] == case.nickname
    assert notifications[0]['data']['playerId'] == case.session_id
