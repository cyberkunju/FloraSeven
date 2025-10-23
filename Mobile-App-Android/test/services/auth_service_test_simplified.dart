import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:mockito/mockito.dart';
import 'package:flora_seven/services/auth_service.dart';
import 'package:flora_seven/services/config_service.dart';

// Create manual mocks for the dependencies
class MockConfigService extends Mock implements ConfigService {}
class MockFlutterSecureStorage extends Mock implements FlutterSecureStorage {}

void main() {
  late MockConfigService mockConfigService;
  late MockFlutterSecureStorage mockSecureStorage;
  late AuthService authService;

  setUp(() {
    mockConfigService = MockConfigService();
    mockSecureStorage = MockFlutterSecureStorage();

    // Configure the mock ConfigService
    when(mockConfigService.getApiUrl('/auth/status')).thenReturn('https://example.com/api/auth/status');
    when(mockConfigService.getApiUrl('/login')).thenReturn('https://example.com/api/login');
    when(mockConfigService.getApiUrl('/logout')).thenReturn('https://example.com/api/logout');
    when(mockConfigService.getServerUrl()).thenReturn('https://example.com');

    // Create the AuthService with mocked dependencies
    authService = AuthService(
      configService: mockConfigService,
      secureStorage: mockSecureStorage,
    );
  });

  group('AuthService', () {
    test('isLoggedIn should check credentials', () async {
      // Arrange
      when(mockSecureStorage.read(key: 'auth_username')).thenAnswer((_) async => 'testuser');
      when(mockSecureStorage.read(key: 'auth_password')).thenAnswer((_) async => 'testpass');

      // Act
      final result = await authService.isLoggedIn();

      // Assert
      expect(result, true);
    });

    test('getUsername should return stored username', () async {
      // Arrange
      when(mockSecureStorage.read(key: 'auth_username')).thenAnswer((_) async => 'testuser');

      // Act
      final result = await authService.getUsername();

      // Assert
      expect(result, 'testuser');
    });

    test('getAuthHeader should return Basic auth header', () async {
      // Arrange
      when(mockSecureStorage.read(key: 'auth_username')).thenAnswer((_) async => 'testuser');
      when(mockSecureStorage.read(key: 'auth_password')).thenAnswer((_) async => 'testpass');

      // Act
      final result = await authService.getAuthHeader();

      // Assert
      expect(result, 'Basic ${base64Encode(utf8.encode('testuser:testpass'))}');
    });
  });
}
