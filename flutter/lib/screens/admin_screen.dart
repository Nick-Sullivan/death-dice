import 'package:death_dice/data_access/analytics_interactor.dart';
import 'package:death_dice/data_access/cognito_interactor.dart';
import 'package:death_dice/model/admin_config.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';

final getIt = GetIt.instance;

class AdminScreen extends StatefulWidget {
  final String accountId;
  final String username;

  const AdminScreen({
    super.key,
    required this.accountId,
    required this.username,
  });

  @override
  State<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends State<AdminScreen> {
  final CognitoInteractor cognito = getIt<CognitoInteractor>();
  final AnalyticsInteractor analytics = getIt<AnalyticsInteractor>();

  bool isLoading = false;
  AdminConfig? adminConfig;

  @override
  void initState() {
    isLoading = true;
    analytics
        .init()
        .then((_) => analytics.getConfig(widget.username))
        .then((value) {
      adminConfig = value;
      setState(() => isLoading = false);
    });
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).backgroundColor,
      appBar: buildAppBar(),
      body: buildBody(),
    );
  }

  AppBar buildAppBar() {
    return AppBar(
      title: const Text('Admin Settings'),
      backgroundColor: Theme.of(context).primaryColor,
    );
  }

  Widget buildBody() {
    if (isLoading) {
      return Center(
        child: SizedBox(
          width: 50,
          height: 50,
          child:
              CircularProgressIndicator(color: Theme.of(context).primaryColor),
        ),
      );
    }

    return ListView(
      children: [
        ListTile(
          title: const Text("Nick - Quest Judge"),
          trailing: Checkbox(
              activeColor: Colors.red.shade400,
              value: adminConfig!.isNickQuestJudge,
              onChanged: (value) {
                adminConfig!.isNickQuestJudge = value!;
                analytics.setConfig(widget.username, adminConfig!);
                setState(() {});
              }),
        ),
        ListTile(
          title: const Text("Nick - Quest Target"),
          trailing: Checkbox(
              activeColor: Colors.red.shade400,
              value: adminConfig!.isNickQuestTarget,
              onChanged: (value) {
                adminConfig!.isNickQuestTarget = value!;
                analytics.setConfig(widget.username, adminConfig!);
                setState(() {});
              }),
        ),
        ListTile(
          title: const Text("Matt - Quest Judge"),
          trailing: Checkbox(
              activeColor: Colors.red.shade400,
              value: adminConfig!.isMattQuestJudge,
              onChanged: (value) {
                adminConfig!.isMattQuestJudge = value!;
                analytics.setConfig(widget.username, adminConfig!);
                setState(() {});
              }),
        ),
        ListTile(
          title: const Text("Matt - Quest Target"),
          trailing: Checkbox(
              activeColor: Colors.red.shade400,
              value: adminConfig!.isMattQuestTarget,
              onChanged: (value) {
                adminConfig!.isMattQuestTarget = value!;
                analytics.setConfig(widget.username, adminConfig!);
                setState(() {});
              }),
        ),
        ListTile(
          title: const Text("Angus - Quest Target"),
          trailing: Checkbox(
              activeColor: Colors.red.shade400,
              value: adminConfig!.isAngusQuestTarget,
              onChanged: (value) {
                adminConfig!.isAngusQuestTarget = value!;
                analytics.setConfig(widget.username, adminConfig!);
                setState(() {});
              }),
        ),
      ],
    );
  }
}
