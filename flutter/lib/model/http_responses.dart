

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
      diceRolled: json['dice_rolled'] ?? 0,
      roundsPlayed: json['rounds_played'] ?? 0,
      gamesPlayed: json['games_played'] ?? 0,
      outcomeTie: json['outcome_tie'] ?? 0,
      outcomeSipDrink: json['outcome_sip_drink'] ?? 0,
      outcomeWinner: json['outcome_winner'] ?? 0,
    );
  }
}
