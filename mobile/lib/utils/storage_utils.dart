// Storage utilities for Flutter
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageUtils {
  static final FlutterSecureStorage secureStorage = FlutterSecureStorage();
  static SharedPreferences? _prefs;

  static Future<SharedPreferences> get prefs async {
    if (_prefs == null) {
      _prefs = await SharedPreferences.getInstance();
    }
    return _prefs!;
  }

  // Student management
  static const String _studentIdKey = 'student_id';
  static const String _displayNameKey = 'display_name';
  static const String _isFirstTimeKey = 'is_first_time';

  static Future<void> saveStudentId(String id) async {
    await secureStorage.write(key: _studentIdKey, value: id);
  }

  static Future<String?> getStudentId() async {
    return await secureStorage.read(key: _studentIdKey);
  }

  static Future<void> saveDisplayName(String name) async {
    await secureStorage.write(key: _displayNameKey, value: name);
  }

  static Future<String?> getDisplayName() async {
    return await secureStorage.read(key: _displayNameKey);
  }

  static Future<void> setFirstTime(bool value) async {
    final prefs = await getPrefs();
    await prefs.setBool(_isFirstTimeKey, value);
  }

  static Future<bool> isFirstTime() async {
    final prefs = await getPrefs();
    return prefs.getBool(_isFirstTimeKey) ?? true;
  }

  static Future<void> clearAll() async {
    await secureStorage.deleteAll();
    final prefs = await getPrefs();
    await prefs.clear();
  }

  static Future<SharedPreferences> getPrefs() async {
    return await prefs;
  }
}
