import 'package:flutter/material.dart';

import '../models/product.dart';

class ProductTile extends StatelessWidget {
  final Product product;
  final VoidCallback? onAdd;

  const ProductTile({super.key, required this.product, this.onAdd});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: SizedBox(
        width: 48,
        height: 48,
        child: product.imageUrl != null
            ? Image.network(
                product.imageUrl!,
                fit: BoxFit.contain,
                errorBuilder: (context, error, stack) =>
                    const Icon(Icons.image_not_supported_outlined),
                loadingBuilder: (context, child, progress) {
                  if (progress == null) return child;
                  return const Center(
                    child: SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  );
                },
              )
            : const Icon(Icons.shopping_basket_outlined),
      ),
      title: Text(product.name),
      subtitle: Text(product.category ?? ''),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            product.price != null ? '${product.price!.toStringAsFixed(2)} €' : '-',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          if (onAdd != null)
            IconButton(icon: const Icon(Icons.add_shopping_cart), onPressed: onAdd),
        ],
      ),
    );
  }
}
