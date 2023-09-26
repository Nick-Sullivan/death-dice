
import pytest
from domain_services.interfaces import SessionNotFoundException


@pytest.fixture
def case(given_session_is_pending_timeout):
    given_session_is_pending_timeout.with_timed_out_session()
    yield given_session_is_pending_timeout

    
def test_it_destroys_session(case, session_store):
    with pytest.raises(SessionNotFoundException):
        session_store.get(case.session_id)
