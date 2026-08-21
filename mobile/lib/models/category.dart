class SupermarketCategory {
  final String name;
  final int count;

  SupermarketCategory({required this.name, required this.count});

  factory SupermarketCategory.fromJson(Map<String, dynamic> json) {
    return SupermarketCategory(
      name: json['name'] as String,
      count: json['count'] as int,
    );
  }
}
