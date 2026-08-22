import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/category.dart';
import '../models/favorite.dart';
import '../models/geocode_result.dart';
import '../models/price_history.dart';
import '../models/product.dart';
import '../models/profile.dart';
import '../models/scan_result.dart';
import '../models/store.dart';
import '../models/worth_it.dart';
import 'backend_config.dart';
import 'device_identity.dart';

class ApiClient {
  Future<Map<String, String>> _headers([Map<String, String>? extra]) async {
    final deviceId = await DeviceIdentity.getOrCreate();
    return {'X-Device-Id': deviceId, ...?extra};
  }

  Future<Uri> _uri(String path, [Map<String, String>? query]) async {
    final baseUrl = await BackendConfig.getBaseUrl();
    return Uri.parse('$baseUrl$path').replace(queryParameters: query);
  }

  Future<dynamic> _get(String path, [Map<String, String>? query]) async {
    final response = await http.get(await _uri(path, query), headers: await _headers());
    if (response.statusCode != 200) {
      throw Exception('${response.statusCode}: ${_errorDetail(response)}');
    }
    return jsonDecode(utf8.decode(response.bodyBytes));
  }

  String _errorDetail(http.Response response) {
    try {
      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (body is Map && body['detail'] is String) return body['detail'] as String;
    } catch (_) {
      // cuerpo no-JSON (ej. 502 de un servicio caído) — se usa el texto crudo
    }
    return 'Error en ${response.request?.url.path}';
  }

  Future<List<Product>> searchProducts(String query) async {
    final data = await _get('/products/search', {'q': query}) as List<dynamic>;
    return data.map((e) => Product.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<String>> getChains() async {
    final data = await _get('/chains') as List<dynamic>;
    return data.cast<String>();
  }

  Future<List<SupermarketCategory>> getCategories(String chain) async {
    final data = await _get('/categories', {'chain': chain}) as List<dynamic>;
    return data
        .map((e) => SupermarketCategory.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<Product>> getProducts(String chain, String category) async {
    final data = await _get('/products', {'chain': chain, 'category': category}) as List<dynamic>;
    return data.map((e) => Product.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<PriceHistory> getPriceHistory(int productId) async {
    final data = await _get('/products/$productId/price_history') as Map<String, dynamic>;
    return PriceHistory.fromJson(data);
  }

  Future<List<GeocodeResult>> geocode(String query) async {
    final data = await _get('/geocode', {'q': query}) as List<dynamic>;
    return data.map((e) => GeocodeResult.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<Favorite>> getFavorites() async {
    final data = await _get('/favorites') as List<dynamic>;
    return data.map((e) => Favorite.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> addFavorite(String query, {int quantity = 1}) async {
    final response = await http.post(
      await _uri('/favorites'),
      headers: await _headers({'Content-Type': 'application/json'}),
      body: jsonEncode({'query': query, 'quantity': quantity}),
    );
    if (response.statusCode != 200) {
      throw Exception('Error añadiendo a la lista: ${response.statusCode}');
    }
  }

  Future<void> deleteFavorite(int id) async {
    final response = await http.delete(await _uri('/favorites/$id'), headers: await _headers());
    if (response.statusCode != 200) {
      throw Exception('Error borrando de la lista: ${response.statusCode}');
    }
  }

  Future<ShoppingComparison> compareFavorites() async {
    final data = await _get('/favorites/compare') as Map<String, dynamic>;
    return ShoppingComparison.fromJson(data);
  }

  Future<UserProfile> getProfile() async {
    final data = await _get('/profile') as Map<String, dynamic>;
    return UserProfile.fromJson(data);
  }

  Future<UserProfile> updateProfile(UserProfile profile) async {
    final response = await http.put(
      await _uri('/profile'),
      headers: await _headers({'Content-Type': 'application/json'}),
      body: jsonEncode(profile.toJson()),
    );
    if (response.statusCode != 200) {
      throw Exception('Error guardando el perfil: ${response.statusCode}');
    }
    return UserProfile.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
  }

  Future<List<WorthItResult>> getWorthIt() async {
    final data = await _get('/worth-it') as List<dynamic>;
    return data.map((e) => WorthItResult.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<ScanResult> scanBarcode(String ean) async {
    final data = await _get('/products/scan/$ean') as Map<String, dynamic>;
    return ScanResult.fromJson(data);
  }

  Future<List<NearbyStore>> getNearbyStores(double lat, double lon, {double radiusKm = 3}) async {
    final data = await _get('/stores/nearby', {
      'lat': lat.toString(),
      'lon': lon.toString(),
      'radius_km': radiusKm.toString(),
    }) as List<dynamic>;
    return data.map((e) => NearbyStore.fromJson(e as Map<String, dynamic>)).toList();
  }
}
