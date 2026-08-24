import 'package:flutter/material.dart';

import 'core/models/commitment_model.dart';
import 'core/models/evaluation_model.dart';
import 'services/api_service.dart';

void main() => runApp(const LifeAutopilotApp());

class LifeAutopilotApp extends StatelessWidget {
  const LifeAutopilotApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Life Autopilot',
        theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
        home: const DashboardPage(),
      );
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  final _studentId = 'demo-student';
  late final ApiService _api;
  bool _loading = true;
  bool _healthy = false;
  List<Commitment> _commitments = [];
  List<AgentEvent> _events = [];
  EvaluationResponse? _evaluation;
  String? _error;

  @override
  void initState() {
    super.initState();
    _api = ApiService(studentId: _studentId);
    _refresh();
  }

  Future<void> _refresh() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      _healthy = await _api.healthCheck();
      _commitments = await _api.getCommitments();
      _events = await _api.getEvents(limit: 10);
    } catch (error) {
      _error = error.toString();
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _evaluate() async {
    try {
      final result = await _api.evaluateAutonomous(
        now: DateTime.now().toUtc(),
        studentHasStartedMoving: false,
      );
      if (mounted) {
        setState(() => _evaluation = result);
        await _refresh();
      }
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(
          title: const Text('Life Autopilot'),
          actions: [IconButton(onPressed: _refresh, icon: const Icon(Icons.refresh))],
        ),
        body: RefreshIndicator(
          onRefresh: _refresh,
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Text('Your day, kept on track', style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 8),
              Text(_healthy ? 'Connected to Cloud Run' : 'Backend unavailable'),
              if (_loading) const LinearProgressIndicator(),
              if (_error != null) _MessageCard(text: _error!, color: Colors.red),
              const SizedBox(height: 16),
              Text('Upcoming commitments', style: Theme.of(context).textTheme.titleLarge),
              if (_commitments.isEmpty)
                const _MessageCard(text: 'No commitments yet. Seed one through the backend docs or curl.')
              else
                ..._commitments.map((item) => Card(child: ListTile(
                      title: Text(item.title),
                      subtitle: Text('${item.destination}\n${item.startTime.toLocal()}'),
                    ))),
              const SizedBox(height: 12),
              FilledButton.icon(
                onPressed: _loading || _commitments.isEmpty ? null : _evaluate,
                icon: const Icon(Icons.smart_toy),
                label: const Text('Evaluate autonomously'),
              ),
              if (_evaluation != null)
                _MessageCard(
                  text: '${_evaluation!.decision}: ${_evaluation!.reason}\n${_evaluation!.notificationBody ?? ''}',
                  color: Colors.indigo,
                ),
              const SizedBox(height: 12),
              Text('Agent activity', style: Theme.of(context).textTheme.titleLarge),
              ..._events.map((event) => ListTile(
                    dense: true,
                    leading: const Icon(Icons.history),
                    title: Text(event.decision),
                    subtitle: Text(event.reason),
                  )),
            ],
          ),
        ),
      );
}

class _MessageCard extends StatelessWidget {
  final String text;
  final Color? color;

  const _MessageCard({required this.text, this.color});

  @override
  Widget build(BuildContext context) => Card(
        color: color?.withValues(alpha: 0.1),
        child: Padding(padding: const EdgeInsets.all(16), child: Text(text)),
      );
}
