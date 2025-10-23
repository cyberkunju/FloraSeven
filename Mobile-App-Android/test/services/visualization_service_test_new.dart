import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:flora_seven/services/visualization_service.dart';
import 'package:flora_seven/services/auth_service.dart';
import 'package:flora_seven/services/config_service.dart';

import 'visualization_service_test_new.mocks.dart';

@GenerateMocks([ConfigService, AuthService, Dio])
void main() {
  late MockConfigService mockConfigService;
  late MockAuthService mockAuthService;
  late MockDio mockDio;
  late VisualizationService visualizationService;

  setUp(() {
    mockConfigService = MockConfigService();
    mockAuthService = MockAuthService();
    mockDio = MockDio();
    
    // Configure the mock ConfigService
    when(mockConfigService.getApiUrl('/visualization/sensor/plant_node/moisture'))
        .thenReturn('https://example.com/api/visualization/sensor/plant_node/moisture');
    when(mockConfigService.getApiUrl('/visualization/health'))
        .thenReturn('https://example.com/api/visualization/health');
    when(mockConfigService.getApiUrl('/visualization/dashboard'))
        .thenReturn('https://example.com/api/visualization/dashboard');
    when(mockConfigService.getApiUrl('/visualization/data/moisture'))
        .thenReturn('https://example.com/api/visualization/data/moisture');
    when(mockConfigService.getApiUrl('/visualization/health_trend'))
        .thenReturn('https://example.com/api/visualization/health_trend');
    
    // Configure the mock AuthService
    when(mockAuthService.getAuthHeader()).thenAnswer((_) async => 'Bearer test-token');
    
    // Configure the mock Dio
    when(mockDio.options).thenReturn(BaseOptions());
    when(mockDio.interceptors).thenReturn(Interceptors());
    
    // Create the VisualizationService with mocked dependencies
    visualizationService = VisualizationService(
      configService: mockConfigService,
      authService: mockAuthService,
      dio: mockDio,
    );
  });

  group('VisualizationService', () {
    group('getSensorChart', () {
      test('should return chart data on success', () async {
        // Arrange
        final chartData = 'base64encodedchartdata';
        final response = Response(
          requestOptions: RequestOptions(path: '/visualization/sensor/plant_node/moisture'),
          statusCode: 200,
          data: {'chart_data': chartData},
        );
        
        when(mockDio.get(
          'https://example.com/api/visualization/sensor/plant_node/moisture',
          queryParameters: {'hours': 24},
        )).thenAnswer((_) async => response);

        // Act
        final result = await visualizationService.getSensorChart('plant_node', 'moisture');

        // Assert
        expect(result, chartData);
      });

      test('should return null when response does not contain chart_data', () async {
        // Arrange
        final response = Response(
          requestOptions: RequestOptions(path: '/visualization/sensor/plant_node/moisture'),
          statusCode: 200,
          data: {'status': 'ok'},
        );
        
        when(mockDio.get(
          'https://example.com/api/visualization/sensor/plant_node/moisture',
          queryParameters: {'hours': 24},
        )).thenAnswer((_) async => response);

        // Act
        final result = await visualizationService.getSensorChart('plant_node', 'moisture');

        // Assert
        expect(result, null);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get(
          'https://example.com/api/visualization/sensor/plant_node/moisture',
          queryParameters: {'hours': 24},
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/visualization/sensor/plant_node/moisture'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await visualizationService.getSensorChart('plant_node', 'moisture');

        // Assert
        expect(result, null);
      });
    });

    group('base64ToImage', () {
      test('should convert Base64 string to image bytes', () {
        // Arrange
        final base64String = 'SGVsbG8gV29ybGQ='; // "Hello World" in Base64
        final expectedBytes = Uint8List.fromList(utf8.encode('Hello World'));

        // Act
        final result = visualizationService.base64ToImage(base64String);

        // Assert
        expect(result, expectedBytes);
      });

      test('should return null for null input', () {
        // Act
        final result = visualizationService.base64ToImage(null);

        // Assert
        expect(result, null);
      });

      test('should return null for invalid Base64 string', () {
        // Arrange
        final invalidBase64 = 'not a valid base64 string';

        // Act
        final result = visualizationService.base64ToImage(invalidBase64);

        // Assert
        expect(result, null);
      });
    });
  });
}
