import 'package:death_dice/data_access/analytics_interactor.dart';
import 'package:death_dice/data_access/cognito_interactor.dart';
import 'package:death_dice/model/http_responses.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
final getIt = GetIt.instance;

const analyticsUrl = 'https://3er3bwfcy1.execute-api.ap-southeast-2.amazonaws.com/v1/statistics';

class AccountScreen extends StatefulWidget {
  final String accountId;
  final String username;

  const AccountScreen({
    super.key,
    required this.accountId,
    required this.username,
  });

  @override
  State<AccountScreen> createState() => _AccountScreenState();
}

class _AccountScreenState extends State<AccountScreen> {
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  final AnalyticsInteractor analytics = getIt<AnalyticsInteractor>();
  bool isLoading = false;
  Statistics? statistics;

  @override
  void initState() {
    isLoading = true;
    analytics.init()
      .then((_) => getStatistics())
      .then((value) {
        statistics = value;
        setState(() => isLoading = false);
      });
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
            // Padding(
            //   padding: const EdgeInsets.only(top: 10.0, bottom: 10.0),
            //   child: buildSendButton(),
            // ),
            Padding(
              padding: const EdgeInsets.only(top: 10.0, bottom: 10.0),
              child: buildGameStatistics(),
            ),
          ],
        ),
      ),
    );
  }

  AppBar buildAppBar(){
    return AppBar(
      title: const Text('Account'),
      backgroundColor: Theme.of(context).primaryColor,
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
  
  Widget buildSendButton() {
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
          statistics = await getStatistics();
          setState(() => isLoading = false);
        },
        child: const Text(
          'Refresh data',
          style: TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildGameStatistics() {

    var gamesPlayed = '-';
    var diceRolled = '-';
    var roundsPlayed = '-';
    var outcomeTie = '-';
    var outcomeSipDrink = '-';
    var outcomeWinner = '-';
    var outcomeFinishDrink = '-';
    var outcomeDualWield = '-';
    var outcomeShower = '-';
    var outcomeHeadOnTable = '-';
    var outcomeWishPurchase = '-';
    var outcomePool = '-';

    var outcomeWinPercent= '-';

    if (statistics != null){
      gamesPlayed = statistics!.gamesPlayed.toString();
      diceRolled = statistics!.diceRolled.toString();
      roundsPlayed = statistics!.roundsPlayed.toString();
      outcomeTie = statistics!.outcomeTie.toString();
      outcomeSipDrink = statistics!.outcomeSipDrink.toString();
      outcomeWinner = statistics!.outcomeWinner.toString();
      outcomeFinishDrink = statistics!.outcomeFinishDrink.toString();
      outcomeDualWield = statistics!.outcomeDualWield.toString();
      outcomeShower = statistics!.outcomeShower.toString();
      outcomeHeadOnTable = statistics!.outcomeHeadOnTable.toString();
      outcomeWishPurchase = statistics!.outcomeWishPurchase.toString();
      outcomePool = statistics!.outcomePool.toString();

      outcomeWinPercent = (100 * statistics!.outcomeWinner / statistics!.roundsPlayed).toStringAsFixed(1);
    }

    var spans = <TextSpan>[
      TextSpan(text: 'Dice rolled: $diceRolled\n'),
      TextSpan(text: 'Games played: $gamesPlayed\n'),
      TextSpan(text: 'Rounds played: $roundsPlayed\n'),
      TextSpan(text: '- Wins: $outcomeWinner ($outcomeWinPercent%)\n'),
      TextSpan(text: '- Losses: $outcomeSipDrink\n'),
      TextSpan(text: '- Tie: $outcomeTie\n'),
      TextSpan(text: '- Finish drink: $outcomeFinishDrink\n'),
      TextSpan(text: '- Dual wield: $outcomeDualWield\n'),
      TextSpan(text: '- Shower: $outcomeShower\n'),
      TextSpan(text: '- Head on table: $outcomeHeadOnTable\n'),
      TextSpan(text: '- Wish purchase: $outcomeWishPurchase\n'),
      TextSpan(text: '- Pool: $outcomePool\n'),
    ];
    return RichText(
      text: TextSpan(
        style: const TextStyle(color: Colors.black),
        children: spans,
      ),
      textAlign: TextAlign.left,
    );
  }

  Future<Statistics> getStatistics() async {
    return await analytics.getStatistics(widget.username, widget.accountId);
  }

}