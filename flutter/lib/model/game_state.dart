
import 'dart:convert';

enum GameAction {
  setNickname,
  joinGame,
  gameState,
}

enum RollResult{
  none(''),
  cockringHands('COCKRING_HANDS'),
  dualWield('DUAL_WIELD'),
  headOnTable('HEAD_ON_TABLE'),
  finishDrink('FINISH_DRINK'),
  pool('POOL'),
  sipDrink('SIP_DRINK'),
  shower('SHOWER'),
  threeWayTie('THREE_WAY_TIE'),
  tie('TIE'),
  uhOh('UH_OH'),
  winner('WINNER'),
  wishPurchase('WISH_PURCHASE'),
  ;

  final String value;
  static final Map<String, RollResult> _byValue = {};

  const RollResult(this.value);

  static RollResult getByValue(String value){
    if (_byValue.isEmpty){
      for (var result in RollResult.values){
        _byValue[result.value] = result;
      }
    }
    return _byValue[value]!;
  }
}

enum Dice {
  d4,
  d6,
  d8,
  d10,
  d12,
  d20,
  d10percentile,
}

class GameState {
  List<GamePlayer> players;
  List<GameSpectator> spectators;
  GameRound round;

  GameState(this.players, this.spectators, this.round);

  factory GameState.fromJson(Map<String, dynamic> map){
    var players = <GamePlayer>[];
    for (var playerJson in map['players']){
      players.add(GamePlayer.fromJson(playerJson));
    }
    var spectators = <GameSpectator>[];
    for (var spectatorJson in map['spectators']){
      spectators.add(GameSpectator.fromJson(spectatorJson));
    }
    return GameState(
      players,
      spectators,
      GameRound.fromJson(map['round']),
    );
  }
}


class GameSpectator {
  String id;
  String nickname;

  GameSpectator(this.id, this.nickname);

  factory GameSpectator.fromJson(Map<String, dynamic> map){
    return GameSpectator(
      map['id'],
      map['nickname'],
    );
  }
}


class GamePlayer {
  String id;
  String nickname;
  bool isTurnFinished;
  int winCount;
  RollResult? rollResult;
  int? rollTotal;
  List<DiceRoll> diceRolls;

  GamePlayer(this.id, this.nickname, this.isTurnFinished, this.winCount, this.rollResult, this.rollTotal, this.diceRolls);

  factory GamePlayer.fromJson(Map<String, dynamic> map){
    var rolls = <DiceRoll>[];
    if (map.containsKey('diceValue')){
      var diceList = json.decode(map['diceValue']);
      for (var diceJson in diceList){
        rolls.add(DiceRoll.fromJson(diceJson));
      }
    }
    return GamePlayer(
      map['id'],
      map['nickname'],
      map['turnFinished'],
      map['winCount'],
      map['rollResult'] == null ? null : RollResult.getByValue(map['rollResult']),
      map['rollTotal'],
      rolls,
    );
  }
}

class DiceRoll {
  Dice dice;
  int value;
  DiceRoll(this.dice, this.value);

  factory DiceRoll.fromJson(Map<String, dynamic> map){
    return DiceRoll(
      Dice.values.byName(map['id'].toLowerCase()),
      map['value'],
    );
  }
}

class GameRound {
  bool isComplete;

  GameRound(this.isComplete);

  factory GameRound.fromJson(Map<String, dynamic> map){
    return GameRound(
      map['complete'],
    );
  }
}