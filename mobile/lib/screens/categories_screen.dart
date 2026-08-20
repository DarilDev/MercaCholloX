import 'package:flutter/material.dart';

import '../models/category.dart';
import '../services/api_client.dart';
import 'category_products_screen.dart';
import 'settings_screen.dart';

class CategoriesScreen extends StatefulWidget {
  const CategoriesScreen({super.key});

  @override
  State<CategoriesScreen> createState() => _CategoriesScreenState();
}

class _CategoriesScreenState extends State<CategoriesScreen> {
  final _apiClient = ApiClient();
  late Future<List<SupermarketCategory>> _categories;

  @override
  void initState() {
    super.initState();
    _categories = _apiClient.getCategories();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pasillos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const SettingsScreen()),
            ),
          ),
        ],
      ),
      body: FutureBuilder<List<SupermarketCategory>>(
        future: _categories,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text('Error cargando pasillos: ${snapshot.error}'),
              ),
            );
          }
          final categories = snapshot.data ?? [];
          if (categories.isEmpty) {
            return const Center(child: Text('Todavía no hay pasillos con datos'));
          }
          return ListView.builder(
            itemCount: categories.length,
            itemBuilder: (context, index) {
              final cat = categories[index];
              final breakdown = cat.chains.entries.map((e) => '${e.value} en ${e.key}').join(' · ');
              return ListTile(
                leading: const Icon(Icons.storefront_outlined),
                title: Text(cat.name),
                subtitle: Text(breakdown),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => CategoryProductsScreen(category: cat.name),
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
