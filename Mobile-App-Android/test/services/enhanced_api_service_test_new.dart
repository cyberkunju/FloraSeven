import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:flora_seven/services/enhanced_api_service.dart';
import 'package:flora_seven/services/auth_service.dart';
import 'package:flora_seven/services/config_service.dart';
import 'package:flora_seven/domain/models/thresholds.dart';

import 'enhanced_api_service_test_new.mocks.dart';

@GenerateMocks([ConfigService, AuthService, Dio])
void main() {
  late MockConfigService mockConfigService;
  late MockAuthService mockAuthService;
  late MockDio mockDio;
  late EnhancedApiService apiService;

  setUp(() {
    mockConfigService = MockConfigService();
    mockAuthService = MockAuthService();
    mockDio = MockDio();

    // Configure the mock ConfigService
    when(mockConfigService.getApiUrl('/status')).thenReturn('https://example.com/api/status');
    when(mockConfigService.getApiUrl('/settings/thresholds')).thenReturn('https://example.com/api/settings/thresholds');
    when(mockConfigService.getApiUrl('/image/latest')).thenReturn('https://example.com/api/image/latest');
    when(mockConfigService.getServerUrl()).thenReturn('https://example.com');

    // Configure the mock AuthService
    when(mockAuthService.getAuthHeader()).thenAnswer((_) async => 'Bearer test-token');

    // Configure the mock Dio
    when(mockDio.options).thenReturn(BaseOptions());
    when(mockDio.interceptors).thenReturn(Interceptors());

    // Create the EnhancedApiService with mocked dependencies
    apiService = EnhancedApiService(
      configService: mockConfigService,
      authService: mockAuthService,
      dio: mockDio,
    );
  });

  group('EnhancedApiService', () {
    group('isServerAvailable', () {
      test('should return true when server is available', () async {
        // Arrange
        final response = Response(
          requestOptions: RequestOptions(path: '/status'),
          statusCode: 200,
          data: {'status': 'ok'},
        );

        when(mockDio.get(
          'https://example.com/api/status',
          options: anyNamed('options'),
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.isServerAvailable();

        // Assert
        expect(result, true);
      });

      test('should return false when server returns error status code', () async {
        // Arrange
        final response = Response(
          requestOptions: RequestOptions(path: '/status'),
          statusCode: 500,
          data: {'error': 'Internal server error'},
        );

        when(mockDio.get(
          'https://example.com/api/status',
          options: anyNamed('options'),
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.isServerAvailable();

        // Assert
        expect(result, false);
      });

      test('should return false on network error', () async {
        // Arrange
        when(mockDio.get(
          'https://example.com/api/status',
          options: anyNamed('options'),
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/status'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await apiService.isServerAvailable();

        // Assert
        expect(result, false);
      });
    });

    group('getThresholds', () {
      test('should return Thresholds on success', () async {
        // Arrange
        final thresholdsJson = {
          'moistureLow': 40,
          'moistureHigh': 70,
          'temperatureLow': 18.0,
          'temperatureHigh': 28.0,
          'lightIntensityLow': 5000.0,
          'lightIntensityHigh': 20000.0,
          'ecLow': 800.0,
          'ecHigh': 1500.0,
          'phLow': 5.8,
          'phHigh': 6.8,
          'uvIndexLow': 0.0,
          'uvIndexHigh': 5.0,
        };

        final response = Response(
          requestOptions: RequestOptions(path: '/settings/thresholds'),
          statusCode: 200,
          data: thresholdsJson,
        );

        when(mockDio.get('https://example.com/api/settings/thresholds'))
            .thenAnswer((_) async => response);

        // Act
        final result = await apiService.getThresholds();

        // Assert
        expect(result, isA<Thresholds>());
        expect(result?.moistureLow, 40);
        expect(result?.moistureHigh, 70);
        expect(result?.temperatureLow, 18.0);
        expect(result?.temperatureHigh, 28.0);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get('https://example.com/api/settings/thresholds'))
            .thenThrow(DioException(
              requestOptions: RequestOptions(path: '/settings/thresholds'),
              type: DioExceptionType.connectionError,
              error: 'Connection error',
            ));

        // Act
        final result = await apiService.getThresholds();

        // Assert
        expect(result, null);
      });
    });

    group('getLatestImage', () {
      test('should return image data on success', () async {
        // Arrange
        final imageBytes = Uint8List.fromList([1, 2, 3, 4, 5]);

        final response = Response(
          requestOptions: RequestOptions(path: '/image/latest'),
          statusCode: 200,
          data: imageBytes,
        );

        when(mockDio.get(
          'https://example.com/api/image/latest',
          options: anyNamed('options'),
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.getLatestImage();

        // Assert
        expect(result, imageBytes);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get(
          'https://example.com/api/image/latest',
          options: anyNamed('options'),
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/image/latest'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await apiService.getLatestImage();

        // Assert
        expect(result, null);
      });
    });
  });
}
