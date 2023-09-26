import os

import boto3
from domain_services.interfaces import (
    IClientNotifier,
    IEventPublisher,
    IGameStore,
    ISessionStore,
    ITransactionWriter,
    IWebsocketConnectionStore,
)

is_local = os.environ.get('IS_LOCAL') == 'True'

if is_local:
    from infrastructure.local import (
        ClientNotifier,
        EventPublisher,
        GameStore,
        SessionStore,
        TransactionWriter,
        WebsocketConnectionStore,
    )
    infrastructure_instances = {
        IClientNotifier: ClientNotifier(),
        IEventPublisher: EventPublisher(),
        IGameStore: GameStore(),
        ISessionStore: SessionStore(),
        ITransactionWriter: TransactionWriter(),
        IWebsocketConnectionStore: WebsocketConnectionStore(),
    }
else:
    from infrastructure.cloud import (
        ClientNotifier,
        EventPublisher,
        GameStore,
        SessionStore,
        TransactionWriter,
        WebsocketConnectionStore,
    )

    session = boto3.Session()
    db_client = session.client('dynamodb')
    infrastructure_instances = {
        IClientNotifier: ClientNotifier(session.client(
            'apigatewaymanagementapi',
            endpoint_url=os.environ['GATEWAY_URL'].replace('wss', 'https')
        )),
        IEventPublisher: EventPublisher(session.client('events'), os.environ['PROJECT']),
        IGameStore: GameStore(db_client, os.environ['PROJECT']),
        ISessionStore: SessionStore(db_client, os.environ['PROJECT']),
        ITransactionWriter: TransactionWriter(db_client),
        IWebsocketConnectionStore: WebsocketConnectionStore(db_client, os.environ['WEBSOCKET_TABLE_NAME']),
    }
    