from random import randint
from enum import Enum


class RollResult(Enum):
  FINISH_DRINK = 'FINISH_DRINK'
  SIP_DRINK = 'SIP_DRINK'
  SHOWER = 'SHOWER'
  TIE = 'TIE'
  WINNER = 'WINNER'


def roll_dice():
  values = [
    randint(1, 6),
    randint(1, 6),
  ]

  while _roll_another_dice(values):
    values.append(randint(1, 6))

  return values


def _roll_another_dice(values):
  return (
    _are_all_values_the_same(values)
    and len(values) < _max_duplicates(values[0])
  )


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


def calculate_roll_results(rolls, mr_eleven=None):
  print('calculate_roll_results()')
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
