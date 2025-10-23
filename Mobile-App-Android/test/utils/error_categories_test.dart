import 'package:flutter_test/flutter_test.dart';
import 'package:flora_seven/utils/error_categories.dart';

void main() {
  group('ErrorCategory', () {
    test('should have the correct display names', () {
      // Assert
      expect(ErrorCategory.authentication.displayName, 'Authentication');
      expect(ErrorCategory.network.displayName, 'Network');
      expect(ErrorCategory.server.displayName, 'Server');
      expect(ErrorCategory.api.displayName, 'API');
      expect(ErrorCategory.validation.displayName, 'Validation');
      expect(ErrorCategory.database.displayName, 'Database');
      expect(ErrorCategory.ui.displayName, 'User Interface');
      expect(ErrorCategory.hardware.displayName, 'Hardware');
      expect(ErrorCategory.permission.displayName, 'Permission');
      expect(ErrorCategory.configuration.displayName, 'Configuration');
      expect(ErrorCategory.state.displayName, 'State Management');
      expect(ErrorCategory.unknown.displayName, 'Unknown');
    });

    test('should correctly identify retryable categories', () {
      // Assert
      expect(ErrorCategory.network.isRetryable, true);
      expect(ErrorCategory.server.isRetryable, true);
      expect(ErrorCategory.api.isRetryable, true);
      
      expect(ErrorCategory.authentication.isRetryable, false);
      expect(ErrorCategory.validation.isRetryable, false);
      expect(ErrorCategory.database.isRetryable, false);
      expect(ErrorCategory.ui.isRetryable, false);
      expect(ErrorCategory.hardware.isRetryable, false);
      expect(ErrorCategory.permission.isRetryable, false);
      expect(ErrorCategory.configuration.isRetryable, false);
      expect(ErrorCategory.state.isRetryable, false);
      expect(ErrorCategory.unknown.isRetryable, false);
    });

    test('should correctly identify reportable categories', () {
      // All categories should be reportable
      for (final category in ErrorCategory.values) {
        expect(category.shouldReport, true, reason: '${category.name} should be reportable');
      }
    });

    test('should have user-friendly messages for all categories', () {
      // Assert
      expect(ErrorCategory.authentication.userFriendlyMessage, contains('problem with your login'));
      expect(ErrorCategory.network.userFriendlyMessage, contains('Network connection issue'));
      expect(ErrorCategory.server.userFriendlyMessage, contains('Server is currently unavailable'));
      expect(ErrorCategory.api.userFriendlyMessage, contains('Server communication error'));
      expect(ErrorCategory.validation.userFriendlyMessage, contains('Invalid input data'));
      expect(ErrorCategory.database.userFriendlyMessage, contains('Data storage error'));
      expect(ErrorCategory.ui.userFriendlyMessage, contains('Display error'));
      expect(ErrorCategory.hardware.userFriendlyMessage, contains('Hardware communication error'));
      expect(ErrorCategory.permission.userFriendlyMessage, contains('Permission denied'));
      expect(ErrorCategory.configuration.userFriendlyMessage, contains('Configuration error'));
      expect(ErrorCategory.state.userFriendlyMessage, contains('Application state error'));
      expect(ErrorCategory.unknown.userFriendlyMessage, contains('unexpected error'));
    });
  });
}
