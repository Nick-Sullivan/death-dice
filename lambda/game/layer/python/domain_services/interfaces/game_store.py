
from abc import ABC, abstractmethod
from domain_models import GameState
from .transaction_writer import ITransaction


class GameNotFoundException(Exception):
  pass


class IGameStore(ABC):
  
  @abstractmethod
  def create(self, item: GameState, transaction: ITransaction):
    pass

  @abstractmethod
  def get(self, id: str) -> GameState:
    pass

  @abstractmethod
  def set(self, item: GameState, transaction: ITransaction):
    pass

  @abstractmethod
  def delete(self, item: GameState, transaction: ITransaction):
    pass

  @abstractmethod
  def create_unique_game_id(self) -> str:
    pass

  @abstractmethod
  def is_valid_game_id(self, game_id: str) -> bool:
    pass