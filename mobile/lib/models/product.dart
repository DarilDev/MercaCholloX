class Product {
  final int id;
  final String chain;
  final String externalId;
  final String name;
  final String? topCategory;
  final String? category;
  final String? unit;
  final String? imageUrl;
  final double? price;

  Product({
    required this.id,
    required this.chain,
    required this.externalId,
    required this.name,
    required this.topCategory,
    required this.category,
    required this.unit,
    required this.imageUrl,
    required this.price,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as int,
      chain: json['chain'] as String,
      externalId: json['external_id'] as String,
      name: json['name'] as String,
      topCategory: json['top_category'] as String?,
      category: json['category'] as String?,
      unit: json['unit'] as String?,
      imageUrl: json['image_url'] as String?,
      price: (json['price'] as num?)?.toDouble(),
    );
  }
}
