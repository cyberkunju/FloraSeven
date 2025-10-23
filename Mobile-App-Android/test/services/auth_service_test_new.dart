import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:flora_seven/services/auth_service.dart';
import 'package:flora_seven/services/config_service.dart';

import 'auth_service_test_new.mocks.dart';

@GenerateMocks([ConfigService, FlutterSecureStorage])
void main() {
  group('AuthService', () {
    late MockConfigService mockConfigService;
    late MockFlutterSecureStorage mockSecureStorage;
    late AuthService authService;

    setUp(() {
      mockConfigService = MockConfigService();
      mockSecureStorage = MockFlutterSecureStorage();

      authService = AuthService(
        configService: mockConfigService,
        secureStorage: mockSecureStorage,
      );
    });

    group('isLoggedIn', () {
      test('should return true when credentials are stored', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, true);
      });

      test('should return false when username is missing', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => null);
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, false);
      });

      test('should return false when password is missing', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, false);
      });
    });

    group('getUsername', () {
      test('should return username when stored', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');

        // Act
        final result = await authService.getUsername();

        // Assert
        expect(result, 'testuser');
      });

      test('should return null when username is not stored', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.getUsername();

        // Assert
        expect(result, null);
      });
    });

    group('getAuthHeader', () {
      test('should return Basic auth header when credentials are stored', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        // Act
        final result = await authService.getAuthHeader();

        // Assert
        final expectedHeader = 'Basic ${base64Encode(utf8.encode('testuser:testpass'))}';
        expect(result, expectedHeader);
      });

      test('should return null when username is missing', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => null);
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        // Act
        final result = await authService.getAuthHeader();

        // Assert
        expect(result, null);
      });

      test('should return null when password is missing', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.getAuthHeader();

        // Assert
        expect(result, null);
      });
    });

    group('clearCredentials', () {
      test('should delete stored credentials', () async {
        // Arrange
        when(mockSecureStorage.delete(key: 'auth_username'))
            .thenAnswer((_) async => {});
        when(mockSecureStorage.delete(key: 'auth_password'))
            .thenAnswer((_) async => {});

        // Act
        await authService.clearCredentials();

        // Assert
        verify(mockSecureStorage.delete(key: 'auth_username')).called(1);
        verify(mockSecureStorage.delete(key: 'auth_password')).called(1);
      });
    });
  });
}
