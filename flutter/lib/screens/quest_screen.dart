import 'package:death_dice/data_access/analytics_interactor.dart';
import 'package:death_dice/data_access/cognito_interactor.dart';
import 'package:death_dice/model/admin_config.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';

final getIt = GetIt.instance;

class QuestScreen extends StatefulWidget {
  final String accountId;
  final String username;

  const QuestScreen({
    super.key,
    required this.accountId,
    required this.username,
  });

  @override
  State<QuestScreen> createState() => _QuestScreenState();
}

class _QuestScreenState extends State<QuestScreen> {
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  final AnalyticsInteractor analytics = getIt<AnalyticsInteractor>();

  bool isLoading = false;
  int numTotal = 3;
  int numCompleted = 0;
  AdminConfig? adminConfig;

  @override
  void initState() {
    isLoading = true;
    analytics
        .init()
        .then((_) => analytics.getConfig(widget.username))
        .then((value) {
      adminConfig = value;
      numCompleted = countCompletedQuests(adminConfig!);
      setState(() => isLoading = false);
    });
    super.initState();
  }

  int countCompletedQuests(AdminConfig adminConfig) {
    return (adminConfig.isEggOneFound ? 1 : 0) +
        (adminConfig.isEggTwoFound ? 1 : 0) +
        (adminConfig.isEggThreeFound ? 1 : 0) +
        (adminConfig.isEggFourFound ? 1 : 0);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).backgroundColor,
      appBar: buildAppBar(),
      body: buildBody(),
    );
  }

  AppBar buildAppBar() {
    return AppBar(
      title: const Text('Quests'),
      backgroundColor: Theme.of(context).primaryColor,
    );
  }

  Widget buildBody() {
    if (isLoading) {
      return Center(
        child: SizedBox(
          width: 50,
          height: 50,
          child:
              CircularProgressIndicator(color: Theme.of(context).primaryColor),
        ),
      );
    }

    var listTiles = <ListTile>[];
    listTiles.add(createTile("Find Egg #1", 0, adminConfig!.isEggOneFound));
    listTiles.add(createTile("Find Egg #2", 0, adminConfig!.isEggTwoFound));
    listTiles.add(createTile("Find Egg #3", 2, adminConfig!.isEggThreeFound));
    listTiles.add(createTile("Find Egg #4", 3, adminConfig!.isEggFourFound));

    return ListView(children: listTiles);
  }

  ListTile createTile(
      String text, int numQuestsNeededToReveal, bool isCompleted) {
    if (isCompleted) {
      return createCompletedTile(text);
    }
    if (numCompleted >= numQuestsNeededToReveal) {
      return createIncompleteTile(text);
    }
    return createHiddenTile(numQuestsNeededToReveal);
  }

  ListTile createCompletedTile(String text) {
    return ListTile(
      title: Text(text,
          style: TextStyle(
              color: Colors.grey.shade400,
              decoration: TextDecoration.lineThrough)),
      trailing: const Icon(Icons.check),
    );
  }

  ListTile createIncompleteTile(String text) {
    return ListTile(
      title: Text(text),
    );
  }

  ListTile createHiddenTile(int numQuestsNeededToReveal) {
    var questsMore = numQuestsNeededToReveal - numCompleted;
    var plural = questsMore == 1 ? 'quest' : 'quests';
    return ListTile(
      title: Text("Complete $questsMore more $plural to reveal",
          style: TextStyle(
            color: Colors.grey.shade400,
          )),
    );
  }
}
