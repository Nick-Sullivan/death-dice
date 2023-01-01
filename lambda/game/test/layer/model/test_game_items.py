
# import os
# import pytest
# import sys
# from datetime import datetime
# from unittest.mock import MagicMock

# sys.path.append(os.path.abspath('./lambda/src/python'))
# from model.dice import D6
# from model.game_items import GameState, Player, Roll
# from model.roll_result import RollResultNote


# class TestRoll:

#   def test_append(self):
#     roll = Roll([D6(1)])
#     roll.append(D6(2))
#     assert roll.values == [1, 2]

#   def test_add(self):
#     result = Roll([D6(1)]) + Roll([D6(2)])
#     assert isinstance(result, Roll)
#     assert result.values == [1, 2]


# class TestGame:

#   @pytest.fixture
#   def obj(self):
#     return GameState(
#       id='ABCD',
#       mr_eleven='mr_eleven',
#       round_finished=False,
#       players=[
#         Player(
#           id='p1',
#           nickname='player1',
#           win_counter=2,
#           finished=True,
#           outcome=RollResultNote.POOL,
#           rolls=[
#             Roll([D6(5), D6(5)]),
#             Roll([D6(2)]),
#           ],
#         ),
#       ],
#       version=7,
#       created_on=datetime(year=2022, month=7, day=1),
#     )

#   @pytest.fixture
#   def serialised(self):
#     return {"id": {"S": "ABCD"}, "mr_eleven": {"S": "mr_eleven"}, "round_finished": {"BOOL": False}, "players": {"L": [{"M": {"id": {"S": "p1"}, "nickname": {"S": "player1"}, "win_counter": {"N": "2"}, "finished": {"BOOL": True}, "outcome": {"S": "POOL"}, "rolls": {"L": [{"M": {"dice": {"L": [{"M": {"id": {"S": "D6"}, "value": {"N": "5"}}}, {"M": {"id": {"S": "D6"}, "value": {"N": "5"}}}]}}}, {"M": {"dice": {"L": [{"M": {"id": {"S": "D6"}, "value": {"N": "2"}}}]}}}]}}}]}, "version": {"N": "7"}, "created_on": {"S": "2022-07-01 00:00:00"}}
  
#   def test_serialise(self, obj, serialised):
#     result = GameState.serialise(obj)
#     assert result == serialised

#   def test_deserialise(self, obj, serialised):
#     result = GameState.deserialise(serialised)
#     assert isinstance(result, GameState)
#     assert isinstance(result.players[0], Player)
#     assert isinstance(result.players[0].rolls[0], Roll)
#     assert result.players[0].rolls[1].dice[0].value == 2
  