import 'package:death_dice/data_access/analytics_interactor.dart';
import 'package:death_dice/data_access/database_interactor.dart';
import 'package:death_dice/data_access/websocket_interactor.dart';
import 'package:death_dice/model/admin_config.dart';
import "dart:math";
import 'package:death_dice/model/constants.dart';
import 'package:death_dice/model/game_state.dart';
import 'package:death_dice/screens/account_screen.dart';
import 'package:death_dice/screens/admin_screen.dart';
import 'package:death_dice/screens/game_screen.dart';
import 'package:death_dice/screens/log_in_screen.dart';
import 'package:death_dice/screens/quest_judging_screen.dart';
import 'package:death_dice/screens/quest_screen.dart';
import 'package:death_dice/screens/rule_screen.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';

import '../model/account.dart';

final getIt = GetIt.instance;

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final DatabaseInteractor database = getIt<DatabaseInteractor>();
  final WebsocketInteractor websocket = getIt<WebsocketInteractor>();
  final AnalyticsInteractor analytics = getIt<AnalyticsInteractor>();
  final AssetImage background =
      const AssetImage("assets/images/can-in-forest.jpg");
  final AssetImage canLogo = const AssetImage("assets/images/can-logo.png");
  late final TextEditingController nameController;
  late final TextEditingController gameCodeController;
  late final String username;
  late final Account account;
  AdminConfig? adminConfig;
  bool isLoading = true;
  String playerId = "default";

  @override
  void dispose() {
    nameController.dispose();
    gameCodeController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    nameController = TextEditingController(text: createRandomName());
    gameCodeController = TextEditingController();
    database
        .init()
        .then((_) => initVariablesFromDatabase())
        .then((_) => websocket.init())
        .then((_) => connect())
        .then((_) => analytics.init())
        .then((_) => analytics.getConfig(username))
        .then((config) {
          adminConfig = config;
        })
        .then((_) => isLoading = false)
        .then((_) => setState(() {}));
    super.initState();
  }

  void initVariablesFromDatabase() {
    var accountId = database.read(accountIdKey);
    var accountEmail = database.read(accountEmailKey);
    account = Account(accountId, accountEmail);
    username = database.read(usernameKey);
    if (database.containsKey(playerIdKey)) {
      playerId = database.read(playerIdKey);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false,
      backgroundColor: Theme.of(context).backgroundColor,
      appBar: buildAppBar(),
      body: Container(
        constraints: const BoxConstraints.expand(),
        decoration: BoxDecoration(
            image: DecorationImage(
          alignment: Alignment.bottomCenter,
          colorFilter: ColorFilter.mode(
              Colors.black.withOpacity(0.5), BlendMode.dstATop),
          fit: BoxFit.cover,
          image: background,
        )),
        child: SingleChildScrollView(
          child: Column(
            children: <Widget>[
              // Padding(
              //   padding: const EdgeInsets.only(top: 30.0, bottom: 30.0),
              //   child: buildLogo(),
              // ),
              Padding(
                padding: const EdgeInsets.only(
                    top: 30, left: 15, right: 15, bottom: 30),
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
      ),
    );
  }

  AppBar buildAppBar() {
    return AppBar(
      title: const Text('Death Dice'),
      backgroundColor: Theme.of(context).primaryColor,
      actions: [
        PopupMenuButton(
          itemBuilder: (_) {
            var popMenus = [
              const PopupMenuItem(
                value: 0,
                child: Text("Account"),
              ),
              const PopupMenuItem(
                value: 1,
                child: Text("Rules"),
              ),
              const PopupMenuItem(
                value: 2,
                child: Text("Log out"),
              ),
            ];
            if (account.email == adminEmail) {
              popMenus.add(const PopupMenuItem(
                value: 3,
                child: Text("Admin settings"),
              ));
            }
            var isJudgingEnabled = (account.email == adminEmail &&
                    adminConfig?.isNickQuestJudge == true) ||
                (account.email == mattsEmail &&
                    adminConfig?.isMattQuestJudge == true);
            if (isJudgingEnabled) {
              popMenus.add(PopupMenuItem(
                value: 4,
                child: Text("Quest judging",
                    style: TextStyle(
                        color: Colors.blue.shade400,
                        fontWeight: FontWeight.bold)),
              ));
            }

            var isQuestingEnabled = (account.email == adminEmail &&
                    adminConfig?.isNickQuestTarget == true) ||
                (account.email == mattsEmail &&
                    adminConfig?.isMattQuestTarget == true) ||
                (account.email == angusesEmail &&
                    adminConfig?.isAngusQuestTarget == true);
            if (isQuestingEnabled) {
              popMenus.add(PopupMenuItem(
                value: 5,
                child: Text("Quests",
                    style: TextStyle(
                        color: Colors.red.shade400,
                        fontWeight: FontWeight.bold)),
              ));
            }

            return popMenus;
          },
          onSelected: ((value) {
            if (value == 0) {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => AccountScreen(
                          accountId: account.id, username: username)));
            }
            if (value == 1) {
              Navigator.push(context,
                  MaterialPageRoute(builder: (context) => RuleScreen()));
            }
            if (value == 2) {
              database.delete(usernameKey);
              database.delete(passwordKey);
              database.delete(accountIdKey);
              Navigator.pushReplacement(context,
                  MaterialPageRoute(builder: (context) => const LogInScreen()));
            }
            if (value == 3) {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => AdminScreen(
                          accountId: account.id, username: username)));
            }
            if (value == 4) {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => QuestJudgingScreen(
                          accountId: account.id, username: username)));
            }
            if (value == 5) {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => QuestScreen(
                          accountId: account.id, username: username)));
            }
          }),
        ),
      ],
    );
  }

  Widget buildLogo() {
    var image = isLoading
        ? CircularProgressIndicator(color: Theme.of(context).primaryColor)
        : Image(image: canLogo);
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
        labelStyle: TextStyle(color: Colors.black),
        labelText: 'Name',
        fillColor: Color(0xaabebfc3),
        filled: true,
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
        onPressed: isLoading
            ? null
            : () async {
                setState(() => isLoading = true);
                createGame();
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
        Expanded(
            flex: 1,
            child: TextField(
              controller: gameCodeController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelStyle: TextStyle(color: Colors.black),
                labelText: 'Game code',
                fillColor: Color(0xaabebfc3),
                filled: true,
              ),
              enabled: !isLoading,
            )),
        Expanded(
            flex: 1,
            child: Container(
              height: 50,
              width: 250,
              decoration: BoxDecoration(
                color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
                borderRadius: BorderRadius.circular(20),
              ),
              child: TextButton(
                onPressed: isLoading
                    ? null
                    : () async {
                        setState(() => isLoading = true);
                        joinGame();
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

  void connect() async {
    websocket.connect(onError);
    websocket.listenToGameState(onGameState);
    var success = await websocket.setSession(playerId);
    if (success) {
      playerId = websocket.cache.sessionId!;
      return;
    }

    await websocket.getSession();
    playerId = websocket.cache.sessionId!;
    await database.write(playerIdKey, playerId);
  }

  void createGame() async {
    await websocket.createPlayer(nameController.text, account.id);
    await websocket.createGame();
  }

  void joinGame() async {
    await websocket.createPlayer(nameController.text, account.id);
    await websocket.joinGame(gameCodeController.text);
  }

  void onGameState(GameState gamestate) {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const GameScreen()),
    );
  }

  void onError(String error) {
    debugPrint(error);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    // websocket.close();
    setState(() => isLoading = false);
  }

  String createRandomName() {
    const list = [
      'A Big Carrot 🥕',
      'A Grapist 🍇',
      'aii yaaa',
      'Big Boi 🍆',
      'Biggus Dickus',
      'bongz4lyfe',
      'Brett Maher',
      'Deez Nuts',
      'Definitely not Roib',
      'Dice Lover',
      'Dirk Cuckold',
      'Dong Swanson',
      'Dr Roib',
      'Eggies 🥚🥚🥚',
      'Girthy Baby 👶',
      'Hanz Shuttlecock',
      'Im so thirsty',
      'Jam Fucker',
      'Lets fuck this pig',
      'Like an Ogre 🧅',
      'Magician',
      'Mike Rotch',
      'Moist Panda',
      'Mr Illeven 🤢',
      'Mr Twelve',
      'Poop 💩',
      'Ready for a drink 🍺',
      'Rimmed by a redneck',
      'Roib',
      'Schubert the Cat',
      'Shower Lover',
      'Sodomy Wizard',
      'Spread by an inbred',
      'Thicc',
      'Uncomfortable Horse',
      'Wet Boy',
      'Wing Lover 🐔',
      'Wish Purchaser',
      'you up?',
    ];

    return list[Random().nextInt(list.length)];
  }
}
