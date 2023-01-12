

class Statistics {
  final int diceRolled;
  final int roundsPlayed;
  final int gamesPlayed;
  final int outcomeTie;
  final int outcomeSipDrink;
  final int outcomeWinner;

  const Statistics({
    required this.diceRolled,
    required this.roundsPlayed,
    required this.gamesPlayed,
    required this.outcomeTie,
    required this.outcomeSipDrink,
    required this.outcomeWinner,
  });

  factory Statistics.fromJson(Map<String, dynamic> json) {
    return Statistics(
      diceRolled: json['dice_rolled'],
      roundsPlayed: json['rounds_played'],
      gamesPlayed: json['games_played'],
      outcomeTie: json['outcome_tie'],
      outcomeSipDrink: json['outcome_sip_drink'],
      outcomeWinner: json['outcome_winner'],
    );
  }
}
