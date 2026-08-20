class WorthItResult {
  final String chain;
  final String usualChain;
  final double detourExtraKm;
  final double detourExtraMin;
  final double fuelCostEur;
  final double timeCostEur;
  final double basketSavingsEur;
  final double netSavingsEur;
  final bool worthIt;

  WorthItResult({
    required this.chain,
    required this.usualChain,
    required this.detourExtraKm,
    required this.detourExtraMin,
    required this.fuelCostEur,
    required this.timeCostEur,
    required this.basketSavingsEur,
    required this.netSavingsEur,
    required this.worthIt,
  });

  factory WorthItResult.fromJson(Map<String, dynamic> json) {
    return WorthItResult(
      chain: json['chain'] as String,
      usualChain: json['usual_chain'] as String,
      detourExtraKm: (json['detour_extra_km'] as num).toDouble(),
      detourExtraMin: (json['detour_extra_min'] as num).toDouble(),
      fuelCostEur: (json['fuel_cost_eur'] as num).toDouble(),
      timeCostEur: (json['time_cost_eur'] as num).toDouble(),
      basketSavingsEur: (json['basket_savings_eur'] as num).toDouble(),
      netSavingsEur: (json['net_savings_eur'] as num).toDouble(),
      worthIt: json['worth_it'] as bool,
    );
  }
}
