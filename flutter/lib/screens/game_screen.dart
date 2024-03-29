import 'package:death_dice/data_access/websocket_interactor.dart';
import 'package:death_dice/model/game_state.dart';
import 'package:death_dice/screens/home_screen.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
final getIt = GetIt.instance;

class GameScreen extends StatefulWidget {
  const GameScreen({super.key});

  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  final WebsocketInteractor websocket = getIt<WebsocketInteractor>();
  late final String gameId;
  late final String playerId;
  bool isRoundComplete = false;
  bool isSpectator = false;
  bool isTurnComplete = false;
  bool isLoading = false;
  
  @override
  void initState() {
    playerId = websocket.cache.sessionId!;
    gameId = websocket.cache.gameState!.gameId;
    onGameStateUpdated(websocket.cache.gameState!);
    websocket.listenToGameState(onGameStateUpdated);
    websocket.listenToDisconnect(onDisconnected);
    super.initState();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).backgroundColor,
      body: Center(
        child: SingleChildScrollView(
          child: Column(
            children: <Widget>[
              Padding(
                padding: const EdgeInsets.all(15),
                child: buildGameCode(),
              ),
              Padding(
                padding: const EdgeInsets.only(top: 30, left: 15, right: 15, bottom: 30),
                child: buildDisconnectButton(),
              ),
              Padding(
                padding: const EdgeInsets.only(bottom: 30),
                child: buildToggleSpectatingButton(),
              ),
              Padding(
                padding: const EdgeInsets.only(bottom: 30),
                child: buildNewRoundButton(),
              ),
              Padding(
                padding: const EdgeInsets.only(left: 15, right: 15),
                child: buildRollDiceButton(),
              ),
              Padding(
                padding: const EdgeInsets.only(top: 30, left: 15, right: 15),
                child: buildGameDisplay(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget buildGameCode() {
    return Text(
      gameId,
      style: const TextStyle(fontStyle: FontStyle.italic),
    );
  }

  Widget buildDisconnectButton() {
    return Container(
      height: 50,
      width: 250,
      decoration: BoxDecoration(
        color: Theme.of(context).primaryColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: TextButton(
        onPressed: () {
          disconnect();
        },
        child: const Text(
          'Disconnect',
          style: TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildToggleSpectatingButton() {

    var enabled = !isLoading;
    return Container(
      height: 50,
      width: 250,
      decoration: BoxDecoration(
        color: enabled ? Theme.of(context).primaryColor : Colors.grey,
        borderRadius: BorderRadius.circular(20),
      ),
      child: TextButton(
        onPressed: enabled ? () async {
          setState(() => isLoading = true);
          isSpectator ? websocket.stopSpectating() : websocket.startSpectating();
        } : null,
        child: Text(
          isSpectator ? 'Stop Spectating' : 'Spectate',
          style: const TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildNewRoundButton() {
    var enabled = isRoundComplete && !isLoading && !isSpectator;
    return Container(
      height: 50,
      width: 250,
      decoration: BoxDecoration(
        color: enabled ? Theme.of(context).primaryColor : Colors.grey,
        borderRadius: BorderRadius.circular(20),
      ),
      child: TextButton(
        onPressed: enabled ? () async {
          setState(() => isLoading = true);
          websocket.newRound();
        } : null,
        child: const Text(
          'New round',
          style: TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildRollDiceButton() {
    var enabled = !isRoundComplete && !isTurnComplete && !isLoading && !isSpectator;
    return Container(
      height: 50,
      width: 250,
      decoration: BoxDecoration(
        color: enabled ? Theme.of(context).primaryColor : Colors.grey,
        borderRadius: BorderRadius.circular(20),
      ),
      child: TextButton(
        onPressed: enabled ? () async {
          setState(() => isLoading = true);
          websocket.rollDice();
        } : null,
        child: const Text(
          'Roll dice',
          style: TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildGameDisplay() {
    var gameState = websocket.cache.gameState!;
    var text = "";
    for (var player in gameState.players){
      var values = <String>[];
      for (var roll in player.diceRolls){
        values.add(roll.value.toString());
      }
      text += "${player.nickname}(${player.winCount}): ${values.join(',')} ${player.rollResult!.value}\r\n";
    }

    for (var spectator in gameState.spectators){
      text += "(Spectator) ${spectator.nickname}\r\n";
    }

    return Text(
      text,
      style: const TextStyle(fontStyle: FontStyle.italic),
    );
  }

  void onGameStateUpdated(GameState gamestate) {
    debugPrint('Game updated');
    isRoundComplete = gamestate.round.isComplete;

    isSpectator = gamestate.spectators.where((s) => s.id == playerId).isNotEmpty;
    if (!isSpectator){
      var player = gamestate.players.firstWhere((p) => p.id == playerId);
      isTurnComplete = player.isTurnFinished;
    }
    setState(() => isLoading = false);
  }

  void disconnect() async {
    await websocket.destroySession(playerId);
    websocket.close();
  }
  
  void onDisconnected() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const HomeScreen()),
    );
  }
}
