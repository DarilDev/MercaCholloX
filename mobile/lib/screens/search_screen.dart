import 'dart:async';

import 'package:flutter/material.dart';

import '../models/product.dart';
import '../services/api_client.dart';
import '../widgets/error_view.dart';
import '../widgets/loading_view.dart';
import '../widgets/product_tile.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _apiClient = ApiClient();
  final _controller = TextEditingController();
  Timer? _debounce;
  Future<List<Product>>? _results;

  @override
  void dispose() {
    _debounce?.cancel();
    _controller.dispose();
    super.dispose();
  }

  void _search() {
    final query = _controller.text.trim();
    if (query.length < 2) {
      setState(() => _results = null);
      return;
    }
    setState(() {
      _results = _apiClient.searchProducts(query);
    });
  }

  // Buscar en cuanto se escribe, no solo al enviar — la mayoría de la gente
  // no sabe de memoria el nombre exacto del producto, así que ver resultados
  // mientras escribe ayuda a "adivinar" en vez de exigir el término exacto.
  void _onChanged(String _) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 350), _search);
  }

  void _addToList(Product product) async {
    await _apiClient.addFavorite(product.name, quantity: 1);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Añadido a la lista: ${product.name}')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Buscar')),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      labelText: 'Buscar producto (ej. leche, aceite)',
                    ),
                    onChanged: _onChanged,
                    onSubmitted: (_) => _search(),
                  ),
                ),
                IconButton(icon: const Icon(Icons.search), onPressed: _search),
              ],
            ),
            const SizedBox(height: 12),
            Expanded(child: _buildResults()),
          ],
        ),
      ),
    );
  }

  Widget _buildResults() {
    if (_results == null) {
      return const Center(child: Text('Busca un producto para ver precios reales'));
    }
    return FutureBuilder<List<Product>>(
      future: _results,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const LoadingView();
        }
        if (snapshot.hasError) {
          return ErrorView(error: snapshot.error!, onRetry: _search);
        }
        final products = snapshot.data ?? [];
        if (products.isEmpty) {
          return const Center(child: Text('Sin resultados en la caché local'));
        }
        return ListView.builder(
          itemCount: products.length,
          itemBuilder: (context, index) {
            final product = products[index];
            return ProductTile(product: product, onAdd: () => _addToList(product));
          },
        );
      },
    );
  }
}
