import 'package:flutter/material.dart';

import '../models/worth_it.dart';
import '../theme.dart';

String _capitalize(String s) => s.isEmpty ? s : '${s[0].toUpperCase()}${s.substring(1)}';

String _eur(double v) => '${v.toStringAsFixed(2)} €';

/// El veredicto va primero y grande, con color — no una lista de números.
/// El desglose completo (cesta, gasolina, tiempo) queda siempre disponible
/// pero en segundo plano (expandible): mismo principio de transparencia que
/// ya se aplica al matching de favoritos, nunca caja negra por detrás del
/// veredicto.
class WorthItCard extends StatelessWidget {
  final WorthItResult result;

  const WorthItCard({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final color = result.worthIt ? AppColors.success : Colors.grey.shade600;
    final chainName = _capitalize(result.chain);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            color: color.withValues(alpha: 0.12),
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(
                  result.worthIt ? Icons.check_circle : Icons.cancel_outlined,
                  color: color,
                  size: 32,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        result.worthIt ? 'Vale la pena ir a $chainName' : 'No compensa ir a $chainName',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: color,
                            ),
                      ),
                      const SizedBox(height: 2),
                      Text(_headline(), style: Theme.of(context).textTheme.bodyMedium),
                    ],
                  ),
                ),
              ],
            ),
          ),
          ExpansionTile(
            title: const Text('Ver desglose'),
            childrenPadding: const EdgeInsets.only(bottom: 8),
            children: [
              _breakdownRow(
                'Ahorro en la cesta vs. ${_capitalize(result.usualChain)}',
                result.basketSavingsEur,
              ),
              _breakdownRow('Coste gasolina del desvío', -result.fuelCostEur),
              _breakdownRow('Coste del tiempo del desvío', -result.timeCostEur),
              const Divider(height: 1),
              _breakdownRow('Ahorro neto', result.netSavingsEur, bold: true),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                child: Text(
                  'Desvío: ${result.detourExtraKm.toStringAsFixed(1)} km · '
                  '${result.detourExtraMin.toStringAsFixed(0)} min extra',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _headline() {
    if (result.worthIt) {
      return 'Ahorras ${_eur(result.netSavingsEur)} en total';
    }
    if (result.netSavingsEur > 0) {
      return 'Solo ahorrarías ${_eur(result.netSavingsEur)}, no llega a compensar el desvío';
    }
    return 'Perderías ${_eur(-result.netSavingsEur)} con el desvío';
  }

  Widget _breakdownRow(String label, double value, {bool bold = false}) {
    final style = TextStyle(fontWeight: bold ? FontWeight.bold : FontWeight.normal);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        children: [
          Expanded(child: Text(label, style: style)),
          Text(
            '${value >= 0 ? '+' : ''}${_eur(value)}',
            style: style.copyWith(color: value < 0 ? AppColors.danger : AppColors.success),
          ),
        ],
      ),
    );
  }
}
