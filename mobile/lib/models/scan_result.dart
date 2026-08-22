import 'product.dart';

class ScanResult {
  final String ean;
  final String? name;
  final String? imageUrl;
  final String? nutriscoreGrade;
  final int? novaGroup;
  final int additivesCount;
  final Product? matchedProduct;

  ScanResult({
    required this.ean,
    required this.name,
    required this.imageUrl,
    required this.nutriscoreGrade,
    required this.novaGroup,
    required this.additivesCount,
    required this.matchedProduct,
  });

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    return ScanResult(
      ean: json['ean'] as String,
      name: json['name'] as String?,
      imageUrl: json['image_url'] as String?,
      nutriscoreGrade: json['nutriscore_grade'] as String?,
      novaGroup: json['nova_group'] as int?,
      additivesCount: json['additives_count'] as int,
      matchedProduct: json['matched_product'] != null
          ? Product.fromJson(json['matched_product'] as Map<String, dynamic>)
          : null,
    );
  }
}
