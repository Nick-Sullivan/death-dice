
import itertools
from collections import Counter
from enum import Enum

from dice_models import Roll, D4, D6, D8, D10, D12, D20, D10Percentile


class RollResult(Enum):
  NONE = ''
  DUAL_WIELD = 'DUAL_WIELD'
  HEAD_ON_TABLE = 'HEAD_ON_TABLE'
  FINISH_DRINK = 'FINISH_DRINK'
  POOL = 'POOL'
  SIP_DRINK = 'SIP_DRINK'
  SHOWER = 'SHOWER'
  TIE = 'TIE'
  WINNER = 'WINNER'
  WISH_PURCHASE = 'WISH_PURCHASE'


SPECIAL_NAMES = {
  'SNAKE_EYES': [1, 1, 1],
  'SNAKE_EYES_SAFE': [1, 1, 6],
  'DUAL': [2, 2, 2, 2],
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


def initial_roll(win_counter, special_name=None):
  roll = Roll([D6(), D6()])

  if _should_roll_death_dice(win_counter):
    roll.append(_get_death_dice(win_counter))

  if special_name in SPECIAL_NAMES:
    values = SPECIAL_NAMES[special_name]
    for i, d in enumerate(roll.dice):
      d.value = values[i]

  return roll.to_json(), not _should_roll_another_dice([roll])


def extra_roll(prev_rolls, special_name=None):
  roll = Roll([D6()])

  if special_name in SPECIAL_NAMES:
    prev_values = list(itertools.chain.from_iterable([r.values for r in prev_rolls]))
    values = SPECIAL_NAMES[special_name]
    for i, d in enumerate(roll.dice):
      d.value = values[i+len(prev_values)]

  return roll.to_json(), not _should_roll_another_dice(prev_rolls + [roll])


def _should_roll_death_dice(win_counter):
  return win_counter >= 3


def _get_death_dice(win_counter):
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


def _should_roll_another_dice(rolls):
  duplicate_value, duplicate_counter = _get_duplicates(rolls[0].values)

  if duplicate_counter < 2:
    return False

  combined = [duplicate_value] * duplicate_counter + list(itertools.chain.from_iterable([r.values for r in rolls[1:]]))
  return (
    _are_all_values_the_same(combined)
    and len(combined) < _max_duplicates(combined[0])
  )


def _get_duplicates(values):
  return Counter(values).most_common(1)[0]


def _are_all_values_the_same(values):
  return len(set(values)) == 1


def _max_duplicates(value):
  return {
    1: 3,
    2: 4,
    3: 3,
    4: 5,
    5: 5,
    6: 6,
  }[value]


def calculate_turn_results(roll_obj_dict, mr_eleven=None):
  print('game_logic.calculate_turn_results()')
  print(f'roll_objs: {roll_obj_dict}')

  # rolls = {k: Roll.from_json(v).values for k, v in rolls_json.items()}
  rolls = {}
  for k, roll_objs in roll_obj_dict.items():
    rolls[k] = list(itertools.chain.from_iterable([r.values for r in roll_objs]))
  print(f'rolls: {rolls}')

  results = {}
  
  # Instant lose
  for k, values in rolls.items():

    if is_roll_snake_eyes_fail(values):
      results[k] = RollResult.FINISH_DRINK

    elif is_roll_snake_eyes_safe(values):
      results[k] = RollResult.SIP_DRINK

    elif is_roll_dual_wield(values):
      results[k] = RollResult.DUAL_WIELD

    elif is_roll_shower(values):
      results[k] = RollResult.SHOWER
    
    elif is_roll_head_on_table(values):
      results[k] = RollResult.HEAD_ON_TABLE

    elif is_roll_wish_purchase(values):
      results[k] = RollResult.WISH_PURCHASE
    
    elif is_roll_pool(values):
      results[k] = RollResult.POOL


  # In the running
  roll_totals = {k: sum(v) for k, v in rolls.items() if k not in results}

  if not roll_totals:
    return results, mr_eleven

  # Mr eleven wins, anyone else that gets an 11 doesn't lose
  if mr_eleven is not None:
    if roll_totals.get(mr_eleven) == 11:
      results.update({
        k: RollResult.WINNER if v == 11 else RollResult.SIP_DRINK 
        for k, v in roll_totals.items()
      })
      return results, mr_eleven

  # New mr eleven
  for k, v in roll_totals.items():
    if v == 11:
      mr_eleven = k
      break

  # Winner is the highest total

  max_value = max(roll_totals.values())
  is_tie = sum([v == max_value for v in roll_totals.values()]) > 1

  if is_tie:
    results.update({k: RollResult.TIE for k in roll_totals})
  else:
    results.update({
      k: RollResult.WINNER if v == max_value else RollResult.SIP_DRINK 
      for k, v in roll_totals.items()
    })

  return results, mr_eleven


def is_roll_snake_eyes_fail(values):
  counter = Counter(values[:-1])
  if counter.get(1, 0) >= 2:
    return values[-1] in [1, 2, 3]
  return False


def is_roll_snake_eyes_safe(values):
  counter = Counter(values[:-1])
  if counter.get(1, 0) >= 2:
    return values[-1] in [4, 5, 6]
  return False


def is_roll_dual_wield(values):
  counter = Counter(values)
  return counter.get(2, 0) >= 4


def is_roll_pool(values):
  counter = Counter(values)
  return counter.get(6, 0) >= 6


def is_roll_head_on_table(values):
  counter = Counter(values)
  return counter.get(4, 0) >= 5


def is_roll_wish_purchase(values):
  counter = Counter(values)
  return counter.get(5, 0) >= 5
  

def is_roll_shower(values):
  counter = Counter(values)
  return counter.get(3, 0) >= 3


def get_values(roll_json):
  return Roll.from_json(roll_json).values


def get_roll(roll_json):
  return Roll.from_json(roll_json)
