
from dataclasses import dataclass

from domain_models import SessionAction, SessionItem
from domain_models.commands import NotifyConnectionsCommand, SetNicknameCommand

from ...interfaces import IMediator, ISessionStore, ITransactionWriter


@dataclass
class SetNicknameHandler:
    mediator: IMediator
    session_store: ISessionStore
    transaction_writer: ITransactionWriter

    def handle(self, command: SetNicknameCommand):

        session = self.session_store.get(command.session_id)

        if not self.is_valid_nickname(command.nickname):
            self._send_invalid_nickname_response(session)
            return

        session.nickname = command.nickname
        session.account_id = command.account_id
        session.modified_action = SessionAction.SET_NICKNAME
        
        with self.transaction_writer.create() as transaction:
            self.session_store.set(session, transaction)

        self._send_nickname_response(session)

    @staticmethod
    def is_valid_nickname(name: str) -> bool:
        invalid_names = {'MR ELEVEN', 'MRELEVEN', 'MR 11', 'MR11'}
        return (
            2 <= len(name) <= 69
            and name.upper().strip() not in invalid_names
        )
    
    def _send_invalid_nickname_response(self, session: SessionItem):
        self.mediator.send(NotifyConnectionsCommand(
            [session.connection_id],
            action='setNickname',
            error='Invalid nickname'
        ))

    def _send_nickname_response(self, session: SessionItem):
        self.mediator.send(NotifyConnectionsCommand(
            [session.connection_id],
            action='setNickname',
            data={
                'nickname': session.nickname,
                'playerId': session.id,
            }
        ))
        