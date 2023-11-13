import 'dart:async';
import 'dart:convert';
import 'package:death_dice/model/game_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:web_socket_channel/io.dart';

class GameCache {
  String? sessionId;
  String? gameId;
  GameState? gameState;
}

class WebsocketInteractor {
  bool isInitialised = false;
  bool isConnected = false;
  GameCache cache = GameCache();
  Function(GameState)? gameStateCallback;
  Function()? disconnectCallback;
  late final String gatewayUrl;
  late Function(String) errorCallback;
  late IOWebSocketChannel channel;
  late Completer<bool> sessionCompleter;
  late Completer<bool> nicknameCompleter;
  late Completer<bool> gameCompleter;

  WebsocketInteractor();

  Future init() async {
    if (isInitialised) {
      return;
    }
    await dotenv.load(fileName: ".env");
    gatewayUrl = dotenv.env['WEBSOCKET_URL']!;
    isInitialised = true;
  }

  void connect(Function(String) func) {
    debugPrint('connecting');
    errorCallback = func;
    channel = IOWebSocketChannel.connect(Uri.parse(gatewayUrl));
    channel.stream.listen(_onMessage, onDone: _onDone);
    isConnected = true;
  }

  void _onMessage(dynamic message) {
    Map map = json.decode(message);
    if (map["message"] == "Internal server error") {
      errorCallback(map["message"]);
    }
    if (map["message"] == "Forbidden") {
      errorCallback(map["message"]);
      return;
    }

    var action = GameAction.values.byName(map['action']);
    debugPrint('action: $action');

    if (action == GameAction.setSession) {
      if (map.containsKey('error')) {
        sessionCompleter.complete(false);
        return;
      }
    }

    if (map.containsKey('error')) {
      errorCallback(map['error']);
      return;
    }

    if (action == GameAction.getSession) {
      cache.sessionId = map['data'];
      sessionCompleter.complete(true);
    } else if (action == GameAction.setNickname) {
      nicknameCompleter.complete(true);
    } else if (action == GameAction.joinGame) {
      cache.gameId = map['data'];
      gameCompleter.complete(true);
    } else if (action == GameAction.gameState) {
      cache.gameState = GameState.fromJson(map['data']);
      if (gameStateCallback != null) {
        gameStateCallback!(cache.gameState!);
      }
    } else if (action == GameAction.destroySession) {
      cache.sessionId = null;
      sessionCompleter.complete(true);
    }
  }

  void _onDone() {
    if (!isConnected) {
      if (disconnectCallback != null) {
        disconnectCallback!();
      }
      return;
    }
    connect(errorCallback);
    if (cache.sessionId != null) {
      setSession(cache.sessionId!);
    }

    debugPrint('connection closed');
  }

  void listenToGameState(Function(GameState) func) {
    gameStateCallback = func;
  }

  void listenToDisconnect(Function() func) {
    disconnectCallback = func;
  }

  void close() {
    debugPrint("Closing websocket");
    cache = GameCache();
    isConnected = false;
    channel.sink.close();
  }

  Future<bool> setSession(String desiredSessionId) {
    debugPrint("Setting session");
    sessionCompleter = Completer();
    var message =
        "{\"action\": \"setSession\", \"data\": {\"sessionId\": \"$desiredSessionId\"}}";
    channel.sink.add(message);
    return sessionCompleter.future;
  }

  Future<bool> getSession() {
    debugPrint("Getting session");
    sessionCompleter = Completer();
    var message = "{\"action\": \"getSession\"}";
    channel.sink.add(message);
    return sessionCompleter.future;
  }

  Future<bool> createPlayer(String name, String accountId) {
    debugPrint("Creating player");
    nicknameCompleter = Completer();
    var message = {
      "action": "setNickname",
      "data": {
        "sessionId": cache.sessionId,
        "nickname": name,
        "accountId": accountId,
      }
    };
    channel.sink.add(jsonEncode(message));
    return nicknameCompleter.future;
  }

  Future<bool> createGame() {
    debugPrint("Creating game");
    gameCompleter = Completer();
    var message = {
      "action": "createGame",
      "data": {
        "sessionId": cache.sessionId,
      }
    };
    channel.sink.add(jsonEncode(message));
    return gameCompleter.future;
  }

  Future<bool> joinGame(String code) {
    debugPrint("Joining game");
    gameCompleter = Completer();
    var message = {
      "action": "joinGame",
      "data": {
        "sessionId": cache.sessionId,
        "gameId": code,
      }
    };
    channel.sink.add(jsonEncode(message));
    return gameCompleter.future;
  }

  Future<bool> destroySession(String accountId) {
    debugPrint("Destroying player");
    sessionCompleter = Completer();
    var message =
        "{\"action\": \"destroySession\", \"data\": {\"sessionId\": \"${cache.sessionId}\"}}";
    channel.sink.add(message);
    return sessionCompleter.future;
  }

  void newRound() {
    debugPrint("New round");
    var message =
        "{\"action\": \"newRound\", \"data\": {\"sessionId\": \"${cache.sessionId}\"}}";
    channel.sink.add(message);
  }

  void rollDice() {
    debugPrint("Rolling dice");
    var message =
        "{\"action\": \"rollDice\", \"data\": {\"sessionId\": \"${cache.sessionId}\"}}";
    channel.sink.add(message);
  }

  void startSpectating() {
    debugPrint("Starting spectating");
    var message =
        "{\"action\": \"startSpectating\", \"data\": {\"sessionId\": \"${cache.sessionId}\"}}";
    channel.sink.add(message);
  }

  void stopSpectating() {
    debugPrint("Stopping spectating");
    var message =
        "{\"action\": \"stopSpectating\", \"data\": {\"sessionId\": \"${cache.sessionId}\"}}";
    channel.sink.add(message);
  }
}
