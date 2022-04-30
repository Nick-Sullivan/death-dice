
from collections import Counter
from enum import Enum
from dice_models import Roll, D4, D6, D8, D10, D12, D20, D10Percentile


class RollResult(Enum):
  NONE = ''
  FINISH_DRINK = 'FINISH_DRINK'
  SIP_DRINK = 'SIP_DRINK'
  SHOWER = 'SHOWER'
  TIE = 'TIE'
  WINNER = 'WINNER'


def roll_dice(win_counter) -> Roll:
  initial = Roll([D6(), D6()])

  if _is_death_dice(win_counter):
    initial.append(_get_death_dice(win_counter))

  extra = Roll()
  while _should_roll_another_dice(initial, extra):
    extra.append(D6())

  return (initial + extra).to_json()


def _is_death_dice(win_counter):
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


def _should_roll_another_dice(initial_roll, extra_roll):
  duplicate_value, duplicate_counter = _get_duplicates(initial_roll.values)

  if duplicate_counter < 2:
    return False

  combined = [duplicate_value] * duplicate_counter + extra_roll.values
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
    2: 6,
    3: 3,
    4: 6,
    5: 6,
    6: 6,
  }[value]


def calculate_turn_results(rolls_json, mr_eleven=None):
  print('game_logic.calculate_turn_results()')
  print(f'rolls_json: {rolls_json}')

  rolls = {k: Roll.from_json(v) for k, v in rolls_json.items()}

  # Temp until i get back to this
  rolls = {k: roll.values for k, roll in rolls.items()}
  print(f'rolls: {rolls}')


  results = {}
  
  # Instant lose
  for k, values in rolls.items():

    if values[0] == 1 and values[1] == 1:
      if values[2] > 3:
        results[k] = RollResult.SIP_DRINK
      else:
        results[k] = RollResult.FINISH_DRINK
      continue

    if values[0] == 3 and values[1] == 3 and values[2] == 3:
      results[k] = RollResult.SHOWER
      continue

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

def get_values(roll_json):
  return Roll.from_json(roll_json).values