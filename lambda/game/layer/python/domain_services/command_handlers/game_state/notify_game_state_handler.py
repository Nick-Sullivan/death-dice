
import json
from dataclasses import dataclass

from domain_models.commands import NotifyGameStateCommand, NotifySessionsCommand

from ...interfaces import IClientNotifier, IMediator


@dataclass
class NotifyGameStateHandler:
    client_notifier: IClientNotifier
    mediator: IMediator

    def handle(self, command: NotifyGameStateCommand):
        game = command.game

        # Player and turn info
        player_output = []
        for player in game.players:
            entry = {
                'id': player.id,
                'nickname': 'Mr Eleven' if player.id == game.mr_eleven else player.nickname,
                'turnFinished': player.finished,
                'winCount': player.win_counter,
                'rollResult': player.outcome.value,
                'connectionStatus': player.connection_status.value,
            }

            # Combine dice rolls into one
            if player.rolls:

                dice_roll = player.rolls[0]
                for dr in player.rolls[1:]:
                    dice_roll += dr

                entry['rollTotal'] = sum(dice_roll.values)
                entry['diceValue'] = json.dumps(dice_roll.to_json())

            player_output.append(entry)

        # Order by player joined time TODO
        player_output.sort(key=lambda x: x['id'])
        
        spectator_output = []
        for spectator in game.spectators:
            entry = {
                'id': spectator.id,
                'nickname': 'Mr Eleven' if spectator.id == game.mr_eleven else spectator.nickname,
            }
            spectator_output.append(entry)

        # Send it
        message = {
            'gameId': game.id,
            'players': player_output,
            'spectators': spectator_output,
            'round': {'complete': game.round_finished},
        }
        self.mediator.send(NotifySessionsCommand(
            session_ids=[p.id for p in game.players] + [p.id for p in game.spectators],
            action='gameState',
            data=message,
        ))
