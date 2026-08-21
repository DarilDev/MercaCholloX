import 'dart:async';

import 'package:flutter/material.dart';

import '../models/geocode_result.dart';
import '../services/api_client.dart';

/// Campo de dirección con autocompletado — alternativa a "usar mi ubicación"
/// para fijar casa/trabajo sin tener que estar físicamente en el sitio (ej.
/// fijar el trabajo desde el sofá). Espera a que el usuario deje de escribir
/// antes de consultar /geocode: Photon/Nominatim son servicios públicos
/// gratuitos limitados a ~1 petición/segundo, no hay que machacarlos con una
/// consulta por cada letra.
class AddressSearchField extends StatefulWidget {
  final String label;
  final ValueChanged<GeocodeResult> onSelected;

  const AddressSearchField({super.key, required this.label, required this.onSelected});

  @override
  State<AddressSearchField> createState() => _AddressSearchFieldState();
}

class _AddressSearchFieldState extends State<AddressSearchField> {
  final _apiClient = ApiClient();
  final _controller = TextEditingController();
  Timer? _debounce;
  List<GeocodeResult> _results = [];
  bool _searching = false;

  @override
  void dispose() {
    _debounce?.cancel();
    _controller.dispose();
    super.dispose();
  }

  void _onChanged(String text) {
    _debounce?.cancel();
    if (text.trim().length < 3) {
      setState(() => _results = []);
      return;
    }
    _debounce = Timer(const Duration(milliseconds: 450), () => _search(text.trim()));
  }

  Future<void> _search(String query) async {
    setState(() => _searching = true);
    try {
      final results = await _apiClient.geocode(query);
      if (!mounted) return;
      setState(() => _results = results);
    } catch (_) {
      // Fallo silencioso: esto es solo autocompletado, no bloquea el flujo —
      // "Usar mi ubicación" sigue disponible como alternativa.
      if (mounted) setState(() => _results = []);
    } finally {
      if (mounted) setState(() => _searching = false);
    }
  }

  void _select(GeocodeResult result) {
    _debounce?.cancel();
    _controller.clear();
    setState(() => _results = []);
    FocusScope.of(context).unfocus();
    widget.onSelected(result);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: _controller,
          onChanged: _onChanged,
          decoration: InputDecoration(
            labelText: widget.label,
            hintText: 'Escribe una dirección...',
            suffixIcon: _searching
                ? const Padding(
                    padding: EdgeInsets.all(14),
                    child: SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  )
                : null,
          ),
        ),
        ..._results.map(
          (r) => ListTile(
            dense: true,
            leading: const Icon(Icons.place_outlined),
            title: Text(r.label),
            onTap: () => _select(r),
          ),
        ),
      ],
    );
  }
}
