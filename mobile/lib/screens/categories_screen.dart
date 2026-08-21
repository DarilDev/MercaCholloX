import 'package:flutter/material.dart';

import '../services/api_client.dart';
import '../widgets/error_view.dart';
import '../widgets/loading_view.dart';
import 'chain_categories_screen.dart';
import 'settings_screen.dart';

class CategoriesScreen extends StatefulWidget {
  const CategoriesScreen({super.key});

  @override
  State<CategoriesScreen> createState() => _CategoriesScreenState();
}

class _CategoriesScreenState extends State<CategoriesScreen> {
  final _apiClient = ApiClient();
  late Future<List<String>> _chains;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    setState(() => _chains = _apiClient.getChains());
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
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const LoadingView();
          }
          if (snapshot.hasError) {
            return ErrorView(error: snapshot.error!, onRetry: _load);
          }
          final chains = snapshot.data ?? [];
          if (chains.isEmpty) {
            return const Center(child: Text('Todavía no hay cadenas con datos'));
          }
          return ListView.builder(
            itemCount: chains.length,
            itemBuilder: (context, index) {
              final chain = chains[index];
              return ListTile(
                leading: const Icon(Icons.storefront_outlined),
                title: Text(_capitalize(chain)),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => ChainCategoriesScreen(chain: chain),
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
