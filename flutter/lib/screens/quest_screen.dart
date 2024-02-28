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
    return (adminConfig.areEggsFound ? 1 : 0) +
        (adminConfig.hasBulgarianBeenAsked ? 1 : 0) +
        (adminConfig.hasRandomBeenTongued ? 1 : 0) +
        (adminConfig.hasWestEndBeenOrdered ? 1 : 0) +
        (adminConfig.hasTantrumBeenThrown ? 1 : 0) +
        (adminConfig.hasElectricityBillCalled ? 1 : 0) +
        (adminConfig.isStrangerFoiledAgain ? 1 : 0) +
        (adminConfig.hasBupBeenDowed ? 1 : 0) +
        (adminConfig.hasVenuePlayedSteelPanther ? 1 : 0) +
        (adminConfig.hasHalfTimeSpeechInspired ? 1 : 0) +
        (adminConfig.isCrevatteWorn ? 1 : 0) +
        (adminConfig.isFingerRinged ? 1 : 0) +
        (adminConfig.areSexyClownsReal ? 1 : 0) +
        (adminConfig.isMagicGathered ? 1 : 0) +
        (adminConfig.isHotSauceConsumed ? 1 : 0) +
        (adminConfig.isArmpitFarted ? 1 : 0) +
        (adminConfig.isChronicRhinitusTreated ? 1 : 0) +
        (adminConfig.isCatchupOrganised ? 1 : 0) +
        (adminConfig.isMagicMikeRecreated ? 1 : 0) +
        (adminConfig.isHotDogEaten ? 1 : 0) +
        (adminConfig.isKettMaherInvited ? 1 : 0);
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
    listTiles.add(
        createTile("Find all the hidden eggs", 0, adminConfig!.areEggsFound));
    listTiles.add(createTile("Talk to a Bulgarian about DJ Juice", 0,
        adminConfig!.hasBulgarianBeenAsked));
    listTiles.add(createTile(
        "Get a random person to put a fake tongue in their mouth",
        0,
        adminConfig!.hasRandomBeenTongued));
    listTiles.add(createTile(
        "When you order food/drink, order a West End first (x5)",
        0,
        adminConfig!.hasWestEndBeenOrdered));
    listTiles.add(createTile(
        "If a bartender doesn't serve West End, throw a tantrum",
        0,
        adminConfig!.hasTantrumBeenThrown));
    listTiles.add(createTile(
        "Prank call someone at the bucks without them knowing, for 1 minute",
        0,
        adminConfig!.hasElectricityBillCalled));
    listTiles.add(createTile(
        "Get a stranger to say 'foiled', and when they do, say 'foiled again' and walk away",
        0,
        adminConfig!.isStrangerFoiledAgain));
    listTiles.add(createTile("Get a stranger to Dow your Bup (x5)", 0,
        adminConfig!.hasBupBeenDowed));
    listTiles.add(createTile("Get a venue to play Steel Panther", 0,
        adminConfig!.hasVenuePlayedSteelPanther));
    listTiles.add(createTile("Give a 2 minute rambling half-time speech", 1,
        adminConfig!.hasHalfTimeSpeechInspired));
    listTiles.add(createTile(
        "Put a crevatte on a stranger, but take a really long time. No laughing",
        2,
        adminConfig!.isCrevatteWorn));
    listTiles.add(createTile(
        "Get someone with an unsuspecting finger ring (x5)",
        3,
        adminConfig!.isFingerRinged));
    listTiles.add(createTile(
        "Debate a stranger that sexy clowns exist, your are arguing that they do",
        4,
        adminConfig!.areSexyClownsReal));
    listTiles.add(createTile("Beat 5 people at Magic the Gathering", 5,
        adminConfig!.isMagicGathered));
    listTiles.add(createTile("Consume a dab of extremely hot sauce", 6,
        adminConfig!.isHotSauceConsumed));
    listTiles.add(createTile(
        "Do a 10 second long armpit fart, or 30 in 30 seconds",
        7,
        adminConfig!.isArmpitFarted));
    listTiles.add(createTile(
        "Eat a hot dog from your sleeve while having a conversation",
        8,
        adminConfig!.isHotDogEaten));
    listTiles.add(createTile("Treat your chronic rhinitus (1 jar)", 9,
        adminConfig!.isChronicRhinitusTreated));
    listTiles.add(createTile(
        "Organise a catchup with someone you hate from your old job",
        10,
        adminConfig!.isCatchupOrganised));
    listTiles.add(createTile("Recreate Magic Mike's photoshoot", 11,
        adminConfig!.isMagicMikeRecreated));
    listTiles.add(createTile("Invite Kett Maher to your wedding", 12,
        adminConfig!.isKettMaherInvited));

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
