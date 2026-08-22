import 'package:flutter/material.dart';

import '../services/api_client.dart';

Future<void> addToShoppingList(
  BuildContext context,
  ApiClient apiClient,
  String name, {
  String? imageUrl,
}) async {
  await apiClient.addFavorite(name, imageUrl: imageUrl);
  if (!context.mounted) return;
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Añadido a la lista: $name')),
  );
}
