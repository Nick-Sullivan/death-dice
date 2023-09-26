

import pytest


@pytest.fixture
def case(given_user_is_new):
    given_user_is_new.with_connection()
    yield given_user_is_new


def test_it_is_saved_in_database(case, websocket_store):
    connection = websocket_store.get(case.connection_id)
    assert connection is not None
