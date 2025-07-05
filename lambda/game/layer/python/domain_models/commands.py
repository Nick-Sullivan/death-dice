
from dataclasses import dataclass
from typing import Dict, List

from .game_state import GameState, Roll
from .interfaces import ITransaction


@dataclass
class CreateConnectionCommand:
    connection_id: int


@dataclass
class DestroyConnectionCommand:
    connection_id: str


@dataclass
class DestroySessionCommand:
    session_id: str


@dataclass
class GetSessionIdCommand:
    connection_id: str


@dataclass
class CreateSessionCommand:
    connection_id: str
    transaction: ITransaction


@dataclass
class CreateSessionIdCommand:
    connection_id: str


@dataclass
class SetSessionIdCommand:
    connection_id: str
    session_id: str


@dataclass
class NotifyConnectionsCommand:
    connection_ids: List[str]
    action: str
    data: str = None
    error: str = None


@dataclass
class NotifySessionsCommand:
    session_ids: List[str]
    action: str
    data: str = None
    error: str = None


@dataclass
class NotifyGameStateCommand:
    game: GameState


@dataclass
class SetNicknameCommand:
    session_id: str
    account_id: str
    nickname: str


@dataclass
class CreateGameCommand:
    session_id: str


@dataclass
class JoinGameCommand:
    session_id: str
    game_id: str


@dataclass
class NewRoundCommand:
    session_id: str


@dataclass
class RollDiceCommand:
    session_id: str


@dataclass
class CalculateIndividualResultCommand:
    rolls: List[Roll]
    is_mr_eleven: bool


@dataclass
class CalculateGroupResultCommand:
    player_rolls: Dict[str, List[Roll]]
    mr_eleven: str


@dataclass
class FinishRoundCommand:
    game: GameState


@dataclass
class StartSpectatingCommand:
    session_id: str


@dataclass
class StopSpectatingCommand:
    session_id: str


@dataclass
class CheckSessionTimeoutCommand:
    session_id: str


@dataclass
class MarkSessionAsPendingCommand:
    session_id: str
    transaction: ITransaction


@dataclass
class MarkSessionAsConnectedCommand:
    connection_id: str
    session_id: str
    transaction: ITransaction


@dataclass
class MarkPlayerAsPendingCommand:
    session_id: str
    game_id: str
    transaction: ITransaction
    

@dataclass
class MarkPlayerAsConnectedCommand:
    session_id: str
    game_id: str
    transaction: ITransaction


@dataclass
class LeaveGameCommand:
    session_id: str
    game_id: str
    transaction: ITransaction
    

@dataclass
class DecideDiceValuesCommand:
    prev_rolls: List[Roll]
    win_counter: int
    player_name: str
    