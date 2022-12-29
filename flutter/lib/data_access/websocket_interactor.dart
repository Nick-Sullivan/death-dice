import 'dart:convert';
import 'package:death_dice/model/game_state.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:web_socket_channel/io.dart';

class GameCache {
  String? playerId;
  String? gameId;
  GameState? gameState;
}

class WebsocketInteractor {
  bool isInitialised = false;
  late final String gatewayUrl;
  late IOWebSocketChannel channel;
  Map<GameAction, Function(Map)> actionDispatch = <GameAction, Function(Map)>{};
  Map<GameAction, Function(Map)> errorDispatch = <GameAction, Function(Map)>{};
  GameCache cache = GameCache();

  WebsocketInteractor();

  Future init() async {
    if (isInitialised){
      return;
    }
    await dotenv.load(fileName: ".env");
    gatewayUrl = dotenv.env['WEBSOCKET_URL']!;
    isInitialised = true;
  }

  void connect() {
    channel = IOWebSocketChannel.connect(Uri.parse(gatewayUrl));
    channel.stream.listen(_listen);
  }

  void _listen(dynamic message){
    Map map = json.decode(message);
    var action = GameAction.values.byName(map['action']);

    if (map.containsKey('error')){
      if (errorDispatch.containsKey(action)){
        var func = errorDispatch[action]!;
        func(map);
      }
      return;
    }

    if (actionDispatch.containsKey(action)){
      var func = actionDispatch[action]!;
      func(map);
    }
  }

  void clearListeners(){
    actionDispatch = <GameAction, Function(Map)>{};
    errorDispatch = <GameAction, Function(Map)>{};
  }

  void listenToPlayerId(Function(String) func){
    actionDispatch[GameAction.setNickname] = (message) {
      cache.playerId = message['data']['playerId'];
      func(cache.playerId!);
    };
  }

  void listenToGameId(Function(String) func){
    actionDispatch[GameAction.joinGame] = (message) {
      cache.gameId = message['data'];
      func(cache.gameId!);
    };
  }

  void listenToGameError(Function(String) func){
    errorDispatch[GameAction.joinGame] = (message) {
      var error = message['error'];
      func(error);
    };
  }

  void listenToGameState(Function(GameState) func){
    actionDispatch[GameAction.gameState] = (message) {
      cache.gameState = GameState.fromJson(message['data']);
      func(cache.gameState!);
    };
  }

  void close() {
    channel.sink.close();
    cache = GameCache();
  }

  void createPlayer(String name) {
    var message = "{\"action\": \"setNickname\", \"data\": \"$name\"}";
    channel.sink.add(message);
  }

  void createGame() {
    var message = "{\"action\": \"createGame\"}";
    channel.sink.add(message);
  }

  void joinGame(String code) {
    var message = "{\"action\": \"joinGame\", \"data\": \"$code\"}";
    channel.sink.add(message);
  }

  void newRound() {
    var message = "{\"action\": \"newRound\"}";
    channel.sink.add(message);
  }

  void rollDice() {
    var message = "{\"action\": \"rollDice\"}";
    channel.sink.add(message);
  }

}
