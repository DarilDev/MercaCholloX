import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

import '../models/profile.dart';
import '../models/store.dart';
import '../services/api_client.dart';

class LocationScreen extends StatefulWidget {
  const LocationScreen({super.key});

  @override
  State<LocationScreen> createState() => _LocationScreenState();
}

class _LocationScreenState extends State<LocationScreen> {
  final _apiClient = ApiClient();
  UserProfile? _profile;
  List<NearbyStore> _nearbyStores = [];
  bool _loading = true;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final profile = await _apiClient.getProfile();
    setState(() {
      _profile = profile;
      _loading = false;
    });
    if (profile.homeLat != null && profile.homeLon != null) {
      _loadNearbyStores(profile.homeLat!, profile.homeLon!);
    }
  }

  Future<void> _loadNearbyStores(double lat, double lon) async {
    final stores = await _apiClient.getNearbyStores(lat, lon);
    if (!mounted) return;
    setState(() => _nearbyStores = stores);
  }

  Future<Position?> _getCurrentPosition() async {
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      if (!mounted) return null;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Necesito permiso de ubicación para esto')),
      );
      return null;
    }
    if (!await Geolocator.isLocationServiceEnabled()) {
      if (!mounted) return null;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Activa la ubicación del móvil')),
      );
      return null;
    }
    return Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.medium),
    );
  }

  Future<void> _setHomeToCurrentLocation() async {
    setState(() => _busy = true);
    final position = await _getCurrentPosition();
    if (position != null && _profile != null) {
      final updated = _profile!.copyWith(homeLat: position.latitude, homeLon: position.longitude);
      final saved = await _apiClient.updateProfile(updated);
      setState(() => _profile = saved);
      await _loadNearbyStores(position.latitude, position.longitude);
    }
    if (mounted) setState(() => _busy = false);
  }

  Future<void> _setWorkToCurrentLocation() async {
    setState(() => _busy = true);
    final position = await _getCurrentPosition();
    if (position != null && _profile != null) {
      final updated = _profile!.copyWith(workLat: position.latitude, workLon: position.longitude);
      final saved = await _apiClient.updateProfile(updated);
      setState(() => _profile = saved);
    }
    if (mounted) setState(() => _busy = false);
  }

  Future<void> _setUsualStore(NearbyStore store) async {
    if (_profile == null) return;
    final updated = _profile!.copyWith(usualStoreId: store.id);
    final saved = await _apiClient.updateProfile(updated);
    setState(() => _profile = saved);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Súper habitual: ${store.name}')),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading || _profile == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final profile = _profile!;

    return Scaffold(
      appBar: AppBar(title: const Text('Casa, trabajo y súper habitual')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          ListTile(
            leading: const Icon(Icons.home_outlined),
            title: const Text('Casa'),
            subtitle: Text(
              profile.homeLat != null
                  ? '${profile.homeLat!.toStringAsFixed(4)}, ${profile.homeLon!.toStringAsFixed(4)}'
                  : 'Sin fijar',
            ),
            trailing: _busy
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : TextButton(
                    onPressed: _setHomeToCurrentLocation,
                    child: const Text('Usar mi ubicación'),
                  ),
          ),
          ListTile(
            leading: const Icon(Icons.work_outline),
            title: const Text('Trabajo (opcional)'),
            subtitle: Text(
              profile.workLat != null
                  ? '${profile.workLat!.toStringAsFixed(4)}, ${profile.workLon!.toStringAsFixed(4)}'
                  : 'Sin fijar',
            ),
            trailing: _busy
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : TextButton(
                    onPressed: _setWorkToCurrentLocation,
                    child: const Text('Usar mi ubicación'),
                  ),
          ),
          const Divider(height: 32),
          Text('Súper cercanos', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          if (profile.homeLat == null)
            const Text('Fija tu casa para ver los súper cercanos de verdad.')
          else if (_nearbyStores.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: Center(child: CircularProgressIndicator()),
            )
          else
            ..._nearbyStores.map((store) {
              final isUsual = store.id == profile.usualStoreId;
              return ListTile(
                leading: Icon(isUsual ? Icons.star : Icons.storefront_outlined,
                    color: isUsual ? Colors.amber : null),
                title: Text(store.name),
                subtitle: Text('${store.chain} · ${store.distanceKm} km'),
                trailing: isUsual
                    ? const Text('Habitual')
                    : TextButton(
                        onPressed: () => _setUsualStore(store),
                        child: const Text('Marcar habitual'),
                      ),
              );
            }),
        ],
      ),
    );
  }
}
