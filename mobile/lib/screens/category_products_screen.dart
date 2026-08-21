import 'package:flutter/material.dart';

import '../models/product.dart';
import '../services/api_client.dart';
import '../widgets/error_view.dart';
import '../widgets/loading_view.dart';
import '../widgets/product_tile.dart';

class CategoryProductsScreen extends StatefulWidget {
  final String chain;
  final String category;

  const CategoryProductsScreen({super.key, required this.chain, required this.category});

  @override
  State<CategoryProductsScreen> createState() => _CategoryProductsScreenState();
}

class _CategoryProductsScreenState extends State<CategoryProductsScreen> {
  final _apiClient = ApiClient();
  late Future<List<Product>> _products;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    setState(() => _products = _apiClient.getProducts(widget.chain, widget.category));
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
      appBar: AppBar(title: Text(widget.category)),
      body: FutureBuilder<List<Product>>(
        future: _products,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const LoadingView();
          }
          if (snapshot.hasError) {
            return ErrorView(error: snapshot.error!, onRetry: _load);
          }
          final products = snapshot.data ?? [];
          if (products.isEmpty) {
            return const Center(child: Text('Sin productos cacheados aquí todavía'));
          }
          return ListView.builder(
            itemCount: products.length,
            itemBuilder: (context, index) {
              final product = products[index];
              return ProductTile(
                product: product,
                onAdd: () => _addToList(product),
              );
            },
          );
        },
      ),
    );
  }
}
