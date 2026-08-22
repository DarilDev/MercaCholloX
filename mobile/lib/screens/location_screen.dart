import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

import '../models/geocode_result.dart';
import '../models/profile.dart';
import '../models/store.dart';
import '../services/api_client.dart';
import '../theme.dart';
import '../widgets/address_search_field.dart';
import '../widgets/loading_view.dart';

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
  bool _nearbyLoading = false;
  Object? _error;
  Object? _nearbyError;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final profile = await _apiClient.getProfile();
      setState(() {
        _profile = profile;
        _loading = false;
      });
      if (profile.homeLat != null && profile.homeLon != null) {
        _loadNearbyStores(profile.homeLat!, profile.homeLon!);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e;
        _loading = false;
      });
    }
  }

  Future<void> _loadNearbyStores(double lat, double lon) async {
    setState(() {
      _nearbyLoading = true;
      _nearbyError = null;
    });
    try {
      final stores = await _apiClient.getNearbyStores(lat, lon);
      if (!mounted) return;
      setState(() => _nearbyStores = stores);
    } catch (e) {
      if (!mounted) return;
      setState(() => _nearbyError = e);
    } finally {
      if (mounted) setState(() => _nearbyLoading = false);
    }
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

  Future<void> _setHome(double lat, double lon) async {
    if (_profile == null) return;
    final updated = _profile!.copyWith(homeLat: lat, homeLon: lon);
    final saved = await _apiClient.updateProfile(updated);
    setState(() => _profile = saved);
    await _loadNearbyStores(lat, lon);
  }

  Future<void> _setWork(double lat, double lon) async {
    if (_profile == null) return;
    final updated = _profile!.copyWith(workLat: lat, workLon: lon);
    final saved = await _apiClient.updateProfile(updated);
    setState(() => _profile = saved);
  }

  Future<void> _setHomeToCurrentLocation() async {
    setState(() => _busy = true);
    final position = await _getCurrentPosition();
    if (position != null) await _setHome(position.latitude, position.longitude);
    if (mounted) setState(() => _busy = false);
  }

  Future<void> _setWorkToCurrentLocation() async {
    setState(() => _busy = true);
    final position = await _getCurrentPosition();
    if (position != null) await _setWork(position.latitude, position.longitude);
    if (mounted) setState(() => _busy = false);
  }

  Future<void> _setHomeFromAddress(GeocodeResult result) async {
    setState(() => _busy = true);
    await _setHome(result.lat, result.lon);
    if (mounted) setState(() => _busy = false);
  }

  Future<void> _setWorkFromAddress(GeocodeResult result) async {
    setState(() => _busy = true);
    await _setWork(result.lat, result.lon);
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
    if (_loading) {
      return const Scaffold(body: LoadingView());
    }
    if (_error != null || _profile == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Casa, trabajo y súper habitual')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Error cargando el perfil: $_error', textAlign: TextAlign.center),
                const SizedBox(height: 12),
                FilledButton(onPressed: _load, child: const Text('Reintentar')),
              ],
            ),
          ),
        ),
      );
    }
    final profile = _profile!;

    return Scaffold(
      appBar: AppBar(title: const Text('Casa, trabajo y súper habitual')),
      body: ListView(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
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
                AddressSearchField(label: 'O escribe la dirección de casa', onSelected: _setHomeFromAddress),
                const SizedBox(height: AppSpacing.md),
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
                AddressSearchField(label: 'O escribe la dirección del trabajo', onSelected: _setWorkFromAddress),
                const Divider(height: 32),
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text('Súper cercanos', style: Theme.of(context).textTheme.titleMedium),
                ),
                const SizedBox(height: 8),
                if (profile.homeLat == null)
                  const Text('Fija tu casa para ver los súper cercanos de verdad.')
                else if (_nearbyError != null)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    child: Column(
                      children: [
                        Text('Error buscando súper cercanos: $_nearbyError', textAlign: TextAlign.center),
                        const SizedBox(height: 8),
                        FilledButton(
                          onPressed: () => _loadNearbyStores(profile.homeLat!, profile.homeLon!),
                          child: const Text('Reintentar'),
                        ),
                      ],
                    ),
                  )
                else if (_nearbyLoading)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: LoadingView(),
                  )
                else if (_nearbyStores.isEmpty)
                  const Text('Sin súper cercanos cacheados todavía en esta zona.')
                else
                  ..._nearbyStores.map((store) {
                    final isUsual = store.id == profile.usualStoreId;
                    return ListTile(
                      leading: Icon(isUsual ? Icons.star : Icons.storefront_outlined,
                          color: isUsual ? AppColors.starred : null),
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
          ),
        ],
      ),
    );
  }
}
