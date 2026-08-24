import 'package:riverpod/riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// Student state management
class StudentState {
  final String id;
  final String? displayName;
  final bool isAuthenticated;

  StudentState({
    required this.id,
    this.displayName,
    this.isAuthenticated = false,
  });

  StudentState copyWith({
    String? id,
    String? displayName,
    bool? isAuthenticated,
  }) {
    return StudentState(
      id: id ?? this.id,
      displayName: displayName ?? this.displayName,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
    );
  }
}

class StudentNotifier extends Notifier<StudentState> {
  static const String _studentIdKey = 'student_id';

  void setStudent(String id, {String? displayName}) {
    final state = StudentState(
      id: id,
      displayName: displayName,
      isAuthenticated: true,
    );
    state = state;
    // Save to local storage
    _saveStudentId(id);
  }

  Future<void> loadSavedStudent() async {
    final savedId = await _getSavedStudentId();
    if (savedId != null) {
      setStudent(savedId);
    }
  }

  void clearStudent() {
    state = StudentState(id: '', isAuthenticated: false);
    _clearStudentId();
  }

  bool get hasStudent => state.isAuthenticated && state.id.isNotEmpty;

  String get studentId => state.id;
}

final studentProvider = NotifierProvider<StudentNotifier, StudentState>(StudentNotifier.new);

class _StorageKeys {
  static const String studentId = 'student_id';
}

final _storage = FlutterSecureStorage();

Future<void> _saveStudentId(String id) async {
  await _storage.write(key: _StorageKeys.studentId, value: id);
}

Future<String?> _getSavedStudentId() async {
  return await _storage.read(key: _StorageKeys.studentId);
}

Future<void> _clearStudentId() async {
  await _storage.delete(key: _StorageKeys.studentId);
}
