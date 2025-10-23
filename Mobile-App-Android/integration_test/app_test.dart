import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flora_seven/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('end-to-end test', () {
    testWidgets('tap on the water now button and verify dialog appears',
        (WidgetTester tester) async {
      // Start the app
      app.main();
      await tester.pumpAndSettle();

      // Wait for splash screen to finish and navigate to dashboard
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Verify that we're on the dashboard screen
      expect(find.text('FloraSeven Dashboard'), findsOneWidget);

      // Find and tap the "Water Now" button
      final waterNowButton = find.text('Water Now');
      expect(waterNowButton, findsOneWidget);
      await tester.tap(waterNowButton);
      await tester.pumpAndSettle();

      // Verify that the watering dialog appears
      expect(find.text('Manual Watering'), findsOneWidget);
      expect(find.text('Set watering duration:'), findsOneWidget);
      expect(find.byType(Slider), findsOneWidget);

      // Tap the "Cancel" button to dismiss the dialog
      await tester.tap(find.text('Cancel'));
      await tester.pumpAndSettle();

      // Verify that the dialog is dismissed
      expect(find.text('Manual Watering'), findsNothing);
    });

    testWidgets('navigate to settings screen and back',
        (WidgetTester tester) async {
      // Start the app
      app.main();
      await tester.pumpAndSettle();

      // Wait for splash screen to finish and navigate to dashboard
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Verify that we're on the dashboard screen
      expect(find.text('FloraSeven Dashboard'), findsOneWidget);

      // Find and tap the settings button
      final settingsButton = find.byIcon(Icons.settings);
      expect(settingsButton, findsOneWidget);
      await tester.tap(settingsButton);
      await tester.pumpAndSettle();

      // Verify that we're on the settings screen
      expect(find.text('Settings'), findsOneWidget);

      // Find and tap the back button
      final backButton = find.byType(BackButton);
      expect(backButton, findsOneWidget);
      await tester.tap(backButton);
      await tester.pumpAndSettle();

      // Verify that we're back on the dashboard screen
      expect(find.text('FloraSeven Dashboard'), findsOneWidget);
    });

    testWidgets('navigate to plant detail screen and back',
        (WidgetTester tester) async {
      // Start the app
      app.main();
      await tester.pumpAndSettle();

      // Wait for splash screen to finish and navigate to dashboard
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Verify that we're on the dashboard screen
      expect(find.text('FloraSeven Dashboard'), findsOneWidget);

      // Find and tap the "Details" button
      final detailsButton = find.text('Details');
      expect(detailsButton, findsOneWidget);
      await tester.tap(detailsButton);
      await tester.pumpAndSettle();

      // Verify that we're on the plant detail screen
      expect(find.text('Plant Details'), findsOneWidget);

      // Find and tap the back button
      final backButton = find.byType(BackButton);
      expect(backButton, findsOneWidget);
      await tester.tap(backButton);
      await tester.pumpAndSettle();

      // Verify that we're back on the dashboard screen
      expect(find.text('FloraSeven Dashboard'), findsOneWidget);
    });
  });
}
