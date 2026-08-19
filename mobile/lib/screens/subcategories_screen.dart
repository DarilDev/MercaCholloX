import 'package:flutter/material.dart';

import '../models/category.dart';
import 'category_products_screen.dart';

class SubcategoriesScreen extends StatelessWidget {
  final SupermarketCategory category;

  const SubcategoriesScreen({super.key, required this.category});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(category.name)),
      body: ListView.builder(
        itemCount: category.subcategories.length,
        itemBuilder: (context, index) {
          final sub = category.subcategories[index];
          return ListTile(
            title: Text(sub),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => CategoryProductsScreen(
                  topCategory: category.name,
                  category: sub,
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
