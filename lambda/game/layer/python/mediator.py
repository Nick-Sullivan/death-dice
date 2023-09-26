from dependency_injector import DependencyInjector
from domain_services.command_handlers import (
    CalculateGroupResultHandler,
    CalculateIndividualResultHandler,
    CheckSessionTimeoutHandler,
    CreateConnectionHandler,
    CreateGameHandler,
    CreateSessionHandler,
    CreateSessionIdHandler,
    DecideDiceValuesHandler,
    DestroyConnectionHandler,
    DestroySessionHandler,
    FinishRoundHandler,
    GetSessionIdHandler,
    JoinGameHandler,
    LeaveGameHandler,
    MarkPlayerAsConnectedHandler,
    MarkPlayerAsPendingHandler,
    MarkSessionAsConnectedHandler,
    MarkSessionAsPendingHandler,
    NewRoundHandler,
    NotifyConnectionsHandler,
    NotifyGameStateHandler,
    NotifySessionsHandler,
    RollDiceHandler,
    SetNicknameHandler,
    SetSessionIdHandler,
    StartSpectatingHandler,
    StopSpectatingHandler,
)
from domain_services.interfaces import IMediator
from infrastructure.infrastructure_provider import infrastructure_instances
from mediatr import Mediator

handlers = [
    CalculateGroupResultHandler,
    CalculateIndividualResultHandler,
    CheckSessionTimeoutHandler,
    CreateConnectionHandler,
    CreateGameHandler,
    CreateSessionHandler,
    CreateSessionIdHandler,
    DecideDiceValuesHandler,
    DestroyConnectionHandler,
    DestroySessionHandler,
    FinishRoundHandler,
    GetSessionIdHandler,
    JoinGameHandler,
    LeaveGameHandler,
    MarkPlayerAsConnectedHandler,
    MarkPlayerAsPendingHandler,
    MarkSessionAsConnectedHandler,
    MarkSessionAsPendingHandler,
    NewRoundHandler,
    NotifyConnectionsHandler,
    NotifyGameStateHandler,
    NotifySessionsHandler,
    RollDiceHandler,
    SetNicknameHandler,
    SetSessionIdHandler,
    StartSpectatingHandler,
    StopSpectatingHandler,
]


def handler_class_manager(handler_cls, is_behavior=False):
    obj = DependencyInjector.inject(handler_cls)
    return obj


mediator = Mediator(handler_class_manager=handler_class_manager)
for handler in handlers:
    Mediator.register_handler(handler)
    DependencyInjector.register_handler(handler)

DependencyInjector.register_dependency(IMediator, mediator)
for interface, instance in infrastructure_instances.items():
    DependencyInjector.register_dependency(interface, instance)
