import 'package:flutter/material.dart';

import '../models/category.dart';
import '../services/api_client.dart';
import 'settings_screen.dart';
import 'subcategories_screen.dart';

class CategoriesScreen extends StatefulWidget {
  const CategoriesScreen({super.key});

  @override
  State<CategoriesScreen> createState() => _CategoriesScreenState();
}

class _CategoriesScreenState extends State<CategoriesScreen> {
  final _apiClient = ApiClient();
  late Future<List<String>> _chains;
  String? _selectedChain;
  Future<List<SupermarketCategory>>? _categories;

  @override
  void initState() {
    super.initState();
    _chains = _apiClient.getChains().then((chains) {
      if (chains.isNotEmpty) _selectChain(chains.first);
      return chains;
    });
  }

  void _selectChain(String chain) {
    setState(() {
      _selectedChain = chain;
      _categories = _apiClient.getCategories(chain);
    });
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
      body: FutureBuilder<List<String>>(
        future: _chains,
        builder: (context, chainsSnapshot) {
          if (chainsSnapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (chainsSnapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text('Error cargando cadenas: ${chainsSnapshot.error}'),
              ),
            );
          }
          final chains = chainsSnapshot.data ?? [];
          if (chains.isEmpty) {
            return const Center(child: Text('Todavía no hay ninguna cadena con datos'));
          }
          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(12),
                child: SegmentedButton<String>(
                  segments: chains
                      .map((c) => ButtonSegment(value: c, label: Text(c)))
                      .toList(),
                  selected: {_selectedChain ?? chains.first},
                  onSelectionChanged: (selection) => _selectChain(selection.first),
                ),
              ),
              Expanded(child: _buildCategoryList()),
            ],
          );
        },
      ),
    );
  }

  Widget _buildCategoryList() {
    return FutureBuilder<List<SupermarketCategory>>(
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
                MaterialPageRoute(
                  builder: (_) => SubcategoriesScreen(
                    chain: _selectedChain!,
                    category: cat,
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }
}
