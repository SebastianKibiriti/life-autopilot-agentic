// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'location_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AppLocation _$AppLocationFromJson(Map<String, dynamic> json) => AppLocation(
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      accuracyMeters: (json['accuracyMeters'] as num?)?.toDouble(),
      capturedAt: DateTime.parse(json['capturedAt'] as String),
      provider: json['provider'] as String? ?? 'gps',
    );

Map<String, dynamic> _$AppLocationToJson(AppLocation instance) =>
    <String, dynamic>{
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'accuracyMeters': instance.accuracyMeters,
      'capturedAt': instance.capturedAt.toIso8601String(),
      'provider': instance.provider,
    };

Destination _$DestinationFromJson(Map<String, dynamic> json) => Destination(
      label: json['label'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      formattedAddress: json['formattedAddress'] as String? ?? '',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 1.0,
    );

Map<String, dynamic> _$DestinationToJson(Destination instance) =>
    <String, dynamic>{
      'label': instance.label,
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'formattedAddress': instance.formattedAddress,
      'confidence': instance.confidence,
    };
