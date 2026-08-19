import 'package:flutter/material.dart';

import '../models/category.dart';
import '../services/api_client.dart';
import 'subcategories_screen.dart';

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
      appBar: AppBar(title: const Text('Pasillos')),
      body: FutureBuilder<List<SupermarketCategory>>(
        future: _categories,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          final categories = snapshot.data ?? [];
          return ListView.builder(
            itemCount: categories.length,
            itemBuilder: (context, index) {
              final cat = categories[index];
              return ListTile(
                leading: const Icon(Icons.storefront_outlined),
                title: Text(cat.name),
                subtitle: Text('${cat.subcategories.length} subcategorías'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => SubcategoriesScreen(category: cat)),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
