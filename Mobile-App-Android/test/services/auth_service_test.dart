import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
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
    when(mockConfigService.getApiUrl('/status')).thenReturn('https://example.com/api/status');
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
    group('isAuthRequired', () {
      // Note: We can't test the cached value directly because we can't set private fields
      // without reflection, which is not available in Flutter tests.
      // Instead, we'll test the network calls and responses.

      test('should fetch auth status from server if not cached', () async {
        // Arrange
        final responseJson = {'auth_required': true};
        final response = http.Response(json.encode(responseJson), 200);

        when(http.get(Uri.parse('https://example.com/api/auth/status')))
            .thenAnswer((_) async => response);

        // Act
        final result = await authService.isAuthRequired();

        // Assert
        expect(result, true);
        verify(mockConfigService.getApiUrl('/auth/status')).called(1);
      });

      test('should try status endpoint if auth/status fails', () async {
        // Arrange
        final authStatusResponse = http.Response('Not Found', 404);
        final statusResponse = http.Response('Unauthorized', 401);

        when(http.get(Uri.parse('https://example.com/api/auth/status')))
            .thenAnswer((_) async => authStatusResponse);
        when(http.get(Uri.parse('https://example.com/api/status')))
            .thenAnswer((_) async => statusResponse);

        // Act
        final result = await authService.isAuthRequired();

        // Assert
        expect(result, true);
        verify(mockConfigService.getApiUrl('/auth/status')).called(1);
        verify(mockConfigService.getApiUrl('/status')).called(1);
      });

      test('should return true on error for safety', () async {
        // Arrange
        when(http.get(Uri.parse('https://example.com/api/auth/status')))
            .thenThrow(Exception('Network error'));

        // Act
        final result = await authService.isAuthRequired();

        // Assert
        expect(result, true);
        verify(mockConfigService.getApiUrl('/auth/status')).called(1);
      });
    });

    group('login', () {
      test('should return true on successful login', () async {
        // Arrange
        final responseJson = {'success': true};
        final response = http.Response(json.encode(responseJson), 200);

        when(http.post(
          Uri.parse('https://example.com/api/login'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'username': 'testuser',
            'password': 'testpass',
          }),
        )).thenAnswer((_) async => response);

        when(mockSecureStorage.write(key: 'auth_username', value: 'testuser'))
            .thenAnswer((_) async {});
        when(mockSecureStorage.write(key: 'auth_password', value: 'testpass'))
            .thenAnswer((_) async {});

        // Act
        final result = await authService.login('testuser', 'testpass');

        // Assert
        expect(result, true);
        verify(mockConfigService.getApiUrl('/login')).called(1);
        verify(mockSecureStorage.write(key: 'auth_username', value: 'testuser')).called(1);
        verify(mockSecureStorage.write(key: 'auth_password', value: 'testpass')).called(1);
      });

      test('should return false on failed login', () async {
        // Arrange
        final responseJson = {'success': false, 'message': 'Invalid credentials'};
        final response = http.Response(json.encode(responseJson), 200);

        when(http.post(
          Uri.parse('https://example.com/api/login'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'username': 'testuser',
            'password': 'wrongpass',
          }),
        )).thenAnswer((_) async => response);

        // Act
        final result = await authService.login('testuser', 'wrongpass');

        // Assert
        expect(result, false);
        verify(mockConfigService.getApiUrl('/login')).called(1);
        verifyNever(mockSecureStorage.write(key: 'auth_username', value: 'testuser'));
        verifyNever(mockSecureStorage.write(key: 'auth_password', value: 'wrongpass'));
      });

      test('should return false on network error', () async {
        // Arrange
        when(http.post(
          Uri.parse('https://example.com/api/login'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'username': 'testuser',
            'password': 'testpass',
          }),
        )).thenThrow(Exception('Network error'));

        // Act
        final result = await authService.login('testuser', 'testpass');

        // Assert
        expect(result, false);
        verify(mockConfigService.getApiUrl('/login')).called(1);
        verifyNever(mockSecureStorage.write(key: 'auth_username', value: 'testuser'));
        verifyNever(mockSecureStorage.write(key: 'auth_password', value: 'testpass'));
      });
    });

    group('logout', () {
      test('should return true on successful logout', () async {
        // Arrange
        final response = http.Response('', 200);

        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        when(http.post(
          Uri.parse('https://example.com/api/logout'),
          headers: {'Authorization': 'Basic ${base64Encode(utf8.encode('testuser:testpass'))}'},
        )).thenAnswer((_) async => response);

        when(mockSecureStorage.delete(key: 'auth_username'))
            .thenAnswer((_) async {});
        when(mockSecureStorage.delete(key: 'auth_password'))
            .thenAnswer((_) async {});

        // Act
        final result = await authService.logout();

        // Assert
        expect(result, true);
        verify(mockConfigService.getApiUrl('/logout')).called(1);
        verify(mockSecureStorage.delete(key: 'auth_username')).called(1);
        verify(mockSecureStorage.delete(key: 'auth_password')).called(1);
      });

      test('should return true if already logged out', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => null);
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.logout();

        // Assert
        expect(result, true);
        verifyNever(mockConfigService.getApiUrl('/logout'));
        verifyNever(mockSecureStorage.delete(key: 'auth_username'));
        verifyNever(mockSecureStorage.delete(key: 'auth_password'));
      });

      test('should clear credentials and return false on error', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        when(http.post(
          Uri.parse('https://example.com/api/logout'),
          headers: {'Authorization': 'Basic ${base64Encode(utf8.encode('testuser:testpass'))}'},
        )).thenThrow(Exception('Network error'));

        when(mockSecureStorage.delete(key: 'auth_username'))
            .thenAnswer((_) async {});
        when(mockSecureStorage.delete(key: 'auth_password'))
            .thenAnswer((_) async {});

        // Act
        final result = await authService.logout();

        // Assert
        expect(result, false);
        verify(mockConfigService.getApiUrl('/logout')).called(1);
        verify(mockSecureStorage.delete(key: 'auth_username')).called(1);
        verify(mockSecureStorage.delete(key: 'auth_password')).called(1);
      });
    });

    group('isLoggedIn', () {
      test('should return true if credentials are stored', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, true);
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
        verify(mockSecureStorage.read(key: 'auth_password')).called(1);
      });

      test('should return false if username is missing', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => null);
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, false);
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
        verify(mockSecureStorage.read(key: 'auth_password')).called(1);
      });

      test('should return false if password is missing', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, false);
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
        verify(mockSecureStorage.read(key: 'auth_password')).called(1);
      });

      test('should return false on error', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenThrow(Exception('Storage error'));

        // Act
        final result = await authService.isLoggedIn();

        // Assert
        expect(result, false);
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
        verifyNever(mockSecureStorage.read(key: 'auth_password'));
      });
    });

    group('getAuthHeader', () {
      test('should return Basic auth header if credentials are stored', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        // Act
        final result = await authService.getAuthHeader();

        // Assert
        expect(result, 'Basic ${base64Encode(utf8.encode('testuser:testpass'))}');
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
        verify(mockSecureStorage.read(key: 'auth_password')).called(1);
      });

      test('should return null if username is missing', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => null);
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => 'testpass');

        // Act
        final result = await authService.getAuthHeader();

        // Assert
        expect(result, null);
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
        verify(mockSecureStorage.read(key: 'auth_password')).called(1);
      });

      test('should return null if password is missing', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');
        when(mockSecureStorage.read(key: 'auth_password'))
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.getAuthHeader();

        // Assert
        expect(result, null);
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
        verify(mockSecureStorage.read(key: 'auth_password')).called(1);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenThrow(Exception('Storage error'));

        // Act
        final result = await authService.getAuthHeader();

        // Assert
        expect(result, null);
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
        verifyNever(mockSecureStorage.read(key: 'auth_password'));
      });
    });

    group('getUsername', () {
      test('should return username if stored', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => 'testuser');

        // Act
        final result = await authService.getUsername();

        // Assert
        expect(result, 'testuser');
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
      });

      test('should return null if username is not stored', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenAnswer((_) async => null);

        // Act
        final result = await authService.getUsername();

        // Assert
        expect(result, null);
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockSecureStorage.read(key: 'auth_username'))
            .thenThrow(Exception('Storage error'));

        // Act
        final result = await authService.getUsername();

        // Assert
        expect(result, null);
        verify(mockSecureStorage.read(key: 'auth_username')).called(1);
      });
    });

    group('clearCredentials', () {
      test('should delete stored credentials', () async {
        // Arrange
        when(mockSecureStorage.delete(key: 'auth_username'))
            .thenAnswer((_) async {});
        when(mockSecureStorage.delete(key: 'auth_password'))
            .thenAnswer((_) async {});

        // Act
        await authService.clearCredentials();

        // Assert
        verify(mockSecureStorage.delete(key: 'auth_username')).called(1);
        verify(mockSecureStorage.delete(key: 'auth_password')).called(1);
      });

      test('should handle errors gracefully', () async {
        // Arrange
        when(mockSecureStorage.delete(key: 'auth_username'))
            .thenThrow(Exception('Storage error'));

        // Act & Assert
        // Should not throw an exception
        await expectLater(authService.clearCredentials(), completes);
        verify(mockSecureStorage.delete(key: 'auth_username')).called(1);
      });
    });
  });
}


