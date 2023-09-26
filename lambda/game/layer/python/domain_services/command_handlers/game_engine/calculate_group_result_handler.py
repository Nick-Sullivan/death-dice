
from dataclasses import dataclass
from typing import Dict, List

from domain_models import RollResult, RollResultNote, RollResultType
from domain_models.commands import CalculateGroupResultCommand, CalculateIndividualResultCommand

from ...interfaces import IMediator


@dataclass
class CalculateGroupResultHandler:
    mediator: IMediator
   
    def handle(self, command: CalculateGroupResultCommand) -> (Dict[str, RollResult], str):
        """Check each win and loss conditions, incrementally removing losers that can't win"""
        self.player_rolls = command.player_rolls
        self.result = {}
        self.mr_eleven = command.mr_eleven

        self.contenders = {
            p: self.mediator.send(CalculateIndividualResultCommand(r, p == command.mr_eleven))
            for p, r in self.player_rolls.items()
        }

        self._assert_finished()
        self._remove_individual_losers()
        self._remove_three_way_tie()
        self._remove_mr_eleven_gets_eleven()
        self._remove_tie()
        self._remove_low_scores()

        return self.result, self._calculate_new_mr_eleven()

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

        is_tie = sum([v == max_value for v in roll_totals.values()]) == 3

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
                if max_value == 8 and roll_totals[player] == 8:
                    result.note = RollResultNote.COCKRING_HANDS
                else:
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
            p: sum(self._get_values_from_rolls(self.player_rolls[p]))
            for p in self.contenders
        }

    def _calculate_new_mr_eleven(self) -> str:
        """Determine who is the new Mr Eleven"""
        roll_totals = {k: sum(self._get_values_from_rolls(v)) for k, v in self.player_rolls.items()}

        if roll_totals.get(self.mr_eleven) == 11:
            return self.mr_eleven

        for k, v in roll_totals.items():
            if v == 11:
                return k
        
        return self.mr_eleven

    def _get_values_from_rolls(self, rolls) -> List[int]:
        values = []
        for r in rolls:
            values += r.values
        return values
