
from dataclasses import dataclass

from domain_models.commands import NotifyConnectionsCommand

from ...interfaces import IClientNotifier


@dataclass
class NotifyConnectionsHandler:
    client_notifier: IClientNotifier

    def handle(self, command: NotifyConnectionsCommand):
        message = {}
        if command.action:
            message['action'] = command.action
        if command.data:
            message['data'] = command.data
        if command.error:
            message['error'] = command.error

        self.client_notifier.send_notification(
            command.connection_ids,
            message
        )
