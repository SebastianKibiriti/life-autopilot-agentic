// Core app widgets and UI components
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:geolocator/geolocator.dart';
import 'package:url_launcher/url_launcher.dart';

// Models
import '../models/commitment_model.dart';
import '../models/location_model.dart';
import '../models/evaluation_model.dart';

// Providers
import '../providers/student_provider.dart';

// Services
import '../services/api_service.dart';

// Constants
import '../utils/constants.dart';

// Utils
import '../utils/formatters.dart';
import '../utils/location_utils.dart';

class LifeAutopilotApp extends ConsumerWidget {
  const LifeAutopilotApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final studentState = ref.watch(studentProvider);

    return MaterialApp(
      title: 'Life Autopilot',
      theme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Colors.black,
          elevation: 1,
        ),
      ),
      initialRoute: studentState.hasStudent
          ? '/dashboard'
          : '/setup',
      routes: {
        '/setup': (context) => const StudentSetupScreen(),
        '/dashboard': (context) => const DashboardScreen(),
      },
    );
  }
}

// Student setup screen for entering student ID
class StudentSetupScreen extends ConsumerStatefulWidget {
  const StudentSetupScreen({super.key});

  @override
  createState() => _StudentSetupScreenState();
}

class _StudentSetupScreenState extends ConsumerState<StudentSetupScreen> {
  final _studentIdController = TextEditingController();
  final _displayNameController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  @override
  void dispose() {
    _studentIdController.dispose();
    _displayNameController.dispose();
    super.dispose();
  }

