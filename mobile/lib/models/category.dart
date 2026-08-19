class SupermarketCategory {
  final String name;
  final List<String> subcategories;

  SupermarketCategory({required this.name, required this.subcategories});

  factory SupermarketCategory.fromJson(Map<String, dynamic> json) {
    return SupermarketCategory(
      name: json['name'] as String,
      subcategories: (json['subcategories'] as List).cast<String>(),
    );
  }
}
