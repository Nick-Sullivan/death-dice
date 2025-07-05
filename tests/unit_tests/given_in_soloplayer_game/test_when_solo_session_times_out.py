
import pytest
from domain_services.interfaces import GameNotFoundException, SessionNotFoundException


@pytest.fixture
def case(given_user_has_game, client_notifier):
    given_user_has_game.with_destroyed_connection()
    client_notifier.clear(given_user_has_game.connection_id)
    given_user_has_game.with_timed_out_session()
    yield given_user_has_game


def test_it_destroys_session(case, session_store):
    with pytest.raises(SessionNotFoundException):
        session_store.get(case.session_id)


# def test_no_notification_is_sent(case, client_notifier):
#     assert case.connection_id not in client_notifier.notifications


def test_it_destroys_the_game(case, game_store):
    with pytest.raises(GameNotFoundException):
        game_store.get(case.game_id)
