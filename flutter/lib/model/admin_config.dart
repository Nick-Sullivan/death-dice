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
      isNickQuestJudge: json['isNickQuestJudge'] ?? false,
      isMattQuestJudge: json['isMattQuestJudge'] ?? false,
      isNickQuestTarget: json['isNickQuestTarget'] ?? false,
      isMattQuestTarget: json['isMattQuestTarget'] ?? false,
      isEggOneFound: json['isEggOneFound'] ?? false,
      isEggTwoFound: json['isEggTwoFound'] ?? false,
      isEggThreeFound: json['isEggThreeFound'] ?? false,
      isEggFourFound: json['isEggFourFound'] ?? false,
    );
  }
}
