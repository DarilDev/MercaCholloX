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

// Dominio real de cada cadena, para pedir su icono de marca (favicon) —
// ver Image.network más abajo. Una cadena nueva sin dominio aquí simplemente
// cae al icono genérico, no rompe nada.
const _chainDomains = {
  'mercadona': 'mercadona.es',
  'dia': 'dia.es',
  'hiperdino': 'hiperdino.es',
  'aldi': 'aldi.es',
  'lidl': 'lidl.es',
};

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
        title: const Text('Supermercados'),
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
              final domain = _chainDomains[chain];
              return ListTile(
                leading: domain == null
                    ? const Icon(Icons.storefront_outlined)
                    : ClipRRect(
                        borderRadius: BorderRadius.circular(6),
                        child: Image.network(
                          'https://www.google.com/s2/favicons?domain=$domain&sz=64',
                          width: 32,
                          height: 32,
                          errorBuilder: (context, error, stack) =>
                              const Icon(Icons.storefront_outlined),
                        ),
                      ),
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
