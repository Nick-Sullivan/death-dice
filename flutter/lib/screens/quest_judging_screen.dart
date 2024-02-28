import 'package:death_dice/data_access/analytics_interactor.dart';
import 'package:death_dice/data_access/cognito_interactor.dart';
import 'package:death_dice/model/admin_config.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';

final getIt = GetIt.instance;

class QuestJudgingScreen extends StatefulWidget {
  final String accountId;
  final String username;

  const QuestJudgingScreen({
    super.key,
    required this.accountId,
    required this.username,
  });

  @override
  State<QuestJudgingScreen> createState() => _QuestJudgingScreenState();
}

class _QuestJudgingScreenState extends State<QuestJudgingScreen> {
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  final AnalyticsInteractor analytics = getIt<AnalyticsInteractor>();

  bool isLoading = false;
  AdminConfig? adminConfig;

  @override
  void initState() {
    isLoading = true;
    analytics
        .init()
        .then((_) => analytics.getConfig(widget.username))
        .then((value) {
      adminConfig = value;
      setState(() => isLoading = false);
    });
    super.initState();
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
      title: const Text('Quest Judging'),
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

    return ListView(
      children: [
        createTile('areEggsFound'),
        createTile('hasBulgarianBeenAsked'),
        createTile('hasRandomBeenTongued'),
        createTile('hasWestEndBeenOrdered'),
        createTile('hasTantrumBeenThrown'),
        createTile('hasElectricityBillCalled'),
        createTile('isStrangerFoiledAgain'),
        createTile('hasBupBeenDowed'),
        createTile('hasVenuePlayedSteelPanther'),
        createTile('hasHalfTimeSpeechInspired'),
        createTile('isCrevatteWorn'),
        createTile('isFingerRinged'),
        createTile('areSexyClownsReal'),
        createTile('isMagicGathered'),
        createTile('isHotSauceConsumed'),
        createTile('isArmpitFarted'),
        createTile('isHotDogEaten'),
        createTile('isChronicRhinitusTreated'),
        createTile('isCatchupOrganised'),
        createTile('isMagicMikeRecreated'),
        createTile('isKettMaherInvited'),
      ],
    );
  }

  ListTile createTile(String propertyName) {
    return ListTile(
      title: Text(propertyName),
      trailing: Checkbox(
          activeColor: Colors.red.shade400,
          value: adminConfig!.getProperty(propertyName),
          onChanged: (value) {
            adminConfig!.setProperty(propertyName, value!);
            analytics.setConfig(widget.username, adminConfig!);
            setState(() {});
          }),
    );
  }
}
