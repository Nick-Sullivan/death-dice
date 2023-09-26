
import uuid

import pytest
from domain_models.commands import (
    CheckSessionTimeoutCommand,
    CreateConnectionCommand,
    CreateGameCommand,
    CreateSessionIdCommand,
    DestroyConnectionCommand,
    JoinGameCommand,
    NewRoundCommand,
    RollDiceCommand,
    SetNicknameCommand,
    SetSessionIdCommand,
    StartSpectatingCommand,
    StopSpectatingCommand,
)
from domain_services.interfaces import (
    IClientNotifier,
    IEventPublisher,
    IGameStore,
    ISessionStore,
    IWebsocketConnectionStore,
)
from infrastructure.infrastructure_provider import infrastructure_instances
from mediator import mediator


@pytest.fixture
def client_notifier():
    yield infrastructure_instances[IClientNotifier]


@pytest.fixture
def game_store():
    yield infrastructure_instances[IGameStore]


@pytest.fixture
def event_publisher():
    yield infrastructure_instances[IEventPublisher]


@pytest.fixture
def websocket_store():
    yield infrastructure_instances[IWebsocketConnectionStore]


@pytest.fixture
def session_store():
    yield infrastructure_instances[ISessionStore]


@pytest.fixture
def connection_id():
    yield mediator.send(CreateConnectionCommand(uuid.uuid4())).connection_id


@pytest.fixture
def session_id(connection_id) -> int:
    yield mediator.send(CreateSessionIdCommand(connection_id))


@pytest.fixture
def nickname(session_id) -> str:
    nickname = 'AVERAGE_JOE'
    mediator.send(SetNicknameCommand(session_id, '', 'AVERAGE_JOE'))
    yield nickname


@pytest.fixture
def game_id(nickname, session_id) -> int:
    game = mediator.send(CreateGameCommand(session_id))
    yield game.id


@pytest.fixture
def destroyed_connection_id(connection_id, session_id):
    mediator.send(DestroyConnectionCommand(connection_id))
    yield connection_id


@pytest.fixture
def connection_id_b():
    yield mediator.send(CreateConnectionCommand(uuid.uuid4())).connection_id


@pytest.fixture
def session_id_b(connection_id_b) -> int:
    yield mediator.send(CreateSessionIdCommand(connection_id_b))


@pytest.fixture
def nickname_b(session_id_b) -> str:
    nickname = 'ABOVE_AVERAGE_JOE'
    mediator.send(SetNicknameCommand(session_id_b, '', 'ABOVE_AVERAGE_JOE'))
    yield nickname


@pytest.fixture
def game_id_b(nickname_b, session_id_b) -> int:
    game = mediator.send(CreateGameCommand(session_id_b))
    yield game.id


@pytest.fixture
def multiplayer_game_id(nickname_b, session_id_b, game_id) -> int:
    game = mediator.send(JoinGameCommand(session_id_b, game_id))
    yield game.id


@pytest.fixture
def new_round(connection_id, session_id, multiplayer_game_id, client_notifier):
    client_notifier.clear(connection_id)
    mediator.send(NewRoundCommand(session_id))


@pytest.fixture
def roll(new_round, connection_id, connection_id_b, session_id, client_notifier):
    client_notifier.clear(connection_id)
    client_notifier.clear(connection_id_b)
    yield mediator.send(RollDiceCommand(session_id))


@pytest.fixture
def roll_b(new_round, connection_id, connection_id_b, session_id_b, client_notifier):
    client_notifier.clear(connection_id)
    client_notifier.clear(connection_id_b)
    yield mediator.send(RollDiceCommand(session_id_b))


@pytest.fixture
def start_spectating(roll_b, connection_id, connection_id_b, session_id, client_notifier):
    client_notifier.clear(connection_id)
    client_notifier.clear(connection_id_b)
    yield mediator.send(StartSpectatingCommand(session_id))


