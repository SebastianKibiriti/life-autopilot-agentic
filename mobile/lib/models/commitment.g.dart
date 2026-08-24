// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'commitment.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Commitment _$CommitmentFromJson(Map<String, dynamic> json) => Commitment(
      id: json['id'] as String,
      title: json['title'] as String,
      startTime: DateTime.parse(json['startTime'] as String),
      destination: json['destination'] as String,
      status: json['status'] as String? ?? 'active',
    );

Map<String, dynamic> _$CommitmentToJson(Commitment instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'startTime': instance.startTime.toIso8601String(),
      'destination': instance.destination,
      'status': instance.status,
    };

CommitmentCreate _$CommitmentCreateFromJson(Map<String, dynamic> json) =>
    CommitmentCreate(
      title: json['title'] as String,
      startTime: DateTime.parse(json['startTime'] as String),
      destination: json['destination'] as String,
      status: json['status'] as String? ?? 'active',
    );

Map<String, dynamic> _$CommitmentCreateToJson(CommitmentCreate instance) =>
    <String, dynamic>{
      'title': instance.title,
      'startTime': instance.startTime.toIso8601String(),
      'destination': instance.destination,
      'status': instance.status,
    };
