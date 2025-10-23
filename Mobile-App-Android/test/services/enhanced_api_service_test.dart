import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:flora_seven/services/enhanced_api_service.dart';
import 'package:flora_seven/services/auth_service.dart';
import 'package:flora_seven/services/config_service.dart';
import 'package:flora_seven/domain/models/plant_data.dart';
import 'package:flora_seven/domain/models/thresholds.dart';

import 'enhanced_api_service_test.mocks.dart';

// Generate mocks for the dependencies
@GenerateMocks([ConfigService, AuthService, Dio, HttpClientAdapter])
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
    when(mockConfigService.getApiUrl(any)).thenAnswer(
      (invocation) => 'https://example.com/api${invocation.positionalArguments[0]}'
    );
    when(mockConfigService.getServerUrl()).thenReturn('https://example.com');
    
    // Configure the mock AuthService
    when(mockAuthService.getAuthHeader()).thenAnswer((_) async => 'Bearer test-token');
    
    // Create the EnhancedApiService with mocked dependencies
    apiService = EnhancedApiService(
      configService: mockConfigService,
      authService: mockAuthService,
      dio: mockDio,
    );
    
    // Configure the mock Dio
    when(mockDio.options).thenReturn(BaseOptions());
    when(mockDio.interceptors).thenReturn(Interceptors());
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
        verify(mockDio.get(
          'https://example.com/api/status',
          options: anyNamed('options'),
        )).called(1);
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
        verify(mockDio.get(
          'https://example.com/api/status',
          options: anyNamed('options'),
        )).called(1);
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
        verify(mockDio.get(
          'https://example.com/api/status',
          options: anyNamed('options'),
        )).called(1);
      });
    });

    group('getStatus', () {
      test('should return status data on success', () async {
        // Arrange
        final statusData = {
          'status': 'ok',
          'version': '1.0.0',
          'connected_hardware': ['plant_node', 'hub_node'],
          'last_seen': {'plant_node': '2025-04-15T10:30:00Z', 'hub_node': '2025-04-15T10:30:00Z'},
        };
        
        final response = Response(
          requestOptions: RequestOptions(path: '/status'),
          statusCode: 200,
          data: statusData,
        );
        
        when(mockDio.get('https://example.com/api/status'))
            .thenAnswer((_) async => response);

        // Act
        final result = await apiService.getStatus();

        // Assert
        expect(result, statusData);
        verify(mockDio.get('https://example.com/api/status')).called(1);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get('https://example.com/api/status'))
            .thenThrow(DioException(
              requestOptions: RequestOptions(path: '/status'),
              type: DioExceptionType.connectionError,
              error: 'Connection error',
            ));

        // Act
        final result = await apiService.getStatus();

        // Assert
        expect(result, null);
        verify(mockDio.get('https://example.com/api/status')).called(1);
      });
    });

    group('getPlantData', () {
      test('should return PlantData on success', () async {
        // Arrange
        final plantDataJson = {
          'timestamp': '2025-04-15T10:30:00Z',
          'plant_node': {
            'moisture': 65.5,
            'temperature_soil': 24.8,
            'light_lux': 15000,
            'uv_index_plant': 1.2,
            'ec_conductivity': 1.8
          },
          'hub_node': {
            'ph_water_tank': 6.5,
            'uv_index_ambient': 1.1
          },
          'health': {
            'condition_index': {
              'moisture': 'Optimal',
              'temperature_soil': 'Optimal',
              'light_lux': 'WarningLow',
              'uv_index_plant': 'Optimal',
              'ec_conductivity': 'WarningHigh',
              'ph_water_tank': 'Optimal'
            },
            'visual_health': {
              'score': 85,
              'label': 'Appears Healthy',
              'last_check_timestamp': '2025-04-15T10:25:00Z'
            },
            'overall_status': 'Good',
            'suggestions': ['Consider checking nutrient levels.']
          },
          'latest_image': {
            'url': '/api/v1/image/latest',
            'timestamp': '2025-04-15T10:25:00Z'
          },
          'pump_status': {
            'is_active': false,
            'last_watered_timestamp': '2025-04-15T08:00:00Z'
          },
          'power': {
            'plant_node_voltage': 4.1,
            'hub_node_voltage': 4.0
          },
          'auto_watering_enabled': true
        };
        
        final response = Response(
          requestOptions: RequestOptions(path: '/status'),
          statusCode: 200,
          data: plantDataJson,
        );
        
        when(mockDio.get('https://example.com/api/status'))
            .thenAnswer((_) async => response);

        // Act
        final result = await apiService.getPlantData();

        // Assert
        expect(result, isA<PlantData>());
        expect(result?.plantNode.moisture, 65.5);
        expect(result?.plantNode.temperatureSoil, 24.8);
        expect(result?.hubNode.phWaterTank, 6.5);
        verify(mockDio.get('https://example.com/api/status')).called(1);
      });

      test('should return null when response does not contain expected data', () async {
        // Arrange
        final invalidData = {
          'status': 'ok',
          'version': '1.0.0',
          // Missing plant_node and hub_node
        };
        
        final response = Response(
          requestOptions: RequestOptions(path: '/status'),
          statusCode: 200,
          data: invalidData,
        );
        
        when(mockDio.get('https://example.com/api/status'))
            .thenAnswer((_) async => response);

        // Act
        final result = await apiService.getPlantData();

        // Assert
        expect(result, null);
        verify(mockDio.get('https://example.com/api/status')).called(1);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get('https://example.com/api/status'))
            .thenThrow(DioException(
              requestOptions: RequestOptions(path: '/status'),
              type: DioExceptionType.connectionError,
              error: 'Connection error',
            ));

        // Act
        final result = await apiService.getPlantData();

        // Assert
        expect(result, null);
        verify(mockDio.get('https://example.com/api/status')).called(1);
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
        verify(mockDio.get(
          'https://example.com/api/image/latest',
          options: anyNamed('options'),
        )).called(1);
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
        verify(mockDio.get(
          'https://example.com/api/image/latest',
          options: anyNamed('options'),
        )).called(1);
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
        verify(mockDio.get('https://example.com/api/settings/thresholds')).called(1);
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
        verify(mockDio.get('https://example.com/api/settings/thresholds')).called(1);
      });
    });

    group('updateThresholds', () {
      test('should return true on success', () async {
        // Arrange
        final thresholds = Thresholds(
          moistureLow: 40,
          moistureHigh: 70,
          temperatureLow: 18.0,
          temperatureHigh: 28.0,
          lightIntensityLow: 5000.0,
          lightIntensityHigh: 20000.0,
          ecLow: 800.0,
          ecHigh: 1500.0,
          phLow: 5.8,
          phHigh: 6.8,
          uvIndexLow: 0.0,
          uvIndexHigh: 5.0,
        );
        
        final response = Response(
          requestOptions: RequestOptions(path: '/settings/thresholds'),
          statusCode: 200,
          data: {'success': true},
        );
        
        when(mockDio.post(
          'https://example.com/api/settings/thresholds',
          data: thresholds.toJson(),
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.updateThresholds(thresholds);

        // Assert
        expect(result, true);
        verify(mockDio.post(
          'https://example.com/api/settings/thresholds',
          data: thresholds.toJson(),
        )).called(1);
      });

      test('should return false on error', () async {
        // Arrange
        final thresholds = Thresholds(
          moistureLow: 40,
          moistureHigh: 70,
          temperatureLow: 18.0,
          temperatureHigh: 28.0,
          lightIntensityLow: 5000.0,
          lightIntensityHigh: 20000.0,
          ecLow: 800.0,
          ecHigh: 1500.0,
          phLow: 5.8,
          phHigh: 6.8,
          uvIndexLow: 0.0,
          uvIndexHigh: 5.0,
        );
        
        when(mockDio.post(
          'https://example.com/api/settings/thresholds',
          data: thresholds.toJson(),
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/settings/thresholds'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await apiService.updateThresholds(thresholds);

        // Assert
        expect(result, false);
        verify(mockDio.post(
          'https://example.com/api/settings/thresholds',
          data: thresholds.toJson(),
        )).called(1);
      });
    });

    group('sendWaterCommand', () {
      test('should return true on success', () async {
        // Arrange
        final response = Response(
          requestOptions: RequestOptions(path: '/command/water'),
          statusCode: 200,
          data: {'success': true},
        );
        
        when(mockDio.post(
          'https://example.com/api/command/water',
          data: {
            'state': 'ON',
            'duration_sec': 10,
          },
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.sendWaterCommand(state: true, durationSec: 10);

        // Assert
        expect(result, true);
        verify(mockDio.post(
          'https://example.com/api/command/water',
          data: {
            'state': 'ON',
            'duration_sec': 10,
          },
        )).called(1);
      });

      test('should return false when server returns error', () async {
        // Arrange
        final response = Response(
          requestOptions: RequestOptions(path: '/command/water'),
          statusCode: 200,
          data: {'success': false, 'message': 'Pump already active'},
        );
        
        when(mockDio.post(
          'https://example.com/api/command/water',
          data: {
            'state': 'ON',
            'duration_sec': 10,
          },
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.sendWaterCommand(state: true, durationSec: 10);

        // Assert
        expect(result, false);
        verify(mockDio.post(
          'https://example.com/api/command/water',
          data: {
            'state': 'ON',
            'duration_sec': 10,
          },
        )).called(1);
      });

      test('should return false on error', () async {
        // Arrange
        when(mockDio.post(
          'https://example.com/api/command/water',
          data: {
            'state': 'ON',
            'duration_sec': 10,
          },
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/command/water'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await apiService.sendWaterCommand(state: true, durationSec: 10);

        // Assert
        expect(result, false);
        verify(mockDio.post(
          'https://example.com/api/command/water',
          data: {
            'state': 'ON',
            'duration_sec': 10,
          },
        )).called(1);
      });
    });

    group('toggleAutoWatering', () {
      test('should return true on success', () async {
        // Arrange
        final response = Response(
          requestOptions: RequestOptions(path: '/settings/auto_watering'),
          statusCode: 200,
          data: {'success': true},
        );
        
        when(mockDio.post(
          'https://example.com/api/settings/auto_watering',
          data: {'enabled': true},
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.toggleAutoWatering(true);

        // Assert
        expect(result, true);
        verify(mockDio.post(
          'https://example.com/api/settings/auto_watering',
          data: {'enabled': true},
        )).called(1);
      });

      test('should return false when server returns error', () async {
        // Arrange
        final response = Response(
          requestOptions: RequestOptions(path: '/settings/auto_watering'),
          statusCode: 200,
          data: {'success': false, 'message': 'Invalid state'},
        );
        
        when(mockDio.post(
          'https://example.com/api/settings/auto_watering',
          data: {'enabled': true},
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.toggleAutoWatering(true);

        // Assert
        expect(result, false);
        verify(mockDio.post(
          'https://example.com/api/settings/auto_watering',
          data: {'enabled': true},
        )).called(1);
      });

      test('should return false on error', () async {
        // Arrange
        when(mockDio.post(
          'https://example.com/api/settings/auto_watering',
          data: {'enabled': true},
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/settings/auto_watering'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await apiService.toggleAutoWatering(true);

        // Assert
        expect(result, false);
        verify(mockDio.post(
          'https://example.com/api/settings/auto_watering',
          data: {'enabled': true},
        )).called(1);
      });
    });

    group('getHistoricalData', () {
      test('should return historical data on success', () async {
        // Arrange
        final historicalData = [
          {
            'timestamp': '2025-04-15T10:00:00Z',
            'moisture': 65.5,
            'temperature': 24.8,
            'light': 15000,
          },
          {
            'timestamp': '2025-04-15T09:00:00Z',
            'moisture': 64.2,
            'temperature': 24.5,
            'light': 14500,
          },
        ];
        
        final response = Response(
          requestOptions: RequestOptions(path: '/data/history'),
          statusCode: 200,
          data: historicalData,
        );
        
        when(mockDio.get(
          'https://example.com/api/data/history',
          queryParameters: {
            'start_time': '2025-04-15T00:00:00Z',
            'end_time': '2025-04-15T23:59:59Z',
            'sensor_type': 'moisture',
          },
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.getHistoricalData(
          startTime: '2025-04-15T00:00:00Z',
          endTime: '2025-04-15T23:59:59Z',
          sensorType: 'moisture',
        );

        // Assert
        expect(result, historicalData);
        verify(mockDio.get(
          'https://example.com/api/data/history',
          queryParameters: {
            'start_time': '2025-04-15T00:00:00Z',
            'end_time': '2025-04-15T23:59:59Z',
            'sensor_type': 'moisture',
          },
        )).called(1);
      });

      test('should return empty list when response is not a list', () async {
        // Arrange
        final invalidData = {'error': 'Invalid format'};
        
        final response = Response(
          requestOptions: RequestOptions(path: '/data/history'),
          statusCode: 200,
          data: invalidData,
        );
        
        when(mockDio.get(
          'https://example.com/api/data/history',
          queryParameters: {
            'start_time': '2025-04-15T00:00:00Z',
            'end_time': '2025-04-15T23:59:59Z',
          },
        )).thenAnswer((_) async => response);

        // Act
        final result = await apiService.getHistoricalData(
          startTime: '2025-04-15T00:00:00Z',
          endTime: '2025-04-15T23:59:59Z',
        );

        // Assert
        expect(result, []);
        verify(mockDio.get(
          'https://example.com/api/data/history',
          queryParameters: {
            'start_time': '2025-04-15T00:00:00Z',
            'end_time': '2025-04-15T23:59:59Z',
          },
        )).called(1);
      });

      test('should return null on error', () async {
        // Arrange
        when(mockDio.get(
          'https://example.com/api/data/history',
          queryParameters: {
            'start_time': '2025-04-15T00:00:00Z',
            'end_time': '2025-04-15T23:59:59Z',
          },
        )).thenThrow(DioException(
          requestOptions: RequestOptions(path: '/data/history'),
          type: DioExceptionType.connectionError,
          error: 'Connection error',
        ));

        // Act
        final result = await apiService.getHistoricalData(
          startTime: '2025-04-15T00:00:00Z',
          endTime: '2025-04-15T23:59:59Z',
        );

        // Assert
        expect(result, null);
        verify(mockDio.get(
          'https://example.com/api/data/history',
          queryParameters: {
            'start_time': '2025-04-15T00:00:00Z',
            'end_time': '2025-04-15T23:59:59Z',
          },
        )).called(1);
      });
    });
  });
}
