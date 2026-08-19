import 'package:flutter/material.dart';

import '../services/backend_config.dart';
import '../services/device_identity.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _urlController = TextEditingController();
  String _deviceId = '';
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final url = await BackendConfig.getBaseUrl();
    final deviceId = await DeviceIdentity.getOrCreate();
    setState(() {
      _urlController.text = url;
      _deviceId = deviceId;
      _loading = false;
    });
  }

  Future<void> _save() async {
    await BackendConfig.setBaseUrl(_urlController.text);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Guardado. Reinicia la app para aplicarlo del todo.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ajustes')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('URL del backend'),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _urlController,
                    decoration: const InputDecoration(
                      hintText: 'https://...',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  FilledButton(onPressed: _save, child: const Text('Guardar')),
                  const SizedBox(height: 32),
                  Text(
                    'Id de este dispositivo (para separar tu lista de la de otros):',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  SelectableText(_deviceId, style: Theme.of(context).textTheme.bodySmall),
                ],
              ),
            ),
    );
  }
}
