import 'package:flutter/material.dart';

/// Generaliza el patrón de error+"Reintentar" que antes solo tenía
/// LocationScreen — el resto de pantallas eran callejón sin salida si
/// fallaba la petición (algunas ni siquiera mostraban el error real).
class ErrorView extends StatelessWidget {
  final Object error;
  final VoidCallback? onRetry;

  const ErrorView({super.key, required this.error, this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Ha ocurrido un error: $error', textAlign: TextAlign.center),
            if (onRetry != null) ...[
              const SizedBox(height: 12),
              FilledButton(onPressed: onRetry, child: const Text('Reintentar')),
            ],
          ],
        ),
      ),
    );
  }
}
