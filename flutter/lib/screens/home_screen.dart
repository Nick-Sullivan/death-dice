import 'package:death_dice/data_access/database_interactor.dart';
import 'package:death_dice/data_access/websocket_interactor.dart';
import 'package:death_dice/model/game_state.dart';
import 'package:death_dice/screens/game_screen.dart';
import 'package:death_dice/screens/log_in_screen.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
final getIt = GetIt.instance;

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final DatabaseInteractor database = getIt<DatabaseInteractor>();
  final WebsocketInteractor websocket = getIt<WebsocketInteractor>();
  late final TextEditingController nameController;
  late final TextEditingController gameCodeController;
  late bool isCreatingGame;
  bool isLoading = false;

  @override
  void dispose() {
    nameController.dispose();
    gameCodeController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    nameController = TextEditingController(text: 'Roib');
    gameCodeController = TextEditingController();
    database.init();
    websocket.init();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).backgroundColor,
      appBar: buildAppBar(),
      body: SingleChildScrollView(
        child: Column(
          children: <Widget>[
            Padding(
              padding: const EdgeInsets.only(top: 30.0, bottom: 30.0),
              child: buildLogo(),
            ),
            Padding(
              padding: const EdgeInsets.only(top: 0, left: 15, right: 15, bottom: 30),
              child: buildName(),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 30),
              child: buildNewGame(),
            ),
            Padding(
              padding: const EdgeInsets.only(left: 15, right: 15),
              child: buildJoinGame(),
            ),
          ],
        ),
      ),
    );
  }

  AppBar buildAppBar(){
    return AppBar(
      title: const Text('Death Dice'),
      backgroundColor: Theme.of(context).primaryColor,
      actions: [
        PopupMenuButton(
          itemBuilder: (_) {
            return [
              const PopupMenuItem(
                value: 0,
                child: Text("Log out"),
              ),
            ];
          },
          onSelected: ((value) {
            if (value == 0){
              database.delete('USERNAME');
              database.delete('PASSWORD');
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const LogInScreen())
              );
            }
          }),
        ),
      ],
    );
  }

  Widget buildLogo() {
    var image = isLoading
      ? CircularProgressIndicator(color: Theme.of(context).primaryColor)
      : const Image(image: AssetImage('assets/can-logo.png'));
    return Center(
      child: SizedBox(
        width: 150,
        height: 100,
        child: image,
      ),
    );
  }

  Widget buildName() {
    return TextField(
      controller: nameController,
      decoration: const InputDecoration(
        labelText: 'Name',
      ),
      enabled: !isLoading,
    );
  }

  Widget buildNewGame() {
    return Container(
      height: 50,
      width: 250,
      decoration: BoxDecoration(
        color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: TextButton(
        onPressed: isLoading ? null : () async {
          setState(() => isLoading = true);
          isCreatingGame = true;
          connect();
        },
        child: const Text(
          'New Game',
          style: TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildJoinGame() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Expanded(flex: 1, child: TextField(
          controller: gameCodeController,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            labelText: 'Game code',
          ),
          enabled: !isLoading,
        )),
        Expanded(flex: 1, child: Container(
          height: 50,
          width: 250,
          decoration: BoxDecoration(
            color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
            borderRadius: BorderRadius.circular(20),
          ),
          child: TextButton(
            onPressed: isLoading ? null : () async {
              setState(() => isLoading = true);
              isCreatingGame = false;
              connect();
            },
            child: const Text(
              'Join',
              style: TextStyle(color: Colors.white, fontSize: 25),
            ),
          ),
        ))
      ],
    );
  }

  void connect() {
    websocket.connect();
    websocket.listenToPlayerId(onPlayerCreated);
    websocket.listenToPlayerError(onError);
    websocket.listenToGameId(onGameJoined);
    websocket.listenToGameError(onError);
    websocket.listenToGameState(onGameStateUpdated);
    websocket.createPlayer(nameController.text);
  }
  
  void onPlayerCreated(String playerId) {
    debugPrint('Player ID set');
    if (isCreatingGame){
      websocket.createGame();
    } else {
      websocket.joinGame(gameCodeController.text);
    }
  }

  void onGameJoined(String gameId) {
    debugPrint('Game joined');
  }

  void onGameStateUpdated(GameState gamestate) {
    debugPrint('Game updated');
    websocket.clearListeners();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const GameScreen()),
    );

  }

  void onError(String error) {
    debugPrint(error);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(error))
    );
    websocket.close();
    setState(() => isLoading = false);
  }

}