import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../models/price_history.dart';
import '../models/product.dart';
import '../services/api_client.dart';
import '../theme.dart';
import '../widgets/error_view.dart';
import '../widgets/loading_view.dart';

class ProductDetailScreen extends StatefulWidget {
  final Product product;

  const ProductDetailScreen({super.key, required this.product});

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  final _apiClient = ApiClient();
  late Future<PriceHistory> _history;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    setState(() => _history = _apiClient.getPriceHistory(widget.product.id));
  }

  @override
  Widget build(BuildContext context) {
    final product = widget.product;
    return Scaffold(
      appBar: AppBar(title: Text(product.name)),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.md),
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: 96,
                height: 96,
                child: product.imageUrl != null
                    ? Image.network(
                        product.imageUrl!,
                        fit: BoxFit.contain,
                        errorBuilder: (context, error, stack) =>
                            const Icon(Icons.image_not_supported_outlined, size: 40),
                      )
                    : const Icon(Icons.shopping_basket_outlined, size: 40),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(product.name, style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: AppSpacing.xs),
                    Text(
                      product.price != null ? '${product.price!.toStringAsFixed(2)} €' : '-',
                      style: Theme.of(context)
                          .textTheme
                          .headlineSmall
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    Text('${product.chain} · ${product.category ?? product.topCategory ?? ''}'),
                  ],
                ),
              ),
            ],
          ),
          const Divider(height: 32),
          Text('Historial de precio', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: AppSpacing.sm),
          FutureBuilder<PriceHistory>(
            future: _history,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const SizedBox(height: 180, child: LoadingView());
              }
              if (snapshot.hasError) {
                return ErrorView(error: snapshot.error!, onRetry: _load);
              }
              final history = snapshot.data!;
              if (history.points.length < 2) {
                return const Text('Todavía no hay histórico suficiente para este producto.');
              }
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (history.discountLabel != null)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppSpacing.sm,
                        vertical: AppSpacing.xs,
                      ),
                      decoration: BoxDecoration(
                        color: history.discountLabel!.startsWith('▼')
                            ? AppColors.success.withValues(alpha: 0.12)
                            : Theme.of(context).colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        history.discountLabel!,
                        style: TextStyle(
                          color: history.discountLabel!.startsWith('▼') ? AppColors.success : null,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  const SizedBox(height: AppSpacing.md),
                  AspectRatio(
                    aspectRatio: 1.8,
                    child: _PriceChart(points: history.points),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class _PriceChart extends StatelessWidget {
  final List<PricePoint> points;

  const _PriceChart({required this.points});

  @override
  Widget build(BuildContext context) {
    final prices = points.map((p) => p.price).toList();
    final minPrice = prices.reduce((a, b) => a < b ? a : b);
    final maxPrice = prices.reduce((a, b) => a > b ? a : b);
    // margen para que la línea no toque los bordes cuando el precio no varía
    final padding = (maxPrice - minPrice) * 0.15 + 0.05;

    return LineChart(
      LineChartData(
        minY: minPrice - padding,
        maxY: maxPrice + padding,
        lineTouchData: LineTouchData(
          touchTooltipData: LineTouchTooltipData(
            getTooltipItems: (spots) => spots.map((s) {
              final point = points[s.x.toInt()];
              return LineTooltipItem(
                '${point.price.toStringAsFixed(2)} €\n${_shortDate(point.capturedAt)}',
                const TextStyle(fontWeight: FontWeight.bold),
              );
            }).toList(),
          ),
        ),
        titlesData: FlTitlesData(
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 44,
              getTitlesWidget: (value, meta) =>
                  Text('${value.toStringAsFixed(2)}€', style: const TextStyle(fontSize: 10)),
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 24,
              interval: (points.length / 4).ceilToDouble().clamp(1, points.length.toDouble()),
              getTitlesWidget: (value, meta) {
                final index = value.toInt();
                if (index < 0 || index >= points.length) return const SizedBox.shrink();
                return Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(_shortDate(points[index].capturedAt), style: const TextStyle(fontSize: 10)),
                );
              },
            ),
          ),
        ),
        gridData: const FlGridData(drawVerticalLine: false),
        borderData: FlBorderData(show: true, border: Border.all(color: Colors.grey.shade300)),
        lineBarsData: [
          LineChartBarData(
            spots: [
              for (var i = 0; i < points.length; i++) FlSpot(i.toDouble(), points[i].price),
            ],
            isCurved: false,
            barWidth: 3,
            color: AppColors.success,
            dotData: const FlDotData(show: true),
            belowBarData: BarAreaData(show: true, color: AppColors.success.withValues(alpha: 0.1)),
          ),
        ],
      ),
    );
  }

  String _shortDate(DateTime d) => '${d.day}/${d.month}';
}
