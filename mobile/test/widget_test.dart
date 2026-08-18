import 'package:flutter_test/flutter_test.dart';
import 'package:life_autopilot_agentic/main.dart';

void main() {
  testWidgets('shows the Life Autopilot dashboard', (tester) async {
    await tester.pumpWidget(const LifeAutopilotApp());

    expect(find.text('Your day, kept on track'), findsOneWidget);
    expect(find.text('Agent activity'), findsOneWidget);
  });
}

