class GeocodeResult {
  final String label;
  final double lat;
  final double lon;

  GeocodeResult({required this.label, required this.lat, required this.lon});

  factory GeocodeResult.fromJson(Map<String, dynamic> json) {
    return GeocodeResult(
      label: json['label'] as String,
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
    );
  }
}
