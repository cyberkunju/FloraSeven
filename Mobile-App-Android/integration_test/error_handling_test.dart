import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flora_seven/main.dart' as app;
import 'package:flora_seven/services/enhanced_api_service.dart';
import 'package:flora_seven/utils/enhanced_error_handler.dart';
import 'package:flora_seven/utils/error_categories.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

@GenerateMocks([EnhancedApiService])
class MockEnhancedApiService extends Mock implements EnhancedApiService {}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  // We don't need to use mockApiService in this test file since we're testing
  // the EnhancedErrorHandler directly, not the API service

  group('Error Handling Integration Tests', () {
    testWidgets('App starts without crashing', (WidgetTester tester) async {
      // Start the app
      app.main();

      // Wait for the app to settle
      await tester.pumpAndSettle();

      // Verify that the dashboard screen is displayed
      expect(find.text('FloraSeven Dashboard'), findsOneWidget);
    });

    test('EnhancedErrorHandler provides user-friendly messages', () {
      // Test network error
      final networkError = DioException(
        requestOptions: RequestOptions(path: '/status'),
        type: DioExceptionType.connectionError,
        error: 'Connection error',
      );
      final networkMessage = EnhancedErrorHandler.getUserFriendlyErrorMessage(networkError);
      expect(networkMessage, contains('network'));
      expect(EnhancedErrorHandler.getErrorCategory(networkError), equals(ErrorCategory.network));

      // Test server error
      final serverError = DioException(
        requestOptions: RequestOptions(path: '/status'),
        type: DioExceptionType.badResponse,
        response: Response(
          requestOptions: RequestOptions(path: '/status'),
          statusCode: 500,
          data: {'error': 'Internal server error'},
        ),
      );
      final serverMessage = EnhancedErrorHandler.getUserFriendlyErrorMessage(serverError);
      expect(serverMessage, contains('server'));
      expect(EnhancedErrorHandler.getErrorCategory(serverError), equals(ErrorCategory.server));

      // Test authentication error
      final authError = DioException(
        requestOptions: RequestOptions(path: '/status'),
        type: DioExceptionType.badResponse,
        response: Response(
          requestOptions: RequestOptions(path: '/status'),
          statusCode: 401,
          data: {'error': 'Unauthorized'},
        ),
      );
      final authMessage = EnhancedErrorHandler.getUserFriendlyErrorMessage(authError);
      expect(authMessage, contains('authorized'));
      expect(EnhancedErrorHandler.getErrorCategory(authError), equals(ErrorCategory.authentication));

      // Test validation error
      final validationError = DioException(
        requestOptions: RequestOptions(path: '/status'),
        type: DioExceptionType.badResponse,
        response: Response(
          requestOptions: RequestOptions(path: '/status'),
          statusCode: 422,
          data: {'error': 'Validation failed'},
        ),
      );
      final validationMessage = EnhancedErrorHandler.getUserFriendlyErrorMessage(validationError);
      expect(validationMessage, contains('invalid'));
      expect(EnhancedErrorHandler.getErrorCategory(validationError), equals(ErrorCategory.validation));

      // Test unknown error
      final unknownError = Exception('Unknown error');
      final unknownMessage = EnhancedErrorHandler.getUserFriendlyErrorMessage(unknownError);
      expect(unknownMessage, contains('unexpected'));
      expect(EnhancedErrorHandler.getErrorCategory(unknownError), equals(ErrorCategory.unknown));
    });

    test('EnhancedErrorHandler handles null errors gracefully', () {
      final message = EnhancedErrorHandler.getUserFriendlyErrorMessage(null);
      expect(message, contains('unknown'));
      expect(EnhancedErrorHandler.getErrorCategory(null), equals(ErrorCategory.unknown));
    });

    // Note: The following tests are commented out because we can't inject our mock into ServiceLocator
    // in the integration test environment. These would work in a unit test environment.

    /*
    testWidgets('EnhancedErrorDisplay shows appropriate error UI', (WidgetTester tester) async {
      // Configure the mock API service to throw an error
      when(mockApiService.getPlantData()).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/status'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ),
      );

      // Start the app
      app.main();

      // Wait for the app to settle
      await tester.pumpAndSettle();

      // Verify that the error display is shown
      expect(find.text('Network Error'), findsOneWidget);
      expect(find.text('Connection error'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });
    */
  });
}
