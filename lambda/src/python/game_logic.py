from enum import Enum


class RollResult(Enum):
  FINISH_DRINK = 'FINISH_DRINK'
  SIP_DRINK = 'SIP_DRINK'
  SHOWER = 'SHOWER'
  WINNER = 'WINNER'
  TIE = 'TIE'


def calculate_roll_results(rolls):
  print('calculate_roll_results()')
  print(f'rolls: {rolls}')
  
  max_value = max(rolls.values())
  is_tie = sum([v == max_value for v in rolls.values()]) > 1

  if is_tie:
    return {k: RollResult.TIE for k in rolls}

  return {
    k: RollResult.WINNER if v == max_value else RollResult.SIP_DRINK 
    for k, v in rolls.items()
  }
