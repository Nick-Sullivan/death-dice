
import pytest
from domain_services.command_handlers import SetNicknameHandler


@pytest.fixture
def case(given_user_has_session, client_notifier):
    client_notifier.clear(given_user_has_session.connection_id)
    given_user_has_session.with_invalid_nickname(given_user_has_session.session_id)
    yield given_user_has_session



def test_it_sends_a_notification(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.connection_id]
        if n['action'] == 'setNickname'
    ]
    assert len(notifications) == 1
    assert notifications[0]['error'] == 'Invalid nickname'
    

@pytest.mark.parametrize('name, expected', [
    pytest.param('Roib', True, id='normal'),
    pytest.param('', False, id='too short'),
    pytest.param('1'*70, False, id='too long'),
    pytest.param('Mr Eleven', False, id='protected word'),
    pytest.param('Mr Eleven ', False, id='protected word with space'),
])
def test_is_valid_nickname(name, expected):
    assert SetNicknameHandler.is_valid_nickname(name) == expected
    