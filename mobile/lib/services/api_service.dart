import 'package:dio/dio.dart';
import 'package:logger/logger.dart';

import '../core/models/commitment_model.dart';
import '../core/models/location_model.dart';
import '../core/models/evaluation_model.dart';

class ApiService {
  static const String defaultBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://life-autopilot-agentic-725797619054.us-central1.run.app',
  );
  final Dio _dio;
  final String studentId;
  final Logger _logger = Logger();

  ApiService({required this.studentId})
      : _dio = Dio(BaseOptions(
          baseUrl: defaultBaseUrl,
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 10),
          headers: {
            'Content-Type': 'application/json',
          },
        ));

  // Health check
  Future<bool> healthCheck() async {
    try {
      final response = await _dio.get('/health');
      return response.statusCode == 200;
    } catch (e) {
      _logger.e('Health check failed: $e');
      return false;
    }
  }

  // Get all commitments for the current student
  Future<List<Commitment>> getCommitments() async {
    try {
      final response = await _dio.get('/api/v1/students/$studentId/commitments');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => Commitment.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load commitments');
      }
    } catch (e) {
      _logger.e('Error getting commitments: $e');
      rethrow;
    }
  }

  // Get next commitment for the current student
  Future<Commitment?> getNextCommitment() async {
    try {
      final now = DateTime.now().toIso8601String();
      final response = await _dio.get(
        '/api/v1/students/$studentId/commitments/next',
        queryParameters: {'now': now},
      );
      if (response.statusCode == 200) {
        final data = response.data;
        if (data == null) {
          return null;
        }
        return Commitment.fromJson(data);
      } else {
        throw Exception('Failed to get next commitment');
      }
    } catch (e) {
      _logger.e('Error getting next commitment: $e');
      rethrow;
    }
  }

  // Get current location
  Future<Location?> getCurrentLocation() async {
    try {
      final response = await _dio.get('/api/v1/students/$studentId/location');
      if (response.statusCode == 200) {
        final data = response.data;
        if (data == null) {
          return null;
        }
        return Location.fromJson(data);
      } else {
        throw Exception('Failed to get location');
      }
    } catch (e) {
      _logger.e('Error getting location: $e');
      rethrow;
    }
  }

  // Get events (activity timeline)
  Future<List<AgentEvent>> getEvents({int limit = 50}) async {
    try {
      final response = await _dio.get(
        '/api/v1/students/$studentId/events',
        queryParameters: {'limit': limit},
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => AgentEvent.fromJson(json)).toList();
      } else {
        throw Exception('Failed to get events');
      }
    } catch (e) {
      _logger.e('Error getting events: $e');
      rethrow;
    }
  }

  // Autonomous evaluation
  Future<EvaluationResponse> evaluateAutonomous({
    required DateTime now,
    required bool studentHasStartedMoving,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/students/$studentId/evaluate',
        data: {
          'now': now.toIso8601String(),
          'student_has_started_moving': studentHasStartedMoving,
        },
      );
      if (response.statusCode == 200) {
        return EvaluationResponse.fromJson(response.data);
      } else {
        throw Exception('Failed to evaluate autonomously');
      }
    } catch (e) {
      _logger.e('Error evaluating autonomously: $e');
      rethrow;
    }
  }

  // Legacy evaluation (for testing)
  Future<EvaluationResponse> evaluateLegacy({
    required DateTime now,
    required String commitmentTitle,
    required int travelMinutes,
    required int preparationMinutes,
    required int arrivalBufferMinutes,
    required bool studentHasStartedMoving,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/agent/evaluate',
        data: {
          'now': now.toIso8601String(),
          'commitment': {
            'title': commitmentTitle,
          },
          'travel_minutes': travelMinutes,
          'preparation_minutes': preparationMinutes,
          'arrival_buffer_minutes': arrivalBufferMinutes,
          'student_has_started_moving': studentHasStartedMoving,
        },
      );
      if (response.statusCode == 200) {
        return EvaluationResponse.fromJson(response.data);
      } else {
        throw Exception('Failed to evaluate legacy');
      }
    } catch (e) {
      _logger.e('Error evaluating legacy: $e');
      rethrow;
    }
  }
}
