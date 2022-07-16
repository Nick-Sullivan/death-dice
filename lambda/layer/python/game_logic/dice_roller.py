

from model import D4, D6, D8, D10, D12, D20, D10Percentile, Roll


class DiceRoller:
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
  }

  @staticmethod
  def roll(prev_rolls, win_counter, player_name) -> Roll:

    roll = Roll([D6(), D6()]) if not prev_rolls else Roll([D6()])

    if DiceRoller._should_roll_death_dice(win_counter, prev_rolls):
      roll.dice.append(DiceRoller._roll_death_dice(win_counter))

    if player_name in DiceRoller.SPECIAL_NAMES:
      DiceRoller._set_values_for_special_players(prev_rolls + [roll], player_name)

    return roll

  @staticmethod
  def _should_roll_death_dice(win_counter, prev_rolls) -> bool:
    return win_counter >= 3 and not prev_rolls

  @staticmethod
  def _roll_death_dice(win_counter) -> Roll:
    """Rolls the death dice with N sides according"""
    if win_counter in [3, 4]:
      return D4()
    elif win_counter in [5, 6]:
      return D6()
    elif win_counter in [7, 8]:
      return D8()
    elif win_counter in [9, 10]:
      return D10()
    elif win_counter in [11, 12]:
      return D12()
    elif win_counter in [13, 14]:
      return D20()
    elif win_counter > 14:
      return D10Percentile()

    raise NotImplementedError()

  @staticmethod
  def _set_values_for_special_players(rolls, player_name):
    """Used for reliable rolls in automated testing"""
    values = DiceRoller.SPECIAL_NAMES[player_name]
    i = 0
    for r in rolls:
      for d in r.dice:
        d.value = values[i]
        i += 1

