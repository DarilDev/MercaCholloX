import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/category.dart';
import '../models/favorite.dart';
import '../models/product.dart';

class ApiClient {
  // URL del túnel ngrok (ver docs/DECISIONS.md — WSL2 no acepta conexiones
  // entrantes directas). El túnel gratuito cambia de URL cada vez que se
  // reinicia ngrok, así que esto habrá que actualizarlo si se reinicia.
  final String baseUrl;

  ApiClient({this.baseUrl = 'https://f70a-188-85-102-238.ngrok-free.app'});

  Future<dynamic> _get(String path, [Map<String, String>? query]) async {
    final uri = Uri.parse('$baseUrl$path').replace(queryParameters: query);
    final response = await http.get(uri);
    if (response.statusCode != 200) {
      throw Exception('Error ${response.statusCode} en $path');
    }
    return jsonDecode(utf8.decode(response.bodyBytes));
  }

  Future<List<Product>> searchProducts(String query) async {
    final data = await _get('/products/search', {'q': query}) as List<dynamic>;
    return data.map((e) => Product.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<SupermarketCategory>> getCategories() async {
    final data = await _get('/categories') as List<dynamic>;
    return data
        .map((e) => SupermarketCategory.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<Product>> getProducts({String? topCategory, String? category}) async {
    final query = <String, String>{
      if (topCategory != null) 'top_category': topCategory,
      if (category != null) 'category': category,
    };
    final data = await _get('/products', query) as List<dynamic>;
    return data.map((e) => Product.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<Favorite>> getFavorites() async {
    final data = await _get('/favorites') as List<dynamic>;
    return data.map((e) => Favorite.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> addFavorite(String query, {int quantity = 1}) async {
    final uri = Uri.parse('$baseUrl/favorites');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'query': query, 'quantity': quantity}),
    );
    if (response.statusCode != 200) {
      throw Exception('Error añadiendo a la lista: ${response.statusCode}');
    }
  }

  Future<void> deleteFavorite(int id) async {
    final uri = Uri.parse('$baseUrl/favorites/$id');
    final response = await http.delete(uri);
    if (response.statusCode != 200) {
      throw Exception('Error borrando de la lista: ${response.statusCode}');
    }
  }

  Future<ShoppingComparison> compareFavorites() async {
    final data = await _get('/favorites/compare') as Map<String, dynamic>;
    return ShoppingComparison.fromJson(data);
  }
}
