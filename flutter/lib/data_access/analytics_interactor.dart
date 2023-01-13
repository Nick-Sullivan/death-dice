
import 'dart:convert';
import 'package:death_dice/data_access/cognito_interactor.dart';
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
    if (isInitialised){
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

    if (response.statusCode == 200){
      return Statistics.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('uh oh');
    }
  }
}
