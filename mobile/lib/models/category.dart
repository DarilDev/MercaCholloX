class SupermarketCategory {
  final String name;
  final Map<String, int> chains; // cadena -> nº de productos cacheados

  SupermarketCategory({required this.name, required this.chains});

  int get totalProducts => chains.values.fold(0, (a, b) => a + b);

  factory SupermarketCategory.fromJson(Map<String, dynamic> json) {
    return SupermarketCategory(
      name: json['name'] as String,
      chains: Map<String, int>.from(json['chains'] as Map),
    );
  }
}
