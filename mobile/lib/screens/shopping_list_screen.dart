import 'package:flutter/material.dart';

import '../models/favorite.dart';
import '../services/api_client.dart';

class ShoppingListScreen extends StatefulWidget {
  const ShoppingListScreen({super.key});

  @override
  State<ShoppingListScreen> createState() => _ShoppingListScreenState();
}

class _ShoppingListScreenState extends State<ShoppingListScreen> {
  final _apiClient = ApiClient();
  final _controller = TextEditingController();
  Future<List<Favorite>>? _favorites;
  ShoppingComparison? _comparison;
  bool _comparing = false;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    setState(() {
      _favorites = _apiClient.getFavorites();
      _comparison = null;
    });
  }

  Future<void> _add() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    _controller.clear();
    await _apiClient.addFavorite(text);
    _reload();
  }

  Future<void> _remove(int id) async {
    await _apiClient.deleteFavorite(id);
    _reload();
  }

  Future<void> _compare() async {
    setState(() => _comparing = true);
    try {
      final result = await _apiClient.compareFavorites();
      setState(() => _comparison = result);
    } finally {
      if (mounted) setState(() => _comparing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mi lista de la compra')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      labelText: 'Ej. leche entera, aceite de oliva',
                    ),
                    onSubmitted: (_) => _add(),
                  ),
                ),
                IconButton(icon: const Icon(Icons.add), onPressed: _add),
              ],
            ),
          ),
          Expanded(child: _buildFavoritesList()),
          if (_comparison != null) _buildComparison(_comparison!),
          Padding(
            padding: const EdgeInsets.all(12),
            child: SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: _comparing ? null : _compare,
                icon: _comparing
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.compare_arrows),
                label: const Text('Comparar supermercados'),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFavoritesList() {
    return FutureBuilder<List<Favorite>>(
      future: _favorites,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        final favorites = snapshot.data ?? [];
        if (favorites.isEmpty) {
          return const Center(child: Text('Tu lista está vacía'));
        }
        return ListView.builder(
          itemCount: favorites.length,
          itemBuilder: (context, index) {
            final fav = favorites[index];
            return ListTile(
              title: Text(fav.query),
              subtitle: Text('Cantidad: ${fav.quantity}'),
              trailing: IconButton(
                icon: const Icon(Icons.delete_outline),
                onPressed: () => _remove(fav.id),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildComparison(ShoppingComparison comparison) {
    return Container(
      constraints: const BoxConstraints(maxHeight: 220),
      margin: const EdgeInsets.symmetric(horizontal: 12),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        border: Border.all(color: Theme.of(context).colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(8),
      ),
      child: ListView(
        shrinkWrap: true,
        children: comparison.chains.map((chain) {
          final isCheapest = chain.chain == comparison.cheapestChain;
          return ExpansionTile(
            title: Row(
              children: [
                Text(
                  chain.chain,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                if (isCheapest) ...[
                  const SizedBox(width: 6),
                  const Icon(Icons.emoji_events, color: Colors.amber, size: 18),
                ],
              ],
            ),
            subtitle: Text(
              '${chain.total.toStringAsFixed(2)} €'
              '${chain.missing.isNotEmpty ? " · faltan: ${chain.missing.join(', ')}" : ""}',
            ),
            children: chain.items.map((item) {
              return ListTile(
                dense: true,
                title: Text(item.matchedProduct?.name ?? item.query),
                subtitle: item.matchedProduct == null
                    ? const Text('Sin coincidencia en esta cadena')
                    : null,
                trailing: Text(
                  item.subtotal != null ? '${item.subtotal!.toStringAsFixed(2)} €' : '-',
                ),
              );
            }).toList(),
          );
        }).toList(),
      ),
    );
  }
}