@pytest.fixture
def stop_spectating(start_spectating, connection_id, connection_id_b, session_id, client_notifier):
    client_notifier.clear(connection_id)
    client_notifier.clear(connection_id_b)
    yield mediator.send(StopSpectatingCommand(session_id))


class Case:

    def __init__(self) -> None:
        self.websocket_store = infrastructure_instances[IWebsocketConnectionStore]
        self.connection_id = None
        self.session_id = None
        self.second_connection_id = None
        self.second_session_id = None
        self.second_nickname = None

    def with_connection(self):
        self.connection_id = mediator.send(CreateConnectionCommand(uuid.uuid4())).connection_id
        return self.connection_id
    
    def with_destroyed_connection(self):
        if self.connection_id is None:
            self.with_connection()
        mediator.send(DestroyConnectionCommand(self.connection_id))

    def with_session(self):
        if self.connection_id is None:
            self.with_connection()
        self.session_id = mediator.send(CreateSessionIdCommand(self.connection_id))
        return self.session_id

    def with_invalid_session(self):
        if self.connection_id is None:
            self.with_connection()
        self.session_id = mediator.send(SetSessionIdCommand(self.connection_id, 'badSessionId'))

    def with_nickname(self, nickname):
        mediator.send(SetNicknameCommand(self.session_id, '', nickname))
        self.nickname = nickname
        return self.nickname

    def with_invalid_nickname(self, session_id):
        self.nickname = mediator.send(SetNicknameCommand(session_id, '', ''))
        return self.nickname

    def with_game(self, session_id=None, game_id=None):
        if session_id is None:
            if self.session_id is None:
                session_id = self.with_session()
            else:
                session_id = self.session_id
        if game_id is None:
            self.game_id = mediator.send(CreateGameCommand(session_id)).id
        else:
            self.game_id = mediator.send(JoinGameCommand(session_id, game_id)).id
        return self.game_id

    def with_invalid_game(self, session_id=None):
        if session_id is None:
            session_id = self.with_session()
        mediator.send(JoinGameCommand(session_id, 'badGameId'))
        self.game_id = 'badGameId'

    def with_second_connection(self):
        self.second_connection_id = mediator.send(CreateConnectionCommand(uuid.uuid4())).connection_id
        return self.second_connection_id

    def with_second_session(self):
        if self.second_connection_id is None:
            self.with_second_connection()
        self.second_session_id = mediator.send(CreateSessionIdCommand(self.second_connection_id))
        return self.second_session_id
    
    def with_second_nickname(self, nickname):
        mediator.send(SetNicknameCommand(self.second_session_id, '', nickname))
        self.second_nickname = nickname
        return self.second_nickname

    def with_timed_out_session(self):
        mediator.send(CheckSessionTimeoutCommand(self.session_id))
        return self.session_id

    def with_new_round(self):
        mediator.send(NewRoundCommand(self.session_id))

    def with_rolled_dice(self):
        mediator.send(RollDiceCommand(self.session_id))

    def with_second_rolled_dice(self):
        mediator.send(RollDiceCommand(self.second_session_id))

    
@pytest.fixture
def given_user_is_new() -> Case:
    case = Case()
    yield case


@pytest.fixture
def given_user_is_connected() -> Case:
    case = Case()
    case.with_connection()
    yield case

@pytest.fixture
def given_user_has_session() -> Case:
    case = Case()
    case.with_session()
    yield case

@pytest.fixture
def given_user_has_game() -> Case:
    case = Case()
    case.with_game()
    yield case

@pytest.fixture
def given_session_is_pending_timeout() -> Case:
    case = Case()
    case.with_session()
    case.with_destroyed_connection()
    yield case

@pytest.fixture
def given_two_player_game() -> Case:
    case = Case()
    case.with_session()
    case.with_nickname('AVERAGE_JOE')
    case.with_second_session()
    case.with_second_nickname('ABOVE_AVERAGE_JOE')
    case.with_game()
    case.with_game(session_id=case.second_session_id, game_id=case.game_id)
    yield case
