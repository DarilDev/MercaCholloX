class NearbyStore {
  final int id;
  final String chain;
  final String name;
  final String? address;
  final double lat;
  final double lon;
  final double distanceKm;

  NearbyStore({
    required this.id,
    required this.chain,
    required this.name,
    required this.address,
    required this.lat,
    required this.lon,
    required this.distanceKm,
  });

  factory NearbyStore.fromJson(Map<String, dynamic> json) {
    return NearbyStore(
      id: json['id'] as int,
      chain: json['chain'] as String,
      name: json['name'] as String,
      address: json['address'] as String?,
      lat: (json['lat'] as num).toDouble(),
      lon: (json['lon'] as num).toDouble(),
      distanceKm: (json['distance_km'] as num).toDouble(),
    );
  }
}
