import pytest
from domain_models import GameAction, RollResultNote


@pytest.fixture
def case(given_two_player_game, client_notifier):
    given_two_player_game.with_new_round()
    client_notifier.clear(given_two_player_game.connection_id)
    client_notifier.clear(given_two_player_game.second_connection_id)
    given_two_player_game.with_rolled_dice()
    yield given_two_player_game


def test_it_updates_game_state(case, game_store):
    game = game_store.get(case.game_id)
    assert game.modified_action == GameAction.ROLL_DICE
    assert game.modified_by == case.session_id
    assert game.round_finished is False


def test_it_updates_player_state(case, game_store):
    game = game_store.get(case.game_id)
    assert len(game.players) == 2
    player = next(p for p in game.players if p.id == case.session_id)
    assert player.outcome == RollResultNote.NONE
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
    