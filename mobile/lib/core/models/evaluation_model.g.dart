// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'evaluation_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

EvaluationResponse _$EvaluationResponseFromJson(Map<String, dynamic> json) =>
    EvaluationResponse(
      commitmentTitle: json['commitmentTitle'] as String,
      preparationAt: json['preparationAt'] == null
          ? null
          : DateTime.parse(json['preparationAt'] as String),
      leaveAt: json['leaveAt'] == null
          ? null
          : DateTime.parse(json['leaveAt'] as String),
      decision: json['decision'] as String,
      reason: json['reason'] as String,
      routeProvider: json['routeProvider'] as String,
      notificationSent: json['notificationSent'] as bool? ?? false,
      notificationBody: json['notificationBody'] as String?,
    );

Map<String, dynamic> _$EvaluationResponseToJson(EvaluationResponse instance) =>
    <String, dynamic>{
      'commitmentTitle': instance.commitmentTitle,
      'preparationAt': instance.preparationAt?.toIso8601String(),
      'leaveAt': instance.leaveAt?.toIso8601String(),
      'decision': instance.decision,
      'reason': instance.reason,
      'routeProvider': instance.routeProvider,
      'notificationSent': instance.notificationSent,
      'notificationBody': instance.notificationBody,
    };

AgentEvent _$AgentEventFromJson(Map<String, dynamic> json) => AgentEvent(
      id: json['id'] as String,
      studentId: json['studentId'] as String,
      commitmentId: json['commitmentId'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
      decision: json['decision'] as String,
      reason: json['reason'] as String,
      action: json['action'] as String,
      outcome: json['outcome'] as String,
      notificationTitle: json['notificationTitle'] as String?,
      notificationBody: json['notificationBody'] as String?,
    );

Map<String, dynamic> _$AgentEventToJson(AgentEvent instance) =>
    <String, dynamic>{
      'id': instance.id,
      'studentId': instance.studentId,
      'commitmentId': instance.commitmentId,
      'timestamp': instance.timestamp.toIso8601String(),
      'decision': instance.decision,
      'reason': instance.reason,
      'action': instance.action,
      'outcome': instance.outcome,
      'notificationTitle': instance.notificationTitle,
      'notificationBody': instance.notificationBody,
    };
