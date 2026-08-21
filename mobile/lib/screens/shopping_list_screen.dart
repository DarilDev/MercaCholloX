import 'package:flutter/material.dart';

import '../models/favorite.dart';
import '../models/profile.dart';
import '../models/worth_it.dart';
import '../services/api_client.dart';
import '../theme.dart';
import '../widgets/error_view.dart';
import '../widgets/loading_view.dart';
import '../widgets/worth_it_card.dart';

class ShoppingListScreen extends StatefulWidget {
  const ShoppingListScreen({super.key});

  @override
  State<ShoppingListScreen> createState() => _ShoppingListScreenState();
}

class _ShoppingListScreenState extends State<ShoppingListScreen> {
  final _apiClient = ApiClient();
  final _controller = TextEditingController();
  Future<List<Favorite>>? _favorites;
  UserProfile? _profile;
  ShoppingComparison? _comparison;
  List<WorthItResult>? _worthItResults;
  bool _comparing = false;

  @override
  void initState() {
    super.initState();
    _reload();
    _apiClient.getProfile().then((p) {
      if (mounted) setState(() => _profile = p);
    });
  }

  void _reload() {
    setState(() {
      _favorites = _apiClient.getFavorites();
      _comparison = null;
      _worthItResults = null;
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
      // Con casa fijada en el perfil, el "vale la pena el desvío" es
      // estrictamente más útil que el total desnudo — lo sustituye, no lo
      // añade, para no duplicar la misma decisión con dos vistas distintas.
      if (_profile?.homeLat != null && _profile?.homeLon != null) {
        final result = await _apiClient.getWorthIt();
        setState(() {
          _worthItResults = result;
          _comparison = null;
        });
      } else {
        final result = await _apiClient.compareFavorites();
        setState(() {
          _comparison = result;
          _worthItResults = null;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
      }
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
          if (_worthItResults != null) _buildWorthIt(_worthItResults!),
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
          return const LoadingView();
        }
        if (snapshot.hasError) {
          return ErrorView(error: snapshot.error!, onRetry: _reload);
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

  Widget _buildWorthIt(List<WorthItResult> results) {
    if (results.isEmpty) {
      return const Padding(
        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Text(
          'No hay otra cadena cercana con la que comparar tu cesta ahora mismo.',
          textAlign: TextAlign.center,
        ),
      );
    }
    return ConstrainedBox(
      constraints: const BoxConstraints(maxHeight: 320),
      child: ListView(
        shrinkWrap: true,
        children: results.map((r) => WorthItCard(result: r)).toList(),
      ),
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
                  const Icon(Icons.emoji_events, color: AppColors.starred, size: 18),
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
