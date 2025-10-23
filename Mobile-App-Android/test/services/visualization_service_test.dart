import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:flora_seven/services/visualization_service.dart';
import 'package:flora_seven/services/auth_service.dart';
import 'package:flora_seven/services/config_service.dart';

import 'visualization_service_test.mocks.dart';

// Generate mocks for the dependencies
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
    when(mockConfigService.getApiUrl(any)).thenAnswer(
      (invocation) => 'https://example.com/api${invocation.positionalArguments[0]}'
    );
    
    // Configure the mock AuthService
    when(mockAuthService.getAuthHeader()).thenAnswer((_) async => 'Bearer test-token');
    
    // Create the VisualizationService with mocked dependencies
    visualizationService = VisualizationService(
      configService: mockConfigService,
      authService: mockAuthService,
      dio: mockDio,
    );
    
    // Configure the mock Dio
    when(mockDio.options).thenReturn(BaseOptions());
    when(mockDio.interceptors).thenReturn(Interceptors());
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
        verify(mockDio.get(
          'https://example.com/api/visualization/sensor/plant_node/moisture',
          queryParameters: {'hours': 24},
        )).called(1);
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
        verify(mockDio.get(
          'https://example.com/api/visualization/sensor/plant_node/moisture',
          queryParameters: {'hours': 24},
        )).called(1);
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
        verify(mockDio.get(
          'https://example.com/api/visualization/sensor/plant_node/moisture',
          queryParameters: {'hours': 24},
        )).called(1);
      });
    });

    group('getHealthChart', () {
      test('should return health chart data on success', () async {
        // Arrange
        final chartData = 'base64encodedchartdata';
        final response = Response(
          requestOptions: RequestOptions(path: '/visualization/health'),
          statusCode: 200,
          data: {'chart_data': chartData},
        );
        
        when(mockDio.get(
          'https://example.com/api/visualization/health',
          queryParameters: {'days': 7},
        )).thenAnswer((_) async => response);

        // Act
        final result = await visualizationService.getHealthChart();

        // Assert
        expect(result, chartData);
        verify(mockDio.get(
          'https://example.com/api/visualization/health',
          queryParameters: {'days': 7},
        )).called(1);
      });

      test('should return null when response does not contain chart_data', () async {
        // Arrange
        final response = Response(
          requestOptions: RequestOptions(path: '/visualization/health'),
          statusCode: 200,
          data: {'status': 'ok'},
        );
        
        when(mockDio.get(
          'https://example.com/api/visualization/health',
          queryParameters: {'days': 7},
        )).thenAnswer((_) async => response);

        // Act
        final result = await visualizationService.getHealthChart();

        // Assert
        expect(result, null);
        verify(mockDio.get(
          'https://example.com/api/visualization/health',
          queryParameters: {'days': 7},
        )).called(1);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get(
          'https://example.com/api/visualization/health',
          queryParameters: {'days': 7},
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/visualization/health'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await visualizationService.getHealthChart();

        // Assert
        expect(result, null);
        verify(mockDio.get(
          'https://example.com/api/visualization/health',
          queryParameters: {'days': 7},
        )).called(1);
      });
    });

    group('getDashboard', () {
      test('should return dashboard data on success', () async {
        // Arrange
        final dashboardData = {
          'moisture': 'base64encodedchartdata1',
          'temperature': 'base64encodedchartdata2',
          'light': 'base64encodedchartdata3',
        };
        
        final response = Response(
          requestOptions: RequestOptions(path: '/visualization/dashboard'),
          statusCode: 200,
          data: {'dashboard': dashboardData},
        );
        
        when(mockDio.get('https://example.com/api/visualization/dashboard'))
            .thenAnswer((_) async => response);

        // Act
        final result = await visualizationService.getDashboard();

        // Assert
        expect(result, dashboardData);
        verify(mockDio.get('https://example.com/api/visualization/dashboard')).called(1);
      });

      test('should return null when response does not contain dashboard data', () async {
        // Arrange
        final response = Response(
          requestOptions: RequestOptions(path: '/visualization/dashboard'),
          statusCode: 200,
          data: {'status': 'ok'},
        );
        
        when(mockDio.get('https://example.com/api/visualization/dashboard'))
            .thenAnswer((_) async => response);

        // Act
        final result = await visualizationService.getDashboard();

        // Assert
        expect(result, null);
        verify(mockDio.get('https://example.com/api/visualization/dashboard')).called(1);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get('https://example.com/api/visualization/dashboard'))
            .thenThrow(DioException(
              requestOptions: RequestOptions(path: '/visualization/dashboard'),
              type: DioExceptionType.connectionError,
              error: 'Connection error',
            ));

        // Act
        final result = await visualizationService.getDashboard();

        // Assert
        expect(result, null);
        verify(mockDio.get('https://example.com/api/visualization/dashboard')).called(1);
      });
    });

    group('getSensorData', () {
      test('should return sensor data on success', () async {
        // Arrange
        final sensorData = {
          'timestamps': ['2025-04-15T10:00:00Z', '2025-04-15T11:00:00Z'],
          'values': [65.5, 66.2],
          'unit': '%',
          'min': 65.5,
          'max': 66.2,
          'avg': 65.85,
        };
        
        final response = Response(
          requestOptions: RequestOptions(path: '/visualization/data/moisture'),
          statusCode: 200,
          data: sensorData,
        );
        
        when(mockDio.get(
          'https://example.com/api/visualization/data/moisture',
          queryParameters: {'time_range': 'day'},
        )).thenAnswer((_) async => response);

        // Act
        final result = await visualizationService.getSensorData('moisture');

        // Assert
        expect(result, sensorData);
        verify(mockDio.get(
          'https://example.com/api/visualization/data/moisture',
          queryParameters: {'time_range': 'day'},
        )).called(1);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get(
          'https://example.com/api/visualization/data/moisture',
          queryParameters: {'time_range': 'day'},
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/visualization/data/moisture'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await visualizationService.getSensorData('moisture');

        // Assert
        expect(result, null);
        verify(mockDio.get(
          'https://example.com/api/visualization/data/moisture',
          queryParameters: {'time_range': 'day'},
        )).called(1);
      });
    });

    group('getHealthTrend', () {
      test('should return health trend data on success', () async {
        // Arrange
        final healthTrendData = {
          'timestamps': ['2025-04-15T10:00:00Z', '2025-04-16T10:00:00Z'],
          'scores': [85, 87],
          'labels': ['Appears Healthy', 'Appears Healthy'],
        };
        
        final response = Response(
          requestOptions: RequestOptions(path: '/visualization/health_trend'),
          statusCode: 200,
          data: healthTrendData,
        );
        
        when(mockDio.get(
          'https://example.com/api/visualization/health_trend',
          queryParameters: {'time_range': 'week'},
        )).thenAnswer((_) async => response);

        // Act
        final result = await visualizationService.getHealthTrend();

        // Assert
        expect(result, healthTrendData);
        verify(mockDio.get(
          'https://example.com/api/visualization/health_trend',
          queryParameters: {'time_range': 'week'},
        )).called(1);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get(
          'https://example.com/api/visualization/health_trend',
          queryParameters: {'time_range': 'week'},
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/visualization/health_trend'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await visualizationService.getHealthTrend();

        // Assert
        expect(result, null);
        verify(mockDio.get(
          'https://example.com/api/visualization/health_trend',
          queryParameters: {'time_range': 'week'},
        )).called(1);
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
