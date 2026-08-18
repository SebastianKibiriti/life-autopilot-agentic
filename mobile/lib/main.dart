import 'package:flutter/material.dart';

void main() {
  runApp(const LifeAutopilotApp());
}

class LifeAutopilotApp extends StatelessWidget {
  const LifeAutopilotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Life Autopilot',
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: const DashboardPage(),
    );
  }
}

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Life Autopilot')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: const [
          Text('Your day, kept on track', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Text('The agent watches context and acts before you have to ask.'),
          SizedBox(height: 24),
          Card(
            child: Padding(
              padding: EdgeInsets.all(20),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('Agent status', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text('Local foundation ready'),
                SizedBox(height: 16),
                LinearProgressIndicator(value: 0.2),
              ]),
            ),
          ),
          SizedBox(height: 12),
          Card(child: ListTile(leading: Icon(Icons.event), title: Text('No commitments loaded'), subtitle: Text('Timetable import is the next mobile slice.'))),
          Card(child: ListTile(leading: Icon(Icons.history), title: Text('Agent activity'), subtitle: Text('Decision history will appear here.'))),
        ],
      ),
    );
  }
}

