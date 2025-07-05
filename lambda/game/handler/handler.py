import api


def connect(event, context):
    return api.connect(event, context)


def create_game(event, context):
    return api.create_game(event, context)


def disconnect(event, context):
    return api.disconnect(event, context)


def get_session(event, context):
    return api.get_session(event, context)


def destroy_session(event, context):
    return api.destroy_session(event, context)


def heartbeat(event, context):
    return {'statusCode': 200}


def join_game(event, context):
    return api.join_game(event, context)


def new_round(event, context):
    return api.new_round(event, context)


def roll_dice(event, context):
    return api.roll_dice(event, context)


def set_nickname(event, context):
    return api.set_nickname(event, context)


def set_session(event, context):
    return api.set_session(event, context)


def start_spectating(event, context):
    return api.start_spectating(event, context)


def stop_spectating(event, context):
    return api.stop_spectating(event, context)


def check_session_timeout(event, context):
    return api.check_session_timeout(event, context)


if __name__ == '__main__':
    import json
    import sys
    func_name = sys.argv[1]
    connection_id = 'abcd-efgh'
    session_id = '5650893e-6bd8-45ad-baab-041f5e9c81c6'
    if func_name == 'connect':
        response = connect({
            'requestContext': {
                'connectionId': connection_id
            }
        }, None)
    if func_name == 'create_game':
        create_game({
        'requestContext': {
            'connectionId': connection_id
        },
            'body': json.dumps({'data': {
                'sessionId': session_id
            }})
        }, None)
    if func_name == 'disconnect':
        disconnect({
            'requestContext': {
                'connectionId': connection_id
            },
        }, None)
    if func_name == 'get_session':
        get_session({
            'requestContext': {
                'connectionId': connection_id
            },
        }, None)
    if func_name == 'destroy_session':
        destroy_session({
            'requestContext': {
                'connectionId': connection_id
            },
            'body': json.dumps({'data': {
                'sessionId': session_id
            }})
        }, None)
    if func_name == 'join_game':
        join_game({
            'requestContext': {
                'connectionId': connection_id
            },
            'body': json.dumps({'data': {
                'gameId': 'KHHF',
                'sessionId': session_id
            }})
        }, None)
    if func_name == 'new_round':
        new_round({
            'requestContext': {
                'connectionId': connection_id
            },
            'body': json.dumps({'data': {
                'sessionId': session_id
            }})
        }, None)
    if func_name == 'roll_dice':
        roll_dice({
            'requestContext': {
                'connectionId': connection_id
            },
            'body': json.dumps({'data': {
                'sessionId': session_id
            }})
        }, None)
    if func_name == 'set_nickname':
        set_nickname({
            'requestContext': {
                'connectionId': connection_id
            },
            'body': json.dumps({'data': {
                'sessionId': session_id,
                'nickname': 'nick_name',
            }})
        }, None)
    if func_name == 'set_session':
        set_session({
            'requestContext': {
                'connectionId': connection_id
            },
            'body': json.dumps({'data': {
                'sessionId': session_id,
            }})
        }, None)
    if func_name == 'start_spectating':
        start_spectating({
            'requestContext': {
                'connectionId': connection_id
            },
            'body': json.dumps({'data': {
                'sessionId': session_id,
            }})
        }, None)
    if func_name == 'stop_spectating':
        stop_spectating({
            'requestContext': {
                'connectionId': connection_id
            },
            'body': json.dumps({'data': {
                'sessionId': session_id,
            }})
        }, None)
