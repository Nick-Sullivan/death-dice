
import pytest
from domain_models import GameAction, RollResultNote


@pytest.fixture
def case(given_two_player_game, client_notifier):
    given_two_player_game.with_new_round()
    given_two_player_game.with_rolled_dice()
    client_notifier.clear(given_two_player_game.connection_id)
    client_notifier.clear(given_two_player_game.second_connection_id)
    given_two_player_game.with_second_rolled_dice()
    yield given_two_player_game


@pytest.fixture
def game(case, game_store):
    yield game_store.get(case.game_id)


def test_it_updates_game_state(case, game):
  assert game.modified_action == GameAction.ROLL_DICE
  assert game.round_finished is True


def test_it_updates_winning_player_state(case, game):
    assert len(game.players) == 2
    player = next(p for p in game.players if p.id == case.second_session_id)
    assert player.outcome == RollResultNote.WINNER
    assert player.finished is True
    assert player.rolls[0].values == [5, 4]


def test_it_updates_losing_player_state(case, game):
    assert len(game.players) == 2
    player = next(p for p in game.players if p.id == case.session_id)
    assert player.outcome == RollResultNote.SIP_DRINK
    assert player.finished is True
    assert player.rolls[0].values == [1, 2]


def test_it_notifies_rolling_player(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.connection_id]
        if n['action'] == 'gameState'
    ]
    assert len(notifications) == 1

  
def test_it_notifies_existing_players(case, client_notifier):
    notifications = [
        n for n in client_notifier.notifications[case.second_connection_id]
        if n['action'] == 'gameState'
    ]
    assert len(notifications) == 1
    