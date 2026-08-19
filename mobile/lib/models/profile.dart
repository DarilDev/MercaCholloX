class UserProfile {
  final double? homeLat;
  final double? homeLon;
  final double? workLat;
  final double? workLon;
  final int? usualStoreId;
  final double vehicleConsumptionL100km;
  final String fuelType;
  final double hourlyValueEur;

  UserProfile({
    required this.homeLat,
    required this.homeLon,
    required this.workLat,
    required this.workLon,
    required this.usualStoreId,
    required this.vehicleConsumptionL100km,
    required this.fuelType,
    required this.hourlyValueEur,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      homeLat: (json['home_lat'] as num?)?.toDouble(),
      homeLon: (json['home_lon'] as num?)?.toDouble(),
      workLat: (json['work_lat'] as num?)?.toDouble(),
      workLon: (json['work_lon'] as num?)?.toDouble(),
      usualStoreId: json['usual_store_id'] as int?,
      vehicleConsumptionL100km: (json['vehicle_consumption_l_per_100km'] as num).toDouble(),
      fuelType: json['fuel_type'] as String,
      hourlyValueEur: (json['hourly_value_eur'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'home_lat': homeLat,
      'home_lon': homeLon,
      'work_lat': workLat,
      'work_lon': workLon,
      'usual_store_id': usualStoreId,
      'vehicle_consumption_l_per_100km': vehicleConsumptionL100km,
      'fuel_type': fuelType,
      'hourly_value_eur': hourlyValueEur,
    };
  }

  UserProfile copyWith({
    double? homeLat,
    double? homeLon,
    double? workLat,
    double? workLon,
    int? usualStoreId,
  }) {
    return UserProfile(
      homeLat: homeLat ?? this.homeLat,
      homeLon: homeLon ?? this.homeLon,
      workLat: workLat ?? this.workLat,
      workLon: workLon ?? this.workLon,
      usualStoreId: usualStoreId ?? this.usualStoreId,
      vehicleConsumptionL100km: vehicleConsumptionL100km,
      fuelType: fuelType,
      hourlyValueEur: hourlyValueEur,
    );
  }
}
