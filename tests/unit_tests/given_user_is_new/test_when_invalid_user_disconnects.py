
import pytest
from domain_models.commands import DestroyConnectionCommand
from domain_services.interfaces import WebsocketConnectionNotFoundException
from mediator import mediator


@pytest.fixture
def case(given_user_is_new):
    yield given_user_is_new


def test_it_errors_if_not_found(case):
  with pytest.raises(WebsocketConnectionNotFoundException):
    mediator.send(DestroyConnectionCommand(''))
  