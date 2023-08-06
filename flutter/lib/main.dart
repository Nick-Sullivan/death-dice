
import 'package:death_dice/data_access/analytics_interactor.dart';
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
  getIt.registerSingleton<AnalyticsInteractor>(AnalyticsInteractor());
  getIt.registerSingleton<WebsocketInteractor>(WebsocketInteractor());
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    preCacheImages(context);
    const primaryColor = Color(0xffb7212a);//Colors.red[800]!;
    const secondaryColor = Color(0xffbebfc3);
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
        inputDecorationTheme: const InputDecorationTheme(
          border: OutlineInputBorder(
            borderSide: BorderSide(color: primaryColor)
          ),
          focusedBorder: OutlineInputBorder(
            borderSide: BorderSide(color: primaryColor)
          ),
          labelStyle: TextStyle(color: secondaryColor),
        ),
      ),
    );
  }

  void preCacheImages(BuildContext context) {
    precacheImage(const AssetImage("assets/images/ancient-scroll.png"), context);
    precacheImage(const AssetImage("assets/images/can-icon.png"), context);
    precacheImage(const AssetImage("assets/images/can-in-forest.jpg"), context);
    precacheImage(const AssetImage("assets/images/can-logo-grey.png"), context);
    precacheImage(const AssetImage("assets/images/can-logo-white.png"), context);
    precacheImage(const AssetImage("assets/images/can-logo.png"), context);
    precacheImage(const AssetImage("assets/images/can-square.png"), context);
    precacheImage(const AssetImage("assets/images/desert-oasis.jpg"), context);
    precacheImage(const AssetImage("assets/images/desert-tins.jpg"), context);
    precacheImage(const AssetImage("assets/images/dice-logo.png"), context);
    precacheImage(const AssetImage("assets/images/garden-path.jpg"), context);

  }
}
