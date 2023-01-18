

class Statistics {
  final int diceRolled;
  final int roundsPlayed;
  final int gamesPlayed;
  final int outcomeTie;
  final int outcomeSipDrink;
  final int outcomeWinner;
  final int outcomeFinishDrink;
  final int outcomeDualWield;
  final int outcomeShower;
  final int outcomeHeadOnTable;
  final int outcomeWishPurchase;
  final int outcomePool;

  const Statistics({
    required this.diceRolled,
    required this.roundsPlayed,
    required this.gamesPlayed,
    required this.outcomeTie,
    required this.outcomeSipDrink,
    required this.outcomeWinner,
    required this.outcomeFinishDrink,
    required this.outcomeDualWield,
    required this.outcomeShower,
    required this.outcomeHeadOnTable,
    required this.outcomeWishPurchase,
    required this.outcomePool,
  });

  factory Statistics.fromJson(Map<String, dynamic> json) {
    return Statistics(
      diceRolled: json['dice_rolled'] ?? 0,
      roundsPlayed: json['rounds_played'] ?? 0,
      gamesPlayed: json['games_played'] ?? 0,
      outcomeTie: json['outcome_tie'] ?? 0,
      outcomeSipDrink: json['outcome_sip_drink'] ?? 0,
      outcomeWinner: json['outcome_winner'] ?? 0,
      outcomeFinishDrink: json['outcome_finish_drink'] ?? 0,
      outcomeDualWield: json['outcome_dual_wield'] ?? 0,
      outcomeShower: json['outcome_shower'] ?? 0,
      outcomeHeadOnTable: json['outcome_head_on_table'] ?? 0,
      outcomeWishPurchase: json['outcome_wish_purchase'] ?? 0,
      outcomePool: json['outcome_pool'] ?? 0,
    );
  }
}
