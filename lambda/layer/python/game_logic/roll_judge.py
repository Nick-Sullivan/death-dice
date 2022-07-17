
import itertools
from collections import Counter
from typing import Dict, List

from model import RollResult, RollResultNote, RollResultType


class IndividualRollJudge:

  instant_loss_rolls = {
    RollResultNote.FINISH_DRINK,
    RollResultNote.POOL,
    RollResultNote.SIP_DRINK,
    RollResultNote.SHOWER,
  }

  @classmethod
  def calculate_result(cls, rolls, is_mr_eleven) -> RollResult:
    """Returns the roll result details for this player, or NONEs if it can't be determined by this players rolls alone"""
    result = RollResult(
      note=RollResultNote.NONE,
      type=RollResultType.NONE,
      turn_finished=IndividualRollJudge._is_turn_finished(rolls),
    )

    # Instant fail or win cases
    if cls.is_roll_snake_eyes_fail(rolls):
      result.note = RollResultNote.FINISH_DRINK
      result.turn_finished = True
    elif cls.is_roll_snake_eyes_safe(rolls):
      result.note = RollResultNote.SIP_DRINK
      result.turn_finished = True
    elif cls.is_roll_shower(rolls):
      result.note = RollResultNote.SHOWER
      result.turn_finished = True
    elif cls.is_roll_pool(rolls):
      result.note = RollResultNote.POOL
      result.turn_finished = True
    elif cls.is_roll_dual_wield(rolls):
      result.note = RollResultNote.DUAL_WIELD
      result.turn_finished = True
    elif cls.is_roll_head_on_table(rolls):
      result.note = RollResultNote.HEAD_ON_TABLE
      result.turn_finished = True
    elif cls.is_roll_wish_purchase(rolls):
      result.note = RollResultNote.WISH_PURCHASE
      result.turn_finished = True
    elif result.turn_finished and is_mr_eleven and sum(get_values_from_rolls(rolls)) == 11:
      result.note = RollResultNote.WINNER
      result.type = RollResultType.WINNER

    # Notes, but not yet win or lose
    if not result.turn_finished:
      is_uh_oh = (
        cls.is_roll_almost_snake_eyes(rolls)
        or cls.is_roll_almost_dual_wield(rolls)
        or cls.is_roll_almost_pool(rolls)
        or cls.is_roll_almost_head_on_table(rolls)
        or cls.is_roll_almost_wish_purchase(rolls)
        or cls.is_roll_almost_shower(rolls)
      )
      if is_uh_oh:
        result.note = RollResultNote.UH_OH

    if result.note in IndividualRollJudge.instant_loss_rolls:
      result.type = RollResultType.LOSER

    return result
    
  @staticmethod
  def _is_turn_finished(rolls) -> bool:
    if not rolls:
      return False

    duplicate_value, duplicate_counter = IndividualRollJudge._get_duplicates(rolls[0].values)

    if duplicate_counter < 2:
      return True

    combined = [duplicate_value] * duplicate_counter + list(itertools.chain.from_iterable([r.values for r in rolls[1:]]))
    return not IndividualRollJudge._are_all_values_the_same(combined)
  
  @staticmethod
  def _get_duplicates(values):
    return Counter(values).most_common(1)[0]

  @staticmethod
  def _are_all_values_the_same(values):
    return len(set(values)) == 1

  @staticmethod
  def is_roll_almost_snake_eyes(rolls):
    if not rolls:
      return False

    counter = Counter(rolls[0].values)
    return counter.get(1, 0) == 2

  @staticmethod
  def is_roll_snake_eyes_fail(rolls):
    if not rolls:
      return False

    counter = Counter(rolls[0].values)
    if counter.get(1, 0) < 2:
      return False

    if counter.get(1, 0) == 3:
      return True
    
    if len(rolls) < 2:
      return False

    return rolls[1].values[0] in {1, 2, 3}

  @staticmethod
  def is_roll_snake_eyes_safe(rolls):
    if not rolls:
      return False

    counter = Counter(rolls[0].values)
    if counter.get(1, 0) < 2:
      return False

    if counter.get(1, 0) == 3:
      return False
    
    if len(rolls) < 2:
      return False

    return rolls[1].values[0] in {4, 5, 6}

  @staticmethod
  def is_roll_almost_dual_wield(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(2, 0) == 3

  @staticmethod
  def is_roll_dual_wield(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(2, 0) >= 4

  @staticmethod
  def is_roll_almost_pool(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(6, 0) == 5

  @staticmethod
  def is_roll_pool(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(6, 0) >= 6

  @staticmethod
  def is_roll_almost_head_on_table(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(4, 0) == 3

  @staticmethod
  def is_roll_head_on_table(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(4, 0) >= 4

  @staticmethod
  def is_roll_almost_wish_purchase(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(5, 0) == 4

  @staticmethod
  def is_roll_wish_purchase(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(5, 0) >= 5
  
  @staticmethod
  def is_roll_almost_shower(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(3, 0) == 2

  @staticmethod
  def is_roll_shower(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(3, 0) >= 3


class GroupRollJudge:

  def __init__(self, player_rolls, mr_eleven):
    self.player_rolls = player_rolls
    self.mr_eleven = mr_eleven
    self.result = {}
    self.contenders = {}

  def calculate_result(self) -> Dict[str, RollResult]:
    """Check each win and loss conditions, incrementally removing losers that can't win"""
    self.contenders = {p: IndividualRollJudge.calculate_result(r, p == self.mr_eleven) for p, r in self.player_rolls.items()}

    self._assert_finished()
    self._remove_individual_losers()
    self._remove_three_way_tie()
    self._remove_mr_eleven_gets_eleven()
    self._remove_tie()
    self._remove_low_scores()

    return self.result

  def _assert_finished(self):
    """Checks that this judge has only been called when all turns are complete"""
    assert all(r.turn_finished for r in self.contenders.values())

  def _remove_individual_losers(self):
    """Removes players from contention if they have been assessed as losing according to their individual rolls"""
    for player, result in self.contenders.items():
      if result.type == RollResultType.LOSER:
        self.result[player] = result
    
    self.contenders = {p: r for p, r in self.contenders.items() if p not in self.result}

  def _remove_three_way_tie(self):
    """Removes players from contention if there is a three way tie"""
    if len(self.contenders) != 3:
      return

    roll_totals = self._get_contendor_roll_totals()

    max_value = max(roll_totals.values())

    is_tie = sum([v == max_value for v in roll_totals.values()]) > 1

    if not is_tie:
      return
    
    for player, result in self.contenders.items():

      if result.note == RollResultNote.NONE:
        result.note = RollResultNote.THREE_WAY_TIE

      result.type = RollResultType.NO_CHANGE
      result.turn_finished = False

      self.result[player] = result

    self.contenders = {p: r for p, r in self.contenders.items() if p not in self.result}

  def _remove_mr_eleven_gets_eleven(self):
    """Removes players from contention if Mr Eleven rolled an 11"""
    roll_totals = self._get_contendor_roll_totals()

    if roll_totals.get(self.mr_eleven) != 11:
      return

    max_value = max(roll_totals.values())

    for player, result in self.contenders.items():
      if player == self.mr_eleven:
        result.note = RollResultNote.WINNER
        result.type = RollResultType.WINNER

      elif max_value == 11 and roll_totals[player] == 11:
        result.note = RollResultNote.WINNER
        result.type = RollResultType.NO_CHANGE
      
      elif result.note == RollResultNote.NONE:
        result.note = RollResultNote.SIP_DRINK
        result.type = RollResultType.LOSER
      
      else:
        result.type = RollResultType.LOSER

      self.result[player] = result
    self.contenders = {p: r for p, r in self.contenders.items() if p not in self.result}

  def _remove_tie(self):
    """Removes players from contention everyone rolled a tie"""
    if not self.contenders:
      return
    
    roll_totals = self._get_contendor_roll_totals()

    max_value = max(roll_totals.values())

    is_tie = sum([v == max_value for v in roll_totals.values()]) > 1

    if not is_tie:
      return

    for player, result in self.contenders.items():

      if result.note == RollResultNote.NONE:
        result.note = RollResultNote.TIE

      result.type = RollResultType.LOSER

      self.result[player] = result
    
    self.contenders = {p: r for p, r in self.contenders.items() if p not in self.result}

  def _remove_low_scores(self):
    """Removes players from contention if they didn't get the highest score"""
    if not self.contenders:
      return

    roll_totals = self._get_contendor_roll_totals()
    max_value = max(roll_totals.values())

    for player, result in self.contenders.items():
      if roll_totals[player] == max_value:
        result.type = RollResultType.WINNER
        if result.note == RollResultNote.NONE:
          result.note = RollResultNote.WINNER
      
      else:
        result.type = RollResultType.LOSER
        if result.note == RollResultNote.NONE:
          result.note = RollResultNote.SIP_DRINK

      self.result[player] = result

    self.contenders = {p: r for p, r in self.contenders.items() if p not in self.result}

  def _get_contendor_roll_totals(self):
    return {
      p: sum(get_values_from_rolls(self.player_rolls[p]))
      for p in self.contenders
    }

  def calculate_new_mr_eleven(self) -> str:
    """Determine who is the new Mr Eleven"""
    roll_totals = {k: sum(get_values_from_rolls(v)) for k, v in self.player_rolls.items()}

    if roll_totals.get(self.mr_eleven) == 11:
      return self.mr_eleven

    for k, v in roll_totals.items():
      if v == 11:
        return k
    
    return self.mr_eleven


def get_values_from_rolls(rolls) -> List[int]:
  values = []
  for r in rolls:
    values += r.values
  return values
