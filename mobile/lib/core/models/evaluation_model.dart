import 'package:json_annotation/json_annotation.dart';

part 'evaluation_model.g.dart';

@JsonSerializable()
class EvaluationResponse {
  final String commitmentTitle;
  final DateTime? preparationAt;
  final DateTime? leaveAt;
  final String decision;
  final String reason;
  final String routeProvider;
  final bool notificationSent;
  final String? notificationBody;

  EvaluationResponse({
    required this.commitmentTitle,
    this.preparationAt,
    this.leaveAt,
    required this.decision,
    required this.reason,
    required this.routeProvider,
    this.notificationSent = false,
    this.notificationBody,
  });

  factory EvaluationResponse.fromJson(Map<String, dynamic> json) => _$EvaluationResponseFromJson(json);
  Map<String, dynamic> toJson() => _$EvaluationResponseToJson(this);
}

@JsonSerializable()
class AgentEvent {
  final String id;
  final String studentId;
  final String? commitmentId;
  final DateTime timestamp;
  final String decision;
  final String reason;
  final String action;
  final String outcome;
  final String? notificationTitle;
  final String? notificationBody;

  AgentEvent({
    required this.id,
    required this.studentId,
    this.commitmentId,
    required this.timestamp,
    required this.decision,
    required this.reason,
    required this.action,
    required this.outcome,
    this.notificationTitle,
    this.notificationBody,
  });

  factory AgentEvent.fromJson(Map<String, dynamic> json) => _$AgentEventFromJson(json);
  Map<String, dynamic> toJson() => _$AgentEventToJson(this);
}