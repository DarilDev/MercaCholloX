import 'product.dart';

class Favorite {
  final int id;
  final String query;
  final int quantity;

  Favorite({required this.id, required this.query, required this.quantity});

  factory Favorite.fromJson(Map<String, dynamic> json) {
    return Favorite(
      id: json['id'] as int,
      query: json['query'] as String,
      quantity: json['quantity'] as int,
    );
  }
}

class MatchedItem {
  final int favoriteId;
  final String query;
  final int quantity;
  final Product? matchedProduct;
  final double? unitPrice;
  final double? subtotal;

  MatchedItem({
    required this.favoriteId,
    required this.query,
    required this.quantity,
    required this.matchedProduct,
    required this.unitPrice,
    required this.subtotal,
  });

  factory MatchedItem.fromJson(Map<String, dynamic> json) {
    return MatchedItem(
      favoriteId: json['favorite_id'] as int,
      query: json['query'] as String,
      quantity: json['quantity'] as int,
      matchedProduct: json['matched_product'] != null
          ? Product.fromJson(json['matched_product'] as Map<String, dynamic>)
          : null,
      unitPrice: (json['unit_price'] as num?)?.toDouble(),
      subtotal: (json['subtotal'] as num?)?.toDouble(),
    );
  }
}

class ChainTotal {
  final String chain;
  final List<MatchedItem> items;
  final double total;
  final List<String> missing;

  ChainTotal({
    required this.chain,
    required this.items,
    required this.total,
    required this.missing,
  });

  factory ChainTotal.fromJson(Map<String, dynamic> json) {
    return ChainTotal(
      chain: json['chain'] as String,
      items: (json['items'] as List)
          .map((e) => MatchedItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toDouble(),
      missing: (json['missing'] as List).cast<String>(),
    );
  }
}

class ShoppingComparison {
  final List<ChainTotal> chains;
  final String? cheapestChain;

  ShoppingComparison({required this.chains, required this.cheapestChain});

  factory ShoppingComparison.fromJson(Map<String, dynamic> json) {
    return ShoppingComparison(
      chains: (json['chains'] as List)
          .map((e) => ChainTotal.fromJson(e as Map<String, dynamic>))
          .toList(),
      cheapestChain: json['cheapest_chain'] as String?,
    );
  }
}
