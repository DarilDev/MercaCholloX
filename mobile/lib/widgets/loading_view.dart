import 'package:flutter/material.dart';

/// Antes `Center(child: CircularProgressIndicator())` se repetía casi
/// idéntico en 7 sitios distintos — un solo widget compartido en su lugar.
class LoadingView extends StatelessWidget {
  const LoadingView({super.key});

  @override
  Widget build(BuildContext context) => const Center(child: CircularProgressIndicator());
}
