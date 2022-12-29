import 'package:death_dice/data_access/cognito_interactor.dart';
import 'package:death_dice/screens/log_in_screen.dart';
import 'package:flutter/material.dart';
import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:get_it/get_it.dart';
final getIt = GetIt.instance;


class SignUpScreen extends StatefulWidget {
  const SignUpScreen({Key? key}) : super(key: key);

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  bool isLoading = false;

  @override
  void dispose() {
    emailController.dispose();
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
              padding: const EdgeInsets.symmetric(horizontal: 15),
              child: buildEmail(),
            ),
            Padding(
              padding: const EdgeInsets.only(left: 15.0, right: 15.0, top: 15, bottom: 15),
              child: buildPassword(),
            ),
            buildSignUpButton(),
            buildGoBack(),
          ],
        ),
      ),
    );
  }

  Widget buildLogo() {
    var image = isLoading
      ? CircularProgressIndicator(color: Theme.of(context).primaryColor)
      : const Image(image: AssetImage('assets/can-logo.png'));
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

  Widget buildSignUpButton() {
    return Container(
      height: 50,
      width: 250,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
      ),
      child: TextButton(
        onPressed: isLoading ? null : () async {
          setState(() => isLoading = true);
          var success = await signUp();
          setState(() => isLoading = false);

          if (success && mounted){
            Navigator.push(context, MaterialPageRoute(builder: (_) => SignUpConfirmationScreen(email: emailController.text)));
          }
        },
        child: const Text(
          'Sign up',
          style: TextStyle(color: Colors.white, fontSize: 25),
        ),
      ),
    );
  }

  Widget buildGoBack() {
    return TextButton(
      onPressed: isLoading ? null : (){
        Navigator.pop(context);
      },
      child: Text(
        'Already have an account? Sign in',
        style: TextStyle(
          color: isLoading ? Colors.grey : Theme.of(context).primaryColor,
          fontSize: 15,
        ),
      ),
    );
  }

  Future<bool> signUp() async {
    try {
      await cognito.signUp(emailController.text, passwordController.text);
      return true;
    } on CognitoClientException catch(e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message ?? ""))
      );
      return false;
    }
  }

}


class SignUpConfirmationScreen extends StatefulWidget {
  final String email;

  const SignUpConfirmationScreen({
    super.key,
    required this.email,
  });

  @override
  State<SignUpConfirmationScreen> createState() => _SignUpConfirmationScreenState();
}

class _SignUpConfirmationScreenState extends State<SignUpConfirmationScreen> {
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  final codeController = TextEditingController();
  bool isLoading = false;

  @override
  void dispose() {
    codeController.dispose();
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
              padding: const EdgeInsets.all(30),
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
      : const Image(image: AssetImage('assets/can-logo.png'));
    return Center(
      child: SizedBox(
        width: 200,
        height: 150,
        child: image,
      ),
    );
  }

  Widget buildCodeInput(){
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
  
  Widget buildConfirmButton(){
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
          var success = await confirm();
          setState(() => isLoading = false);

          if (success && mounted){
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text("Account created"))
            );

            Navigator.of(context).pushAndRemoveUntil(
              MaterialPageRoute(
                builder: (context) => LogInScreen(initialEmail: widget.email)
              ), 
              (Route<dynamic> route) => false
            );
          }
        },
        child: const Text(
          'Confirm',
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
      await cognito.confirmRegistration(widget.email, codeController.text);
      return true;
    } on CognitoClientException catch(e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message ?? ""))
      );
      return false;
    }
  }

  void resendCode() async {
    try {
      await cognito.resendConfirmationCode(widget.email);
    } on CognitoClientException catch(e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message ?? ""))
      );
    }
  }

}
