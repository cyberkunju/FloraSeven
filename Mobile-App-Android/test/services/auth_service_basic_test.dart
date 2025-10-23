import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:mockito/mockito.dart';
import 'package:flora_seven/services/auth_service.dart';
import 'package:flora_seven/services/config_service.dart';

// Create manual mocks for the dependencies
class MockConfigService extends Mock implements ConfigService {}
class MockFlutterSecureStorage extends Mock implements FlutterSecureStorage {}

void main() {
  group('AuthService', () {
    test('isLoggedIn should check credentials', () async {
      // Arrange
      final mockConfigService = MockConfigService();
      final mockSecureStorage = MockFlutterSecureStorage();
      
      final authService = AuthService(
        configService: mockConfigService,
        secureStorage: mockSecureStorage,
      );
      
      when(mockSecureStorage.read(key: 'auth_username')).thenAnswer((_) async => 'testuser');
      when(mockSecureStorage.read(key: 'auth_password')).thenAnswer((_) async => 'testpass');

      // Act
      final result = await authService.isLoggedIn();

      // Assert
      expect(result, true);
    });
  });
}
