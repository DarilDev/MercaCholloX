import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

/// Identidad anónima por dispositivo (no login real) — el backend aísla los
/// datos de cada persona a partir de este id, mandado como header X-Device-Id
/// en cada petición. Ver backend/app/deps.py y docs/DECISIONS.md.
class DeviceIdentity {
  static const _prefsKey = 'device_id';
  static String? _cached;

  static Future<String> getOrCreate() async {
    if (_cached != null) return _cached!;

    final prefs = await SharedPreferences.getInstance();
    var id = prefs.getString(_prefsKey);
    if (id == null) {
      id = const Uuid().v4();
      await prefs.setString(_prefsKey, id);
    }
    _cached = id;
    return id;
  }
}
