class ScanHistoryEntry {
  final int id;
  final String ean;
  final String? name;
  final String? imageUrl;
  final String? nutriscoreGrade;
  final String scannedAt;

  ScanHistoryEntry({
    required this.id,
    required this.ean,
    required this.name,
    required this.imageUrl,
    required this.nutriscoreGrade,
    required this.scannedAt,
  });

  factory ScanHistoryEntry.fromJson(Map<String, dynamic> json) {
    return ScanHistoryEntry(
      id: json['id'] as int,
      ean: json['ean'] as String,
      name: json['name'] as String?,
      imageUrl: json['image_url'] as String?,
      nutriscoreGrade: json['nutriscore_grade'] as String?,
      scannedAt: json['scanned_at'] as String,
    );
  }
}
