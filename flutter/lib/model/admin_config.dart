class AdminConfig {
  bool isNickQuestJudge;
  bool isMattQuestJudge;
  bool isNickQuestTarget;
  bool isMattQuestTarget;
  // Quest details
  bool isEggOneFound;
  bool isEggTwoFound;
  bool isEggThreeFound;
  bool isEggFourFound;

  AdminConfig({
    required this.isNickQuestJudge,
    required this.isMattQuestJudge,
    required this.isNickQuestTarget,
    required this.isMattQuestTarget,
    required this.isEggOneFound,
    required this.isEggTwoFound,
    required this.isEggThreeFound,
    required this.isEggFourFound,
  });

  factory AdminConfig.fromJson(Map<String, dynamic> json) {
    return AdminConfig(
      isNickQuestJudge: json['isNickQuestJudge'],
      isMattQuestJudge: json['isMattQuestJudge'],
      isNickQuestTarget: json['isNickQuestTarget'],
      isMattQuestTarget: json['isMattQuestTarget'],
      isEggOneFound: json['isEggOneFound'],
      isEggTwoFound: json['isEggTwoFound'],
      isEggThreeFound: json['isEggThreeFound'],
      isEggFourFound: json['isEggFourFound'],
    );
  }
}
