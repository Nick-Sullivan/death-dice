import 'package:death_dice/data_access/cognito_interactor.dart';
import 'package:death_dice/screens/log_in_screen.dart';
import 'package:flutter/material.dart';
import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:get_it/get_it.dart';

final getIt = GetIt.instance;

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({Key? key}) : super(key: key);

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final emailController = TextEditingController();
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  final AssetImage canLogo = const AssetImage("assets/images/can-logo.png");
  bool isLoading = false;

  @override
  void dispose() {
    emailController.dispose();
    super.dispose();
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
              padding: const EdgeInsets.only(
                  left: 15, right: 15, top: 0, bottom: 30),
              child: buildEmail(),
            ),
            buildRequestPasswordChange(),
            buildGoBack(),
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
      onSubmitted: (_) => requestPasswordChange(),
      textInputAction: TextInputAction.done,
    );
  }

  Widget buildRequestPasswordChange() {
    return Container(
      height: 50,
      width: 250,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
      ),
      child: TextButton(
        onPressed: isLoading
            ? null
            : () async {
                setState(() => isLoading = true);
                var success = await requestPasswordChange();
                setState(() => isLoading = false);
                if (success && mounted) {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (_) => ResetPasswordConfirmationScreen(
                              email: emailController.text)));
                }
              },
        child: const Text(
          'Change password',
          style: TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildGoBack() {
    return TextButton(
      onPressed: isLoading
          ? null
          : () {
              Navigator.pop(context);
            },
      child: Text(
        'Go back',
        style: TextStyle(
          color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
          fontSize: 15,
        ),
      ),
    );
  }

  Future<bool> requestPasswordChange() async {
    try {
      await cognito.forgotPassword(emailController.text);
      return true;
    } on CognitoClientException catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.message ?? "")));
      return false;
    }
  }
}

class ResetPasswordConfirmationScreen extends StatefulWidget {
  final String email;

  const ResetPasswordConfirmationScreen({
    super.key,
    required this.email,
  });

  @override
  State<ResetPasswordConfirmationScreen> createState() =>
      _ResetPasswordConfirmationScreenState();
}

class _ResetPasswordConfirmationScreenState
    extends State<ResetPasswordConfirmationScreen> {
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  final codeController = TextEditingController();
  final passwordController = TextEditingController();
  final AssetImage canLogo = const AssetImage("assets/images/can-logo.png");
  bool isLoading = false;

  @override
  void dispose() {
    codeController.dispose();
    passwordController.dispose();
    super.dispose();
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
              padding: const EdgeInsets.only(
                  left: 15.0, right: 15.0, top: 15, bottom: 15),
              child: buildPassword(),
            ),
            Padding(
              padding: const EdgeInsets.only(left: 15, right: 15, bottom: 15),
              child: buildCodeInput(),
            ),
            buildConfirmButton(),
            buildResendCode(),
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

  Widget buildPassword() {
    return TextField(
      controller: passwordController,
      decoration: const InputDecoration(
        border: OutlineInputBorder(),
        labelText: 'New Password',
      ),
      enabled: !isLoading,
      obscureText: true,
    );
  }

  Widget buildCodeInput() {
    return TextField(
      controller: codeController,
      decoration: const InputDecoration(
        border: OutlineInputBorder(),
        labelText: 'Verification code',
      ),
      enabled: !isLoading,
      keyboardType: TextInputType.number,
    );
  }

  Widget buildConfirmButton() {
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
                var success = await confirm();
                setState(() => isLoading = false);

                if (success && mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text("Password has been reset")));
                  Navigator.of(context).pushAndRemoveUntil(
                      MaterialPageRoute(
                          builder: (context) =>
                              LogInScreen(initialEmail: widget.email)),
                      (Route<dynamic> route) => false);
                }
              },
        child: const Text(
          'Set password',
          style: TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildResendCode() {
    return TextButton(
      onPressed: isLoading ? null : resendCode,
      child: Text(
        'No confirmation code? Send it again',
        style: TextStyle(
          color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
          fontSize: 15,
        ),
      ),
    );
  }

  Future<bool> confirm() async {
    try {
      await cognito.confirmPassword(
          widget.email, passwordController.text, codeController.text);
      return true;
    } on CognitoClientException catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.message ?? "")));
      return false;
    }
  }

  void resendCode() async {
    try {
      await cognito.resendConfirmationCode(widget.email);
    } on CognitoClientException catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.message ?? "")));
    }
  }
}
