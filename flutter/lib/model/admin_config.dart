class AdminConfig {
  bool isNickQuestJudge;
  bool isMattQuestJudge;
  bool isNickQuestTarget;
  bool isMattQuestTarget;
  // Quest details
  bool areEggsFound;
  bool hasBulgarianBeenAsked;
  bool hasRandomBeenTongued;
  bool hasWestEndBeenOrdered;
  bool hasTantrumBeenThrown;
  bool hasElectricityBillCalled;
  bool isStrangerFoiledAgain;
  bool hasBupBeenDowed;
  bool hasVenuePlayedSteelPanther;
  bool hasHalfTimeSpeechInspired;
  bool isCrevatteWorn;
  bool isFingerRinged;
  bool areSexyClownsReal;
  bool isMagicGathered;
  bool isHotSauceConsumed;
  bool isArmpitFarted;
  bool isChronicRhinitusTreated;
  bool isCatchupOrganised;
  bool isMagicMikeRecreated;
  bool isHotDogEaten;
  bool isKettMaherInvited;

  AdminConfig({
    required this.isNickQuestJudge,
    required this.isMattQuestJudge,
    required this.isNickQuestTarget,
    required this.isMattQuestTarget,
    required this.areEggsFound,
    required this.hasBulgarianBeenAsked,
    required this.hasRandomBeenTongued,
    required this.hasWestEndBeenOrdered,
    required this.hasTantrumBeenThrown,
    required this.hasElectricityBillCalled,
    required this.isStrangerFoiledAgain,
    required this.hasBupBeenDowed,
    required this.hasVenuePlayedSteelPanther,
    required this.hasHalfTimeSpeechInspired,
    required this.isCrevatteWorn,
    required this.isFingerRinged,
    required this.areSexyClownsReal,
    required this.isMagicGathered,
    required this.isHotSauceConsumed,
    required this.isArmpitFarted,
    required this.isChronicRhinitusTreated,
    required this.isCatchupOrganised,
    required this.isMagicMikeRecreated,
    required this.isHotDogEaten,
    required this.isKettMaherInvited,
  });

  factory AdminConfig.fromJson(Map<String, dynamic> json) {
    return AdminConfig(
      isNickQuestJudge: json['isNickQuestJudge'] ?? false,
      isMattQuestJudge: json['isMattQuestJudge'] ?? false,
      isNickQuestTarget: json['isNickQuestTarget'] ?? false,
      isMattQuestTarget: json['isMattQuestTarget'] ?? false,
      areEggsFound: json['areEggsFound'] ?? false,
      hasBulgarianBeenAsked: json['hasBulgarianBeenAsked'] ?? false,
      hasRandomBeenTongued: json['hasRandomBeenTongued'] ?? false,
      hasWestEndBeenOrdered: json['hasWestEndBeenOrdered'] ?? false,
      hasTantrumBeenThrown: json['hasTantrumBeenThrown'] ?? false,
      hasElectricityBillCalled: json['hasElectricityBillCalled'] ?? false,
      isStrangerFoiledAgain: json['isStrangerFoiledAgain'] ?? false,
      hasBupBeenDowed: json['hasBupBeenDowed'] ?? false,
      hasVenuePlayedSteelPanther: json['hasVenuePlayedSteelPanther'] ?? false,
      hasHalfTimeSpeechInspired: json['hasHalfTimeSpeechInspired'] ?? false,
      isCrevatteWorn: json['isCrevatteWorn'] ?? false,
      isFingerRinged: json['isFingerRinged'] ?? false,
      areSexyClownsReal: json['areSexyClownsReal'] ?? false,
      isMagicGathered: json['isMagicGathered'] ?? false,
      isHotSauceConsumed: json['isHotSauceConsumed'] ?? false,
      isArmpitFarted: json['isArmpitFarted'] ?? false,
      isChronicRhinitusTreated: json['isChronicRhinitusTreated'] ?? false,
      isCatchupOrganised: json['isCatchupOrganised'] ?? false,
      isMagicMikeRecreated: json['isMagicMikeRecreated'] ?? false,
      isHotDogEaten: json['isHotDogEaten'] ?? false,
      isKettMaherInvited: json['isKettMaherInvited'] ?? false,
    );
  }

  bool getProperty(String propertyName) {
    if (propertyName == 'areEggsFound') return areEggsFound;
    if (propertyName == 'hasBulgarianBeenAsked') return hasBulgarianBeenAsked;
    if (propertyName == 'hasRandomBeenTongued') return hasRandomBeenTongued;
    if (propertyName == 'hasWestEndBeenOrdered') return hasWestEndBeenOrdered;
    if (propertyName == 'hasTantrumBeenThrown') return hasTantrumBeenThrown;
    if (propertyName == 'hasElectricityBillCalled')
      return hasElectricityBillCalled;
    if (propertyName == 'isStrangerFoiledAgain') return isStrangerFoiledAgain;
    if (propertyName == 'hasBupBeenDowed') return hasBupBeenDowed;
    if (propertyName == 'hasVenuePlayedSteelPanther')
      return hasVenuePlayedSteelPanther;
    if (propertyName == 'hasHalfTimeSpeechInspired')
      return hasHalfTimeSpeechInspired;
    if (propertyName == 'isCrevatteWorn') return isCrevatteWorn;
    if (propertyName == 'isFingerRinged') return isFingerRinged;
    if (propertyName == 'areSexyClownsReal') return areSexyClownsReal;
    if (propertyName == 'isMagicGathered') return isMagicGathered;
    if (propertyName == 'isHotSauceConsumed') return isHotSauceConsumed;
    if (propertyName == 'isArmpitFarted') return isArmpitFarted;
    if (propertyName == 'isChronicRhinitusTreated')
      return isChronicRhinitusTreated;
    if (propertyName == 'isCatchupOrganised') return isCatchupOrganised;
    if (propertyName == 'isMagicMikeRecreated') return isMagicMikeRecreated;
    if (propertyName == 'isHotDogEaten') return isHotDogEaten;
    if (propertyName == 'isKettMaherInvited') return isKettMaherInvited;
    return false;
  }

  void setProperty(String propertyName, bool value) {
    if (propertyName == 'areEggsFound') areEggsFound = value;
    if (propertyName == 'hasBulgarianBeenAsked') hasBulgarianBeenAsked = value;
    if (propertyName == 'hasRandomBeenTongued') hasRandomBeenTongued = value;
    if (propertyName == 'hasWestEndBeenOrdered') hasWestEndBeenOrdered = value;
    if (propertyName == 'hasTantrumBeenThrown') hasTantrumBeenThrown = value;
    if (propertyName == 'hasElectricityBillCalled')
      hasElectricityBillCalled = value;
    if (propertyName == 'isStrangerFoiledAgain') isStrangerFoiledAgain = value;
    if (propertyName == 'hasBupBeenDowed') hasBupBeenDowed = value;
    if (propertyName == 'hasVenuePlayedSteelPanther')
      hasVenuePlayedSteelPanther = value;
    if (propertyName == 'hasHalfTimeSpeechInspired')
      hasHalfTimeSpeechInspired = value;
    if (propertyName == 'isCrevatteWorn') isCrevatteWorn = value;
    if (propertyName == 'isFingerRinged') isFingerRinged = value;
    if (propertyName == 'areSexyClownsReal') areSexyClownsReal = value;
    if (propertyName == 'isMagicGathered') isMagicGathered = value;
    if (propertyName == 'isHotSauceConsumed') isHotSauceConsumed = value;
    if (propertyName == 'isArmpitFarted') isArmpitFarted = value;
    if (propertyName == 'isChronicRhinitusTreated')
      isChronicRhinitusTreated = value;
    if (propertyName == 'isCatchupOrganised') isCatchupOrganised = value;
    if (propertyName == 'isMagicMikeRecreated') isMagicMikeRecreated = value;
    if (propertyName == 'isHotDogEaten') isHotDogEaten = value;
    if (propertyName == 'isKettMaherInvited') isKettMaherInvited = value;
  }
}
