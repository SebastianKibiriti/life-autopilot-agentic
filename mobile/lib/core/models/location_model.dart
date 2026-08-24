import 'package:json_annotation/json_annotation.dart';
import 'package:geolocator/geolocator.dart';

part 'location_model.g.dart';

@JsonSerializable()
class AppLocation {
  final double latitude;
  final double longitude;
  final double? accuracyMeters;
  final DateTime capturedAt;
  final String provider;

  AppLocation({
    required this.latitude,
    required this.longitude,
    this.accuracyMeters,
    required this.capturedAt,
    this.provider = 'gps',
  });

  factory AppLocation.fromJson(Map<String, dynamic> json) => _$AppLocationFromJson(json);
  Map<String, dynamic> toJson() => _$AppLocationToJson(this);

  Position toPosition() {
    return Position(latitude: latitude, longitude: longitude);
  }

  static AppLocation fromPosition(Position position, {double? accuracy}) {
    return AppLocation(
      latitude: position.latitude,
      longitude: position.longitude,
      accuracyMeters: accuracy,
      capturedAt: DateTime.now(),
    );
  }
}

@JsonSerializable()
class Destination {
  final String label;
  final double latitude;
  final double longitude;
  final String formattedAddress;
  final double confidence;

  Destination({
    required this.label,
    required this.latitude,
    required this.longitude,
    this.formattedAddress = '',
    this.confidence = 1.0,
  });

  factory Destination.fromJson(Map<String, dynamic> json) => _$DestinationFromJson(json);
  Map<String, dynamic> toJson() => _$DestinationToJson(this);
}