import 'dart:convert';
import 'package:death_dice/data_access/cognito_interactor.dart';
import 'package:death_dice/model/admin_config.dart';
import 'package:death_dice/model/http_responses.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:get_it/get_it.dart';
import 'package:http/http.dart' as http;

final getIt = GetIt.instance;

class AnalyticsInteractor {
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  late final String url;
  bool isInitialised = false;

  AnalyticsInteractor();

  Future init() async {
    if (isInitialised) {
      return;
    }
    await dotenv.load(fileName: ".env");
    url = dotenv.env['ANALYTICS_URL']!;
    isInitialised = true;
  }

  Future<Statistics> getStatistics(String username, String accountId) async {
    final token = await cognito.getIdToken(username);

    final response = await http.post(
      Uri.parse('$url/statistics'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': token,
      },
      body: jsonEncode(<String, String>{
        'account_id': accountId,
      }),
    );

    if (response.statusCode == 200) {
      return Statistics.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('uh oh');
    }
  }

  Future<AdminConfig> getConfig(String username) async {
    final token = await cognito.getIdToken(username);

    final response = await http.post(
      Uri.parse('$url/config'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': token,
      },
      body: jsonEncode(<String, String>{}),
    );

    if (response.statusCode == 200) {
      return AdminConfig.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('uh oh');
    }
  }

  Future<void> setConfig(String username, AdminConfig adminConfig) async {
    final token = await cognito.getIdToken(username);

    final response = await http.post(
      Uri.parse('$url/set_config'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': token,
      },
      body: jsonEncode(<String, String>{
        'isNickQuestJudge': adminConfig.isNickQuestJudge.toString(),
        'isMattQuestJudge': adminConfig.isMattQuestJudge.toString(),
        'isNickQuestTarget': adminConfig.isNickQuestTarget.toString(),
        'isMattQuestTarget': adminConfig.isMattQuestTarget.toString(),
        'areEggsFound': adminConfig.areEggsFound.toString(),
        'hasBulgarianBeenAsked': adminConfig.hasBulgarianBeenAsked.toString(),
        'hasRandomBeenTongued': adminConfig.hasRandomBeenTongued.toString(),
        'hasWestEndBeenOrdered': adminConfig.hasWestEndBeenOrdered.toString(),
        'hasTantrumBeenThrown': adminConfig.hasTantrumBeenThrown.toString(),
        'hasElectricityBillCalled':
            adminConfig.hasElectricityBillCalled.toString(),
        'isStrangerFoiledAgain': adminConfig.isStrangerFoiledAgain.toString(),
        'hasBupBeenDowed': adminConfig.hasBupBeenDowed.toString(),
        'hasVenuePlayedSteelPanther':
            adminConfig.hasVenuePlayedSteelPanther.toString(),
        'hasHalfTimeSpeechInspired':
            adminConfig.hasHalfTimeSpeechInspired.toString(),
        'isCrevatteWorn': adminConfig.isCrevatteWorn.toString(),
        'isFingerRinged': adminConfig.isFingerRinged.toString(),
        'areSexyClownsReal': adminConfig.areSexyClownsReal.toString(),
        'isMagicGathered': adminConfig.isMagicGathered.toString(),
        'isHotSauceConsumed': adminConfig.isHotSauceConsumed.toString(),
        'isArmpitFarted': adminConfig.isArmpitFarted.toString(),
        'isChronicRhinitusTreated':
            adminConfig.isChronicRhinitusTreated.toString(),
        'isCatchupOrganised': adminConfig.isCatchupOrganised.toString(),
        'isMagicMikeRecreated': adminConfig.isMagicMikeRecreated.toString(),
        'isHotDogEaten': adminConfig.isHotDogEaten.toString(),
        'isKettMaherInvited': adminConfig.isKettMaherInvited.toString(),
      }),
    );

    if (response.statusCode == 200) {
      return;
    } else {
      throw Exception('uh oh');
    }
  }
}
