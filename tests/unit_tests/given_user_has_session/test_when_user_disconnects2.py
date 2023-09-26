
import pytest
from domain_models import SessionAction


@pytest.fixture
def case(given_user_has_session):
    given_user_has_session.with_destroyed_connection()
    yield given_user_has_session


def test_it_marks_session_as_pending(case, session_store):
    session = session_store.get(case.session_id)
    assert session.modified_action == SessionAction.PENDING_TIMEOUT


def test_it_publishes_an_event(case, event_publisher):
    events = [
        e for e in event_publisher.events['Websocket']
        if e['connection_id'] == case.connection_id
    ]
    assert len(events) == 1
    