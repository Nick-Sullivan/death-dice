import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:death_dice/data_access/cognito_interactor.dart';
import 'package:death_dice/data_access/database_interactor.dart';
import 'package:death_dice/model/constants.dart';
import 'package:death_dice/screens/forgot_password_screen.dart';
import 'package:death_dice/screens/home_screen.dart';
import 'package:death_dice/screens/sign_up_screen.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';

final getIt = GetIt.instance;

class LoginLoadingScreen extends StatefulWidget {
  const LoginLoadingScreen({Key? key}) : super(key: key);

  @override
  State<LoginLoadingScreen> createState() => _LoginLoadingScreenState();
}

class _LoginLoadingScreenState extends State<LoginLoadingScreen> {
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  final DatabaseInteractor database = getIt<DatabaseInteractor>();

  @override
  void initState() {
    init();
    super.initState();
  }

  Future init() async {
    await cognito.init();
    await database.init();
    var screen = await isLoggedIn() ? const HomeScreen() : const LogInScreen();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => screen),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).backgroundColor,
      body: buildLogo(),
    );
  }

  Widget buildLogo() {
    return Center(
      child: SizedBox(
        width: 150,
        height: 100,
        child: CircularProgressIndicator(color: Theme.of(context).primaryColor),
      ),
    );
  }

  Future<bool> isLoggedIn() async {
    if (!database.containsKey(usernameKey) ||
        !database.containsKey(passwordKey)) {
      return false;
    }
    debugPrint('Details already exist, logging in');
    var username = database.read(usernameKey);
    var password = database.read(passwordKey);
    try {
      var account = await cognito.authenticate(username, password);
      await database.write(accountIdKey, account.id);
      await database.write(accountEmailKey, account.email);
    } on CognitoUserException catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.message ?? "")));
      return false;
    }
    return true;
  }
}

class LogInScreen extends StatefulWidget {
  final String? initialEmail;

  const LogInScreen({
    super.key,
    this.initialEmail,
  });

  @override
  State<LogInScreen> createState() => _LogInScreenState();
}

class _LogInScreenState extends State<LogInScreen> {
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  final DatabaseInteractor database = getIt<DatabaseInteractor>();
  final AssetImage canLogo = const AssetImage("assets/images/can-logo.png");
  late final TextEditingController emailController;
  late final TextEditingController passwordController;
  bool isLoading = false;

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    emailController = TextEditingController(text: widget.initialEmail ?? "");
    passwordController = TextEditingController();
    database.init();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).backgroundColor,
      body: SingleChildScrollView(
        child: Column(
          children: <Widget>[
            Padding(
              padding: const EdgeInsets.only(top: 60.0, bottom: 30.0),
              child: buildLogo(),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 15),
              child: buildEmail(),
            ),
            Padding(
              padding: const EdgeInsets.only(
                  left: 15.0, right: 15.0, top: 15, bottom: 0),
              child: buildPassword(),
            ),
            buildForgotPassword(),
            buildLogin(),
            buildSignUp(),
          ],
        ),
      ),
    );
  }

  Widget buildLogo() {
    var image = isLoading
        ? CircularProgressIndicator(color: Theme.of(context).primaryColor)
        : Image(image: canLogo);
    return Center(
      child: SizedBox(
        width: 200,
        height: 150,
        child: image,
      ),
    );
  }

  Widget buildEmail() {
    return TextField(
      controller: emailController,
      decoration: const InputDecoration(
        border: OutlineInputBorder(),
        labelText: 'Email',
      ),
      enabled: !isLoading,
    );
  }

  Widget buildPassword() {
    return TextField(
      controller: passwordController,
      decoration: const InputDecoration(
        border: OutlineInputBorder(),
        labelText: 'Password',
      ),
      enabled: !isLoading,
      obscureText: true,
    );
  }

  Widget buildForgotPassword() {
    return TextButton(
      onPressed: isLoading
          ? null
          : () {
              Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (context) => const ForgotPasswordScreen()),
              );
            },
      child: Text(
        'Forgot Password',
        style: TextStyle(
          color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
          fontSize: 15,
        ),
      ),
    );
  }

  Widget buildLogin() {
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
                var success = await logIn();
                setState(() => isLoading = false);
                if (success && mounted) {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => const HomeScreen()),
                  );
                }
              },
        child: const Text(
          'Log in',
          style: TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildSignUp() {
    return TextButton(
      onPressed: isLoading
          ? null
          : () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SignUpScreen()),
              );
            },
      child: Text(
        'New User? Create Account',
        style: TextStyle(
          color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
          fontSize: 15,
        ),
      ),
    );
  }

  Future<bool> logIn() async {
    try {
      var account = await cognito.authenticate(
          emailController.text, passwordController.text);
      await database.write(usernameKey, emailController.text);
      await database.write(passwordKey, passwordController.text);
      await database.write(accountIdKey, account.id);
      await database.write(accountEmailKey, account.email);
      return true;
    } on CognitoUserException catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.message ?? "Error")));
      return false;
    }
  }
}
