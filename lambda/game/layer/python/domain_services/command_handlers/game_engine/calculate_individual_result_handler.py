
import itertools
from collections import Counter
from typing import List

from domain_models import RollResult, RollResultNote, RollResultType
from domain_models.commands import CalculateIndividualResultCommand

INSTANT_LOSS_ROLLS = {
    RollResultNote.FINISH_DRINK,
    RollResultNote.POOL,
    RollResultNote.SIP_DRINK,
    RollResultNote.SHOWER,
    RollResultNote.DUAL_WIELD,
}

class CalculateIndividualResultHandler:
   
    def handle(self, command: CalculateIndividualResultCommand) -> RollResult:
        """Returns the result for this player, or NONEs if it can't be determined by this players rolls alone"""
        result = RollResult(
            note=RollResultNote.NONE,
            type=RollResultType.NONE,
            turn_finished=_is_turn_finished(command.rolls),
        )

        # Instant fail or win cases
        if is_roll_snake_eyes_fail(command.rolls):
            result.note = RollResultNote.FINISH_DRINK
            result.turn_finished = True
        elif is_roll_snake_eyes_safe(command.rolls):
            result.note = RollResultNote.SIP_DRINK
            result.turn_finished = True
        elif is_roll_shower(command.rolls):
            result.note = RollResultNote.SHOWER
            result.turn_finished = True
        elif is_roll_pool(command.rolls):
            result.note = RollResultNote.POOL
            result.turn_finished = True
        elif is_roll_dual_wield(command.rolls):
            result.note = RollResultNote.DUAL_WIELD
            result.turn_finished = True
        elif is_roll_head_on_table(command.rolls):
            result.note = RollResultNote.HEAD_ON_TABLE
            result.turn_finished = True
        elif is_roll_wish_purchase(command.rolls):
            result.note = RollResultNote.WISH_PURCHASE
            result.turn_finished = True
        elif result.turn_finished and command.is_mr_eleven and sum(get_values_from_rolls(command.rolls)) == 11:
            result.note = RollResultNote.WINNER
            result.type = RollResultType.WINNER

        # Notes, but not yet win or lose
        if not result.turn_finished:
            is_uh_oh = (
                is_roll_almost_snake_eyes(command.rolls)
                or is_roll_almost_dual_wield(command.rolls)
                or is_roll_almost_pool(command.rolls)
                or is_roll_almost_head_on_table(command.rolls)
                or is_roll_almost_wish_purchase(command.rolls)
                or is_roll_almost_shower(command.rolls)
            )
            if is_uh_oh:
                result.note = RollResultNote.UH_OH

        if result.note in INSTANT_LOSS_ROLLS:
            result.type = RollResultType.LOSER

        return result
    

def _is_turn_finished(rolls) -> bool:
    if not rolls:
        return False

    duplicate_value, duplicate_counter = _get_duplicates(rolls[0].values)

    if duplicate_counter < 2:
        return True

    combined = (
        [duplicate_value] * duplicate_counter
        + list(itertools.chain.from_iterable([r.values for r in rolls[1:]]))
    )
    return not _are_all_values_the_same(combined)
  

def _get_duplicates(values):
    return Counter(values).most_common(1)[0]


def _are_all_values_the_same(values):
    return len(set(values)) == 1


def is_roll_almost_snake_eyes(rolls):
    if not rolls:
        return False

    counter = Counter(rolls[0].values)
    return counter.get(1, 0) == 2


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


def is_roll_almost_dual_wield(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(2, 0) == 3


def is_roll_dual_wield(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(2, 0) >= 4


def is_roll_almost_pool(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(6, 0) == 5


def is_roll_pool(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(6, 0) >= 6


def is_roll_almost_head_on_table(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(4, 0) == 3


def is_roll_head_on_table(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(4, 0) >= 4


def is_roll_almost_wish_purchase(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(5, 0) == 4


def is_roll_wish_purchase(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(5, 0) >= 5


def is_roll_almost_shower(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(3, 0) == 2


def is_roll_shower(rolls):
    values = get_values_from_rolls(rolls)
    counter = Counter(values)
    return counter.get(3, 0) >= 3


def get_values_from_rolls(rolls) -> List[int]:
    values = []
    for r in rolls:
        values += r.values
    return values
