import 'package:json_annotation/json_annotation.dart';

part 'commitment_model.g.dart';

@JsonSerializable()
class Commitment {
  final String id;
  final String title;
  final DateTime startTime;
  final String destination;
  final String status;

  Commitment({
    required this.id,
    required this.title,
    required this.startTime,
    required this.destination,
    this.status = 'active',
  });

  factory Commitment.fromJson(Map<String, dynamic> json) => _$CommitmentFromJson(json);
  Map<String, dynamic> toJson() => _$CommitmentToJson(this);

  Commitment copyWith({
    String? id,
    String? title,
    DateTime? startTime,
    String? destination,
    String? status,
  }) {
    return Commitment(
      id: id ?? this.id,
      title: title ?? this.title,
      startTime: startTime ?? this.startTime,
      destination: destination ?? this.destination,
      status: status ?? this.status,
    );
  }
}

@JsonSerializable()
class CommitmentCreate {
  final String title;
  final DateTime startTime;
  final String destination;
  final String status;

  CommitmentCreate({
    required this.title,
    required this.startTime,
    required this.destination,
    this.status = 'active',
  });

  factory CommitmentCreate.fromJson(Map<String, dynamic> json) => _$CommitmentCreateFromJson(json);
  Map<String, dynamic> toJson() => _$CommitmentCreateToJson(this);
}