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
  final AssetImage background = const AssetImage("assets/images/desert-tins.jpg");
  final AssetImage canLogo = const AssetImage("assets/images/can-logo-grey.png");
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
      body: Container(
        constraints: const BoxConstraints.expand(),
        decoration: BoxDecoration(
          image: DecorationImage(
            alignment: Alignment.center,
            colorFilter: ColorFilter.mode(Colors.black.withOpacity(0.5), BlendMode.dstATop),
            fit: BoxFit.cover,
            image: background,
          )
        ),
        child: buildGameStatistics(),
        
      ),
    );
  }

  AppBar buildAppBar(){
    return AppBar(
      title: const Text('Account'),
      backgroundColor: Theme.of(context).primaryColor,
    );
  }

  Widget buildGameStatistics() {

    var gamesPlayed = '-';
    var diceRolled = '-';
    var roundsPlayed = '-';
    var roundsSpectated = '-';
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
      roundsSpectated = statistics!.roundsSpectated.toString();
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
      TextSpan(text: 'Rolls: $diceRolled\n'),
      TextSpan(text: 'Games: $gamesPlayed\n'),
      TextSpan(text: 'Rounds (spectator): $roundsSpectated\n'),
      TextSpan(text: 'Rounds (player): $roundsPlayed\n'),
      TextSpan(text: '\n'),
      TextSpan(text: 'Wins: $outcomeWinner ($outcomeWinPercent%)\n'),
      TextSpan(text: 'Losses: $outcomeSipDrink\n'),
      TextSpan(text: 'Tie: $outcomeTie\n'),
      TextSpan(text: 'Finish drink: $outcomeFinishDrink\n'),
      TextSpan(text: 'Dual wield: $outcomeDualWield\n'),
      TextSpan(text: 'Shower: $outcomeShower\n'),
      TextSpan(text: 'Head on table: $outcomeHeadOnTable\n'),
      TextSpan(text: 'Wish purchase: $outcomeWishPurchase\n'),
      TextSpan(text: 'Pool: $outcomePool\n'),
    ];
    const scaling = 0.8;
    const width = 326 * scaling;
    const height = 612 * scaling;
    return Stack(
      alignment: Alignment.center,
      children: [
        Image(
          image: canLogo,
          width: width,
          height: height,
        ),
        Container(
          alignment: Alignment.center,
          width: width,
          height: height,
          child: Padding(
            padding: const EdgeInsets.only(left: 20, top: 115),
            child: RichText(
              text: TextSpan(
                style: TextStyle(
                  color: Color(0xffb7212a),
                  fontFamily: 'Stanford Breath'
                ),
                children: spans,
              ),
              textAlign: TextAlign.left,
            ),
          ),
        ),
      ],
    );
  }

  Future<Statistics> getStatistics() async {
    return await analytics.getStatistics(widget.username, widget.accountId);
  }

}