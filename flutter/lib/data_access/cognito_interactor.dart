import 'dart:collection';

import 'package:amazon_cognito_identity_dart_2/cognito.dart';
import 'package:death_dice/model/account.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class CognitoInteractor {
  bool isInitialised = false;
  late final CognitoUserPool userPool;
  HashMap userCache = HashMap<String, CognitoUser>();
  HashMap sessionCache = HashMap<String, CognitoUserSession>();

  CognitoInteractor();

  Future init() async {
    if (isInitialised) {
      return;
    }
    await dotenv.load(fileName: ".env");
    var poolId = dotenv.env['COGNITO_USER_POOL']!;
    var clientId = dotenv.env['COGNITO_CLIENT_ID']!;
    userPool = CognitoUserPool(poolId, clientId);
    isInitialised = true;
  }

  CognitoUser getUser(String username) {
    if (!userCache.containsKey(username)) {
      userCache[username] = CognitoUser(username, userPool);
    }
    return userCache[username];
  }

  CognitoUserSession getSession(String username) {
    return sessionCache[username];
  }

  Future signUp(String username, String password) async {
    return userPool.signUp(username, password);
  }

  Future confirmRegistration(String username, String code) async {
    final cognitoUser = getUser(username);
    return cognitoUser.confirmRegistration(code);
  }

  Future resendConfirmationCode(String username) async {
    final cognitoUser = getUser(username);
    return cognitoUser.resendConfirmationCode();
  }

  Future<Account> authenticate(String username, String password) async {
    final cognitoUser = getUser(username);
    final authDetails = AuthenticationDetails(
      username: username,
      password: password,
    );

    CognitoUserException exception;
    try {
      var session = await cognitoUser.authenticateUser(authDetails);
      sessionCache[username] = session;

      var attributes = await cognitoUser.getUserAttributes();
      var accountId = attributes!.singleWhere((a) => a.name == 'sub').value!;
      var email = attributes.singleWhere((a) => a.name == 'email').value!;
      return Account(accountId, email);
    } on CognitoUserNewPasswordRequiredException catch (e) {
      // handle New Password challenge
      exception = e;
    } on CognitoUserMfaRequiredException catch (e) {
      // handle SMS_MFA challenge
      exception = e;
    } on CognitoUserSelectMfaTypeException catch (e) {
      // handle SELECT_MFA_TYPE challenge
      exception = e;
    } on CognitoUserMfaSetupException catch (e) {
      // handle MFA_SETUP challenge
      exception = e;
    } on CognitoUserTotpRequiredException catch (e) {
      // handle SOFTWARE_TOKEN_MFA challenge
      exception = e;
    } on CognitoUserCustomChallengeException catch (e) {
      // handle CUSTOM_CHALLENGE challenge
      exception = e;
    } on CognitoUserConfirmationNecessaryException catch (e) {
      // handle User Confirmation Necessary
      exception = e;
    } on CognitoClientException catch (e) {
      // handle Wrong Username and Password and Cognito Client
      exception = CognitoUserException(e.message);
    }
    throw exception;
  }

  Future<dynamic> forgotPassword(String username) async {
    final cognitoUser = getUser(username);
    return cognitoUser.forgotPassword();
  }

  Future confirmPassword(String username, String password, String code) {
    final cognitoUser = getUser(username);
    return cognitoUser.confirmPassword(code, password);
  }

  Future<List<CognitoUserAttribute>?> getUserAttributes(String username) {
    final cognitoUser = getUser(username);
    return cognitoUser.getUserAttributes();
  }

  Future<String> getIdToken(String username) async {
    final session = getSession(username);
    return session.idToken.getJwtToken()!;
  }
}
