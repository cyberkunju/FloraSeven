import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:flora_seven/utils/enhanced_error_handler.dart';

void main() {
  group('EnhancedErrorHandler', () {
    group('_determineErrorCategory', () {
      // We can't directly test private methods, so we'll test them indirectly
      // through the public methods that use them.

      test('should categorize DioException correctly', () {
        // Arrange
        final connectionTimeoutError = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.connectionTimeout,
        );

        final badResponseError = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.badResponse,
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 401,
          ),
        );

        final serverError = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.badResponse,
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 500,
          ),
        );

        // Act & Assert
        // We can't directly test the private method, but we can test the user-friendly message
        // which depends on the error category
        expect(
          EnhancedErrorHandler.getUserFriendlyErrorMessage(connectionTimeoutError),
          contains('Connection timed out'),
        );

        expect(
          EnhancedErrorHandler.getUserFriendlyErrorMessage(badResponseError),
          contains('not authorized'),
        );

        expect(
          EnhancedErrorHandler.getUserFriendlyErrorMessage(serverError),
          contains('server encountered an error'),
        );
      });

      test('should categorize network errors correctly', () {
        // Arrange
        final socketException = Exception('SocketException: Failed to connect');

        // Act & Assert
        expect(
          EnhancedErrorHandler.getUserFriendlyErrorMessage(socketException),
          contains('Network connection'),
        );
      });

      test('should categorize authentication errors correctly', () {
        // Arrange
        final authError = Exception('Authentication failed: Invalid token');

        // Act & Assert
        expect(
          EnhancedErrorHandler.getUserFriendlyErrorMessage(authError),
          contains('problem with your login'),
        );
      });
    });

    group('getUserFriendlyErrorMessage', () {
      test('should return appropriate message for null error', () {
        // Act
        final result = EnhancedErrorHandler.getUserFriendlyErrorMessage(null);

        // Assert
        expect(result, 'An unknown error occurred');
      });

      test('should return appropriate message for DioException', () {
        // Arrange
        final connectionError = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.connectionError,
        );

        // Act
        final result = EnhancedErrorHandler.getUserFriendlyErrorMessage(connectionError);

        // Assert
        expect(result, contains('Connection error'));
      });

      test('should return appropriate message for FormatException', () {
        // Arrange
        final formatException = FormatException('Invalid format');

        // Act
        final result = EnhancedErrorHandler.getUserFriendlyErrorMessage(formatException);

        // Assert
        expect(result, contains('problem processing the data'));
      });
    });

    group('handleWithFallback', () {
      test('should return result when no error occurs', () {
        // Arrange
        const expectedResult = 42;

        // Act
        final result = EnhancedErrorHandler.handleWithFallback<int>(
          0,
          'test operation',
          () => expectedResult,
        );

        // Assert
        expect(result, expectedResult);
      });
    });

    group('handleAsyncWithFallback', () {
      test('should return result when no error occurs', () async {
        // Arrange
        const expectedResult = 42;

        // Act
        final result = await EnhancedErrorHandler.handleAsyncWithFallback<int>(
          0,
          'test operation',
          () async => expectedResult,
        );

        // Assert
        expect(result, expectedResult);
      });
    });

    // Note: We're simplifying the retry tests to focus on the basic functionality
    // without relying on timing-dependent behavior which can be flaky in tests

    group('retryWithBackoffAndFallback', () {
      test('should return result on first attempt if successful', () async {
        // Arrange
        const expectedResult = 42;
        int attempts = 0;

        // Act
        final result = await EnhancedErrorHandler.retryWithBackoffAndFallback<int>(
          0,
          'test operation',
          () async {
            attempts++;
            return expectedResult;
          },
          maxRetries: 3,
          // Use zero delays for testing to avoid timing issues
          retryDelays: [0, 0, 0],
        );

        // Assert
        expect(result, expectedResult);
        expect(attempts, 1);
      });

      test('should return fallback value on error', () async {
        // Arrange
        const fallbackValue = 99;

        // Act
        final result = await EnhancedErrorHandler.retryWithBackoffAndFallback<int>(
          fallbackValue,
          'test operation',
          () async {
            throw Exception('Test error');
          },
          maxRetries: 1,
          // Use zero delays for testing to avoid timing issues
          retryDelays: [0],
        );

        // Assert
        expect(result, fallbackValue);
      });
    });
  });
}
