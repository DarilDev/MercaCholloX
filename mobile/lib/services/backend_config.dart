import 'package:shared_preferences/shared_preferences.dart';

/// URL del backend, configurable en tiempo de ejecución en vez de hardcodeada
/// en el código — así una nueva URL (ej. tras reiniciar ngrok, o al migrar a
/// Render) no obliga a recompilar y reinstalar en el móvil de cada tester.
///
/// Prioridad: valor guardado en el dispositivo > `--dart-define=API_BASE_URL`
/// en tiempo de compilación > valor por defecto de desarrollo.
class BackendConfig {
  static const _prefsKey = 'api_base_url';
  static const _compiledDefault = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://mercachollo-api.onrender.com',
  );

  static Future<String> getBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_prefsKey) ?? _compiledDefault;
  }

  static Future<void> setBaseUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefsKey, url.trim());
  }
}
