class PricePoint {
  final double price;
  final DateTime capturedAt;

  PricePoint({required this.price, required this.capturedAt});

  factory PricePoint.fromJson(Map<String, dynamic> json) {
    return PricePoint(
      price: (json['price'] as num).toDouble(),
      capturedAt: DateTime.parse(json['captured_at'] as String),
    );
  }
}

class PriceHistory {
  final List<PricePoint> points;
  final String? discountLabel;

  PriceHistory({required this.points, required this.discountLabel});

  factory PriceHistory.fromJson(Map<String, dynamic> json) {
    return PriceHistory(
      points: (json['points'] as List)
          .map((e) => PricePoint.fromJson(e as Map<String, dynamic>))
          .toList(),
      discountLabel: json['discount_label'] as String?,
    );
  }
}
