import 'package:flutter/material.dart';

import '../models/scan_history_entry.dart';
import '../services/api_client.dart';
import '../utils/add_to_list.dart';
import '../widgets/error_view.dart';
import '../widgets/loading_view.dart';

class ScanHistoryScreen extends StatefulWidget {
  const ScanHistoryScreen({super.key});

  @override
  State<ScanHistoryScreen> createState() => _ScanHistoryScreenState();
}

class _ScanHistoryScreenState extends State<ScanHistoryScreen> {
  final _apiClient = ApiClient();
  late Future<List<ScanHistoryEntry>> _history;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    setState(() => _history = _apiClient.getScanHistory());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Historial de escaneos')),
      body: FutureBuilder<List<ScanHistoryEntry>>(
        future: _history,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const LoadingView();
          }
          if (snapshot.hasError) {
            return ErrorView(error: snapshot.error!, onRetry: _load);
          }
          final entries = snapshot.data ?? [];
          if (entries.isEmpty) {
            return const Center(child: Text('Todavía no has escaneado nada'));
          }
          return ListView.builder(
            itemCount: entries.length,
            itemBuilder: (context, index) {
              final entry = entries[index];
              return ListTile(
                leading: SizedBox(
                  width: 44,
                  height: 44,
                  child: entry.imageUrl != null
                      ? Image.network(
                          entry.imageUrl!,
                          fit: BoxFit.contain,
                          errorBuilder: (context, error, stack) =>
                              const Icon(Icons.image_not_supported_outlined),
                        )
                      : const Icon(Icons.qr_code),
                ),
                title: Text(entry.name ?? entry.ean),
                subtitle: entry.nutriscoreGrade != null
                    ? Text('Nutri-Score ${entry.nutriscoreGrade}')
                    : null,
                trailing: entry.name == null
                    ? null
                    : IconButton(
                        icon: const Icon(Icons.add_shopping_cart),
                        onPressed: () => addToShoppingList(context, _apiClient, entry.name!),
                      ),
              );
            },
          );
        },
      ),
    );
  }
}
