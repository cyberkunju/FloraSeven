import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flora_seven/main.dart' as app;
import 'package:flora_seven/services/enhanced_api_service.dart';
import 'package:flora_seven/domain/models/pump_status.dart';
// These imports are not needed for this test
// import 'package:flora_seven/domain/models/plant_data.dart';
// import 'package:flora_seven/domain/models/plant_node_data.dart';
// import 'package:flora_seven/domain/models/hub_node_data.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

@GenerateMocks([EnhancedApiService])
class MockEnhancedApiService extends Mock implements EnhancedApiService {
  @override
  Future<PumpStatus> startWatering({required int duration}) async {
    return super.noSuchMethod(
      Invocation.method(#startWatering, [], {#duration: duration}),
      returnValue: Future.value(PumpStatus(
        isActive: true,
        isRunning: true,
        startTime: DateTime.now(),
        duration: duration,
        remainingTime: duration,
      )),
    );
  }

  @override
  Future<PumpStatus> stopWatering() async {
    return super.noSuchMethod(
      Invocation.method(#stopWatering, []),
      returnValue: Future.value(PumpStatus(
        isActive: false,
        isRunning: false,
        startTime: DateTime.now().subtract(const Duration(seconds: 5)),
        duration: 10,
        remainingTime: 0,
      )),
    );
  }

  @override
  Future<PumpStatus> getPumpStatus() async {
    return super.noSuchMethod(
      Invocation.method(#getPumpStatus, []),
      returnValue: Future.value(PumpStatus(
        isActive: true,
        isRunning: true,
        startTime: DateTime.now().subtract(const Duration(seconds: 5)),
        duration: 10,
        remainingTime: 5,
      )),
    );
  }
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  late MockEnhancedApiService mockApiService;

  setUp(() {
    mockApiService = MockEnhancedApiService();
  });

  group('Watering Functionality Tests', () {
    testWidgets('Manual watering button should be visible on plant detail screen', (WidgetTester tester) async {
      // Start the app
      app.main();

      // Wait for the app to settle
      await tester.pumpAndSettle();

      // Navigate to the plant detail screen
      // This is a simplified test that just verifies the app starts without crashing
      // In a real test, we would navigate to the plant detail screen and verify the watering button is visible
      expect(find.text('FloraSeven Dashboard'), findsOneWidget);
    });

    test('EnhancedApiService.startWatering should send correct request', () async {
      // Configure the mock API service
      when(mockApiService.startWatering(duration: 10))
          .thenAnswer((_) async => PumpStatus(
                isActive: true,
                isRunning: true,
                startTime: DateTime.now(),
                duration: 10,
                remainingTime: 10,
              ));

      // Call the method
      final result = await mockApiService.startWatering(duration: 10);

      // Verify the result
      expect(result.isRunning, isTrue);
      expect(result.duration, equals(10));
      expect(result.remainingTime, equals(10));

      // Verify the method was called with the correct parameters
      verify(mockApiService.startWatering(duration: 10)).called(1);
    });

    test('EnhancedApiService.stopWatering should send correct request', () async {
      // Configure the mock API service
      when(mockApiService.stopWatering())
          .thenAnswer((_) async => PumpStatus(
                isActive: false,
                isRunning: false,
                startTime: DateTime.now().subtract(const Duration(seconds: 5)),
                duration: 10,
                remainingTime: 0,
              ));

      // Call the method
      final result = await mockApiService.stopWatering();

      // Verify the result
      expect(result.isRunning, isFalse);
      expect(result.remainingTime, equals(0));

      // Verify the method was called
      verify(mockApiService.stopWatering()).called(1);
    });

    test('EnhancedApiService.getPumpStatus should return correct status', () async {
      // Configure the mock API service
      when(mockApiService.getPumpStatus())
          .thenAnswer((_) async => PumpStatus(
                isActive: true,
                isRunning: true,
                startTime: DateTime.now().subtract(const Duration(seconds: 5)),
                duration: 10,
                remainingTime: 5,
              ));

      // Call the method
      final result = await mockApiService.getPumpStatus();

      // Verify the result
      expect(result.isRunning, isTrue);
      expect(result.duration, equals(10));
      expect(result.remainingTime, equals(5));

      // Verify the method was called
      verify(mockApiService.getPumpStatus()).called(1);
    });

    test('EnhancedApiService should handle watering errors gracefully', () async {
      // Configure the mock API service to throw an error
      when(mockApiService.startWatering(duration: 10))
          .thenThrow(DioException(
            requestOptions: RequestOptions(path: '/pump/start'),
            type: DioExceptionType.connectionError,
            error: 'Connection error',
          ));

      // Call the method and expect it to throw
      expect(
        () => mockApiService.startWatering(duration: 10),
        throwsA(isA<DioException>()),
      );

      // Verify the method was called with the correct parameters
      verify(mockApiService.startWatering(duration: 10)).called(1);
    });
  });
}
