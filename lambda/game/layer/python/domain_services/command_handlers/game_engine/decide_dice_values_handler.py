from typing import List

from domain_models import D4, D6, D8, D10, D12, D20, D10Percentile, Roll
from domain_models.commands import DecideDiceValuesCommand

SPECIAL_NAMES = {
    'SNAKE_EYES': [1, 1, 1],
    'SNAKE_EYES_SAFE': [1, 1, 6],
    'DUAL': [2, 2, 2, 2],
    'DUAL_SPECIAL': [2, 2, 3, 2, 2],
    'SHOWER': [3, 3, 3],
    'HEAD': [4, 4, 4, 4, 4],
    'WISH': [5, 5, 5, 5, 5],
    'POOL': [6, 6, 6, 6, 6, 6],
    'MR_ELEVEN': [6, 5],
    'AVERAGE_JOE': [1, 2, 1],
    'AVERAGE_PETE': [1, 2, 2],
    'AVERAGE_GREG': [1, 2, 3],
    'ABOVE_AVERAGE_JOE': [5, 4, 4, 5],
    'LUCKY_JOE': [6, 6, 5],
    'QUANTAM_COCKRING1': [5, 3],
    'QUANTAM_COCKRING2': [3, 5],
}

class DecideDiceValuesHandler:

    def handle(self, command: DecideDiceValuesCommand) -> Roll:
       
        roll = Roll([D6(), D6()]) if not command.prev_rolls else Roll([D6()])

        if self._should_roll_death_dice(command.win_counter, command.prev_rolls):
            roll.dice.append(self._roll_death_dice(command.win_counter))

        if command.player_name in SPECIAL_NAMES:
            self._set_values_for_special_players(command.prev_rolls + [roll], command.player_name)

        return roll

    @staticmethod
    def _should_roll_death_dice(win_counter: int, prev_rolls: List[Roll]) -> bool:
        return win_counter >= 3 and not prev_rolls

    @staticmethod
    def _roll_death_dice(win_counter: int) -> Roll:
        if win_counter in [3, 4]:
            return D4(is_death_dice=True)
        elif win_counter in [5, 6]:
            return D6(is_death_dice=True)
        elif win_counter in [7, 8]:
            return D8(is_death_dice=True)
        elif win_counter in [9, 10]:
            return D10(is_death_dice=True)
        elif win_counter in [11, 12]:
            return D12(is_death_dice=True)
        elif win_counter in [13, 14]:
            return D20(is_death_dice=True)
        elif win_counter > 14:
            return D10Percentile(is_death_dice=True)

        raise NotImplementedError()

    @staticmethod
    def _set_values_for_special_players(rolls: List[Roll], player_name: str):
        """Used for reliable rolls in automated testing"""
        values = SPECIAL_NAMES[player_name]
        i = 0
        for r in rolls:
            for d in r.dice:
                d.value = values[i]
                i += 1