  Future<void> _saveStudent() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isLoading = true);

    try {
      final studentId = _studentIdController.text.trim();
      final displayName = _displayNameController.text.trim().isEmpty
          ? null
          : _displayNameController.text.trim();

      final studentNotifier = ref.read(studentProvider.notifier);
      studentNotifier.setStudent(studentId, displayName: displayName);

      // Navigate to dashboard
      Navigator.pushReplacementNamed(context, '/dashboard');
    } catch (e) {
      _showErrorSnackBar('Failed to save student: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.indigo, Colors.white],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Logo and title
                  Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 8,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.directions_walk,
                          size: 64,
                          color: Colors.indigo,
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Life Autopilot',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Your day, kept on track',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.white70,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),

                  // Student ID field
                  TextFormField(
                    controller: _studentIdController,
                    decoration: const InputDecoration(
                      labelText: 'Student ID',
                      hintText: 'e.g., student123',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.person),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Please enter a student ID';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // Display name field
                  TextFormField(
                    controller: _displayNameController,
                    decoration: const InputDecoration(
                      labelText: 'Display Name (optional)',
                      hintText: 'e.g., Alex Johnson',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.badge),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Save button
                  ElevatedButton(
                    onPressed: _isLoading ? null : _saveStudent,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : const Text(
                            'Start Your Day',
                            style: TextStyle(fontSize: 16),
                          ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// Main dashboard screen
class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  late final ApiService _apiService;
  bool _isLoading = true;
  List<Commitment> _commitments = [];
  Commitment? _nextCommitment;
  AppLocation? _currentLocation;
  List<AgentEvent> _recentEvents = [];
  String _agentStatus = 'Initializing...';

  @override
  void initState() {
    super.initState();
    _initDashboard();
  }

  Future<void> _initDashboard() async {
    final studentState = ref.read(studentProvider);

    setState(() {
      _apiService = ApiService(studentId: studentState.id);
      _agentStatus = 'Connecting to backend...';
    });

    try {
      // Test API connection
      final isHealthy = await _apiService.healthCheck();
      if (!isHealthy) {
        throw Exception('Backend not available');
      }

      // Load data
      await _loadDashboardData();
      setState(() {
        _agentStatus = 'Ready';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _agentStatus = 'Connection failed';
        _isLoading = false;
      });
      _showErrorSnackBar('Failed to load dashboard: $e');
    }
  }

  Future<void> _loadDashboardData() async {
    // Load commitments
    final commitments = await _apiService.getCommitments();
    setState(() => _commitments = commitments);

    // Get next commitment
    final nextCommitment = await _apiService.getNextCommitment();
    setState(() => _nextCommitment = nextCommitment);

    // Get current location
    try {
      final location = await _apiService.getCurrentLocation();
      setState(() => _currentLocation = location);
    } catch (e) {
      _logger.w('No location available: $e');
    }

    // Get recent events
    final events = await _apiService.getEvents(limit: 5);
    setState(() => _recentEvents = events);

    // Trigger autonomous evaluation if we have a next commitment
    if (_nextCommitment != null) {
      await _evaluateAutonomous();
    }
  }

  Future<void> _evaluateAutonomous() async {
    try {
      setState(() => _agentStatus = 'Evaluating...');

      final now = DateTime.now();
      final studentHasStartedMoving = _currentLocation != null
          ? await _hasStudentStartedMoving(_currentLocation!)
          : false;

      final evaluation = await _apiService.evaluateAutonomous(
        now: now,
        studentHasStartedMoving: studentHasStartedMoving,
      );

      _logger.i('Evaluation result: ${evaluation.decision}');

      // Show notification if evaluation resulted in action
      if (evaluation.decision != 'NO_ACTION') {
        _showEvaluationNotification(evaluation);
      }

      setState(() => _agentStatus = 'Ready');
    } catch (e) {
      setState(() => _agentStatus = 'Evaluation failed');
      _logger.e('Evaluation error: $e');
      _showErrorSnackBar('Evaluation failed: $e');
    }
  }

  Future<bool> _hasStudentStartedMoving(AppLocation location) async {
    // Simple heuristic: check if location is different from last known location
    // For now, assume not moving
    return false;
  }

  void _showEvaluationNotification(EvaluationResponse evaluation) {
    // TODO: Implement local notification
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Agent: ${evaluation.reason}'),
        backgroundColor: _getDecisionColor(evaluation.decision),
        action: SnackBarAction(
          label: 'VIEW',
          onPressed: () {
            Navigator.pushNamed(
              context,
              '/evaluation',
              arguments: evaluation,
            );
          },
        ),
      ),
    );
  }

  Color _getDecisionColor(String decision) {
    switch (decision) {
      case 'PREPARE':
        return Colors.orange;
      case 'LEAVE':
        return Colors.green;
      case 'REPLAN':
        return Colors.amber;
      case 'ESCALATE':
        return Colors.red;
      default:
        return Colors.blue;
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.fixed,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const Icon(Icons.directions_walk, size: 24),
            const SizedBox(width: 8),
            const Text('Life Autopilot'),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: _getStatusColor(_agentStatus),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                _agentStatus,
                style: const TextStyle(
                  fontSize: 12,
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _initDashboard,
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              ref.read(studentProvider.notifier).clearStudent();
              Navigator.pushReplacementNamed(context, '/setup');
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadDashboardData,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // Welcome section
                  _buildWelcomeSection(),
                  const SizedBox(height: 16),

                  // Next commitment section
                  _buildNextCommitmentSection(),
                  const SizedBox(height: 16),

                  // Context section
                  _buildContextSection(),
                  const SizedBox(height: 16),

                  // Agent status card
                  _buildAgentStatusCard(),
                  const SizedBox(height: 16),

                  // Recent events
                  _buildRecentEventsSection(),
                  const SizedBox(height: 16),

                  // Quick actions
                  _buildQuickActionsSection(),
                ],
              ),
            ),
    );
  }

  Widget _buildWelcomeSection() {
    final studentState = ref.read(studentProvider);
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome back${studentState.displayName != null ? ', ${studentState.displayName}' : ''}!',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Your day, kept on track',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.indigo[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                Icons.directions_walk,
                color: Colors.indigo[700],
                size: 32,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNextCommitmentSection() {
    if (_nextCommitment == null) {
      return Card(
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: const Padding(
          padding: EdgeInsets.all(20),
          child: Column(
            children: [
              Row(
                children: [
                  Icon(Icons.event_busy, color: Colors.grey),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'No commitments loaded',
                      style: TextStyle(color: Colors.grey),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                'Timetable import is the next mobile slice.',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.event, color: Colors.indigo),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _nextCommitment!.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.access_time, size: 16, color: Colors.grey),
                const SizedBox(width: 4),
                Text(
                  Formatters.formatTime(_nextCommitment!.startTime),
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
                const SizedBox(width: 16),
                Icon(Icons.location_on, size: 16, color: Colors.grey),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    _nextCommitment!.destination,
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.indigo[50],
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.auto_awesome, size: 16, color: Colors.indigo),
                  SizedBox(width: 4),
                  Text(
                    'Agent is monitoring',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.indigo,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContextSection() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.location_history, color: Colors.teal),
                const SizedBox(width: 12),
                const Text(
                  'Current Context',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildContextItem(
                    'Location',
                    _currentLocation != null
                        ? '${_currentLocation!.latitude.toStringAsFixed(4)}, ${_currentLocation!.longitude.toStringAsFixed(4)}'
                        : 'Unknown',
                    Icons.my_location,
                  ),
                ),
                Expanded(
                  child: _buildContextItem(
                    'Travel',
                    _nextCommitment != null ? 'Calculating...' : 'N/A',
                    Icons.directions_walk,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildContextItem(
                    'Status',
                    _agentStatus,
                    Icons.info,
                    color: _getStatusColor(_agentStatus),
                  ),
                ),
                Expanded(
                  child: _buildContextItem(
                    'Last Update',
                    Formatters.formatRelativeTime(DateTime.now()),
                    Icons.schedule,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContextItem(
    String label,
    String value,
    IconData icon, {
    Color? color,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            Icon(icon, size: 16, color: color ?? Colors.teal),
            const SizedBox(width: 4),
            Expanded(
              child: Text(
                value,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildAgentStatusCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.smart_toy, color: Colors.purple),
                const SizedBox(width: 12),
                const Text(
                  'Agent Status',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getStatusColor(_agentStatus) == Colors.green
                        ? Colors.green[100]
                        : Colors.orange[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _agentStatus,
                    style: TextStyle(
                      fontSize: 12,
                      color: _getStatusColor(_agentStatus) == Colors.green
                          ? Colors.green[800]
                          : Colors.orange[800],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            LinearProgressIndicator(
              value: _agentStatus == 'Ready' ? 1.0 : 0.5,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(Colors.purple),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentEventsSection() {
    if (_recentEvents.isEmpty) {
      return const SizedBox();
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.history, color: Colors.blue),
                const SizedBox(width: 12),
                const Text(
                  'Recent Agent Activity',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ..._recentEvents.take(3).map((event) => _buildEventItem(event)).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildEventItem(AgentEvent event) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: _getDecisionColor(event.decision).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              _getEventIcon(event.action),
              size: 16,
              color: _getDecisionColor(event.decision),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  event.decision,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: _getDecisionColor(event.decision),
                  ),
                ),
                Text(
                  event.reason,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  IconData _getEventIcon(String action) {
    switch (action) {
      case 'NOTIFICATION_SENT':
        return Icons.notification_add;
      case 'NOTIFICATION_SUPPRESSED':
        return Icons.notifications_off;
      case 'NO_ACTION':
        return Icons.pause;
      default:
        return Icons.history;
    }
  }

  Widget _buildQuickActionsSection() {
    return Row(
      children: [
        Expanded(
          child: _buildQuickActionButton(
            'Add Commitment',
            Icons.add_circle,
            Colors.indigo,
            () => _showAddCommitmentDialog(),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildQuickActionButton(
            'Import Timetable',
            Icons.upload_file,
            Colors.green,
            () => _showTimetableImportDialog(),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildQuickActionButton(
            'Ask Agent',
            Icons.smart_toy,
            Colors.purple,
            () => _showEvaluationDialog(),
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActionButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onPressed,
  ) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 20),
      label: Text(label, style: const TextStyle(fontSize: 12)),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      ),
    );
  }

  // Dialogs and screens
  void _showAddCommitmentDialog() {
    showDialog(
      context: context,
      builder: (context) => AddCommitmentDialog(onCommitmentAdded: (commitment) {
        _loadDashboardData();
      }),
    );
  }

  void _showTimetableImportDialog() {
    showDialog(
      context: context,
      builder: (context) => const TimetableImportDialog(),
    );
  }

  void _showEvaluationDialog() {
    showDialog(
      context: context,
      builder: (context) => const EvaluationDialog(),
    );
  }
}

// Additional screens and dialogs
class AddCommitmentDialog extends StatefulWidget {
  final Function(Commitment) onCommitmentAdded;

  const AddCommitmentDialog({super.key, required this.onCommitmentAdded});

  @override
  createState() => _AddCommitmentDialogState();
}

class _AddCommitmentDialogState extends State<AddCommitmentDialog> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _destinationController = TextEditingController();
  final _dateController = TextEditingController();
  final _timeController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _titleController.dispose();
    _destinationController.dispose();
    _dateController.dispose();
    _timeController.dispose();
    super.dispose();
  }

  Future<void> _saveCommitment() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isLoading = true);

    try {
      // Create commitment using API service
      // For now, just show success and call callback
      final commitment = Commitment(
        id: 'temp_${DateTime.now().millisecondsSinceEpoch}',
        title: _titleController.text,
        startTime: DateTime.parse('${_dateController.text} ${_timeController.text}'),
        destination: _destinationController.text,
        status: 'active',
      );

      widget.onCommitmentAdded(commitment);
      Navigator.of(context).pop();

      _showSuccessSnackBar('Commitment added successfully');
    } catch (e) {
      _showErrorSnackBar('Failed to add commitment: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add New Commitment'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _titleController,
              decoration: const InputDecoration(
                labelText: 'Title',
                hintText: 'e.g., Database Systems',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a title';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _destinationController,
              decoration: const InputDecoration(
                labelText: 'Destination',
                hintText: 'e.g., Engineering Building B',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a destination';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _dateController,
                    decoration: const InputDecoration(
                      labelText: 'Date',
                      hintText: '2024-01-15',
                      border: OutlineInputBorder(),
                    ),
                    readOnly: true,
                    onTap: () => _selectDate(context),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Please select a date';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _timeController,
                    decoration: const InputDecoration(
                      labelText: 'Time',
                      hintText: '14:00',
                      border: OutlineInputBorder(),
                    ),
                    readOnly: true,
                    onTap: () => _selectTime(context),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Please select a time';
                      }
                      return null;
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('CANCEL'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _saveCommitment,
          child: _isLoading
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('SAVE'),
        ),
      ],
    );
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null) {
      setState(() {
        _dateController.text = picked.toIso8601String().split('T')[0];
      });
    }
  }

  Future<void> _selectTime(BuildContext context) async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
    );
    if (picked != null) {
      setState(() {
        _timeController.text = picked.format(context);
      });
    }
  }
}

class TimetableImportDialog extends StatelessWidget {
  const TimetableImportDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Import Timetable'),
      content: const Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Timetable import will extract commitments from PDF, images, or text'),
          SizedBox(height: 16),
          Icon(Icons.upload_file, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text(
            'This feature will be available in the next mobile slice',
            style: TextStyle(color: Colors.grey),
            textAlign: TextAlign.center,
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('OK'),
        ),
      ],
    );
  }
}

class EvaluationDialog extends StatelessWidget {
  const EvaluationDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Ask Agent'),
      content: const Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Run autonomous evaluation manually'),
          SizedBox(height: 16),
          Icon(Icons.smart_toy, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text(
            'This will evaluate the current context and trigger agent actions',
            style: TextStyle(color: Colors.grey),
            textAlign: TextAlign.center,
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('CANCEL'),
        ),
        ElevatedButton(
          onPressed: () {
            // Trigger evaluation
            Navigator.of(context).pop();
            // TODO: Trigger evaluation from dashboard
          },
          child: const Text('EVALUATE'),
        ),
      ],
    );
  }
}

// Helper functions
extension TimeOfDayExtension on TimeOfDay {
  String format(BuildContext context) {
    final hour12 = this.hourOf12 == 12 ? 12 : this.hourOf12;
    final minute = this.minute.toString().padLeft(2, '0');
    final ampm = this.period == DayPeriod.am ? 'AM' : 'PM';
    return '$hour12:$minute $ampm';
  }
}

// Extension functions
extension DateTimeExtension on DateTime {
  String get formatToDateTimeString {
    return '${year}-${month.toString().padLeft(2, '0')}-${day.toString().padLeft(2, '0')} ' +
        '${hour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')}';
  }
}

// Constants
class Constants {
  static const String appName = 'Life Autopilot';
  static const String baseApiUrl = 'http://127.0.0.1:8000';
  static const String studentIdKey = 'student_id';
  static const String displayNameKey = 'display_name';
  static const String isFirstTimeKey = 'is_first_time';
}

// Formatters
class Formatters {
  static String formatTime(DateTime dateTime) {
    return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  static String formatRelativeTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays > 0) {
      return '${difference.inDays} ${difference.inDays == 1 ? 'day' : 'days'} ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} ${difference.inHours == 1 ? 'hour' : 'hours'} ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} ${difference.inMinutes == 1 ? 'minute' : 'minutes'} ago';
    } else {
      return 'Just now';
    }
  }
}

// Location utilities
class LocationUtils {
  static bool isLocationAvailable(Position? position) {
    return position != null && position.latitude != 0 && position.longitude != 0;
  }

  static String formatCoordinates(double latitude, double longitude) {
    return '${latitude.toStringAsFixed(4)}, ${longitude.toStringAsFixed(4)}';
  }
}

// Helper functions
Color _getStatusColor(String status) {
  switch (status) {
    case 'Ready':
      return Colors.green;
    case 'Initializing...':
    case 'Connecting to backend...':
    case 'Evaluating...':
      return Colors.orange;
    case 'Connection failed':
    case 'Evaluation failed':
      return Colors.red;
    default:
      return Colors.grey;
  }
}