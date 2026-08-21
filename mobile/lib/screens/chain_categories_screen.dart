import 'package:flutter/material.dart';

import '../models/category.dart';
import '../services/api_client.dart';
import '../widgets/error_view.dart';
import '../widgets/loading_view.dart';
import 'category_products_screen.dart';

class ChainCategoriesScreen extends StatefulWidget {
  final String chain;

  const ChainCategoriesScreen({super.key, required this.chain});

  @override
  State<ChainCategoriesScreen> createState() => _ChainCategoriesScreenState();
}

class _ChainCategoriesScreenState extends State<ChainCategoriesScreen> {
  final _apiClient = ApiClient();
  late Future<List<SupermarketCategory>> _categories;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    setState(() => _categories = _apiClient.getCategories(widget.chain));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(_capitalize(widget.chain))),
      body: FutureBuilder<List<SupermarketCategory>>(
        future: _categories,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const LoadingView();
          }
          if (snapshot.hasError) {
            return ErrorView(error: snapshot.error!, onRetry: _load);
          }
          final categories = snapshot.data ?? [];
          if (categories.isEmpty) {
            return const Center(child: Text('Todavía no hay pasillos con datos'));
          }
          return ListView.builder(
            itemCount: categories.length,
            itemBuilder: (context, index) {
              final cat = categories[index];
              return ListTile(
                title: Text(cat.name),
                subtitle: Text('${cat.count} productos'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => CategoryProductsScreen(chain: widget.chain, category: cat.name),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

String _capitalize(String s) => s.isEmpty ? s : '${s[0].toUpperCase()}${s.substring(1)}';
