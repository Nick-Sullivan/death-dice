
import 'package:death_dice/data_access/cognito_interactor.dart';
import 'package:death_dice/data_access/database_interactor.dart';
import 'package:death_dice/data_access/websocket_interactor.dart';
import 'package:death_dice/screens/log_in_screen.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
final getIt = GetIt.instance;

void main() {
  getIt.registerSingleton<DatabaseInteractor>(DatabaseInteractor());
  getIt.registerSingleton<CognitoInteractor>(CognitoInteractor());
  getIt.registerSingleton<WebsocketInteractor>(WebsocketInteractor());
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    var primaryColor = Colors.red[800]!;
    return MaterialApp(
      title: 'Death Dice',
      routes: {
        '/login': (context) => const LoginLoadingScreen(),
      },
      initialRoute: '/login',
      theme: ThemeData(
        backgroundColor: Colors.grey[200],
        primaryColor: primaryColor,
        textTheme: const TextTheme(
          bodyText2: TextStyle(
            fontSize: 18,
          )
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderSide: BorderSide(color: primaryColor)
          ),
          focusedBorder: OutlineInputBorder(
            borderSide: BorderSide(color: primaryColor)
          ),
          labelStyle: TextStyle(color: Colors.grey[600]),
        ),
      ),
    );
  }

}
