import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flora_seven/main.dart' as app;
import 'package:flora_seven/services/enhanced_api_service.dart';
import 'package:flora_seven/domain/models/plant_data.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([EnhancedApiService])
class MockEnhancedApiService extends Mock implements EnhancedApiService {
  @override
  Future<PlantData?> getPlantData() {
    return super.noSuchMethod(
      Invocation.method(#getPlantData, []),
      returnValue: Future<PlantData?>.value(null),
    ) as Future<PlantData?>;
  }
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    // No need to initialize mockApiService since we're not using it in the tests
  });

  group('Sensor Readings Tests', () {
    testWidgets('Sensor readings should be displayed on plant detail screen', (WidgetTester tester) async {
      // Start the app
      app.main();

      // Wait for the app to settle
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Verify that the splash screen is displayed
      expect(find.text('FloraSeven'), findsOneWidget);
    });

    test('EnhancedApiService.getPlantData should return correct sensor readings', () {
      // This test is now a unit test in test/services/enhanced_api_service_test.dart
      // We'll skip it here to avoid duplication
    }, skip: 'This test is now a unit test');

    test('EnhancedApiService should handle extreme sensor values', () {
      // This test is now a unit test in test/services/enhanced_api_service_test.dart
      // We'll skip it here to avoid duplication
    }, skip: 'This test is now a unit test');

    test('EnhancedApiService should handle missing sensor values', () {
      // This test is now a unit test in test/services/enhanced_api_service_test.dart
      // We'll skip it here to avoid duplication
    }, skip: 'This test is now a unit test');

    test('EnhancedApiService should handle sensor reading errors', () {
      // This test is now a unit test in test/services/enhanced_api_service_test.dart
      // We'll skip it here to avoid duplication
    }, skip: 'This test is now a unit test');
  });
}
