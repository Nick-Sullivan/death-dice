
import pytest
from domain_services.interfaces import WebsocketConnectionNotFoundException


@pytest.fixture
def case(given_user_is_connected):
    given_user_is_connected.with_destroyed_connection()
    yield given_user_is_connected


def test_it_is_not_in_the_database(case, websocket_store):
    with pytest.raises(WebsocketConnectionNotFoundException):
        websocket_store.get(case.connection_id)


def test_it_does_not_publish_an_event(case, event_publisher):
    events = [
        e for e in event_publisher.events.get('Websocket', [])
        if e['connection_id'] == case.connection_id
    ]
    assert len(events) == 0
    