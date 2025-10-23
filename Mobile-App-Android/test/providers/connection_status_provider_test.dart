import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:flora_seven/domain/models/connection_status.dart';
import 'package:flora_seven/providers/connection_status_provider.dart';
import 'package:flora_seven/services/enhanced_api_service.dart';
import 'package:flora_seven/application/providers/api_service_provider.dart';

import 'connection_status_provider_test.mocks.dart';
import '../mocks/mock_api_service_adapter.dart';

@GenerateMocks([EnhancedApiService])
void main() {
  late MockEnhancedApiService mockApiService;
  late ProviderContainer container;

  setUp(() {
    mockApiService = MockEnhancedApiService();
    final mockAdapter = MockApiServiceAdapter(mockApiService);
    container = ProviderContainer(
      overrides: [
        apiServiceProvider.overrideWithValue(mockAdapter),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  test('ConnectionStatusNotifier should return mock data when API fails', () async {
    // Arrange
    when(mockApiService.getConnectionStatus()).thenAnswer((_) async => null);

    // Act
    final result = await container.read(connectionStatusProvider.future);

    // Assert
    expect(result, isA<SystemConnectionStatus>());
    expect(result.mainHub.state, DeviceConnectionState.unknown);
    expect(result.plantNode.state, DeviceConnectionState.unknown);
    expect(result.camera.state, DeviceConnectionState.unknown);
    expect(result.sensors.length, 6);
  });

  test('ConnectionStatusNotifier should return data from API when successful', () async {
    // Arrange
    final mockData = {
      'main_hub': {
        'name': 'Main Hub',
        'state': 'connected',
        'last_connected': DateTime.now().toIso8601String(),
      },
      'plant_node': {
        'name': 'Plant Node',
        'state': 'connected',
        'last_connected': DateTime.now().toIso8601String(),
      },
      'camera': {
        'name': 'Camera',
        'state': 'connected',
        'last_connected': DateTime.now().toIso8601String(),
      },
      'sensors': {
        'moisture': {
          'name': 'Moisture Sensor',
          'state': 'connected',
          'last_connected': DateTime.now().toIso8601String(),
        },
        'temperature': {
          'name': 'Temperature Sensor',
          'state': 'connected',
          'last_connected': DateTime.now().toIso8601String(),
        },
      },
    };

    when(mockApiService.getConnectionStatus()).thenAnswer((_) async => mockData);

    // Act
    final result = await container.read(connectionStatusProvider.future);

    // Assert
    expect(result, isA<SystemConnectionStatus>());
    expect(result.mainHub.state, DeviceConnectionState.connected);
    expect(result.plantNode.state, DeviceConnectionState.connected);
    expect(result.camera.state, DeviceConnectionState.connected);
    expect(result.sensors.length, 2);
    expect(result.sensors['moisture']?.state, DeviceConnectionState.connected);
    expect(result.sensors['temperature']?.state, DeviceConnectionState.connected);
  });

  test('refreshConnectionStatus should update the state', () async {
    // Arrange
    final mockData = {
      'main_hub': {
        'name': 'Main Hub',
        'state': 'connected',
        'last_connected': DateTime.now().toIso8601String(),
      },
      'plant_node': {
        'name': 'Plant Node',
        'state': 'connected',
        'last_connected': DateTime.now().toIso8601String(),
      },
      'camera': {
        'name': 'Camera',
        'state': 'connected',
        'last_connected': DateTime.now().toIso8601String(),
      },
      'sensors': {
        'moisture': {
          'name': 'Moisture Sensor',
          'state': 'connected',
          'last_connected': DateTime.now().toIso8601String(),
        },
      },
    };

    when(mockApiService.getConnectionStatus()).thenAnswer((_) async => mockData);

    // Initial state
    await container.read(connectionStatusProvider.future);

    // Update the mock to return different data
    final updatedMockData = {
      'main_hub': {
        'name': 'Main Hub',
        'state': 'degraded',
        'last_connected': DateTime.now().toIso8601String(),
        'message': 'Intermittent connection',
      },
      'plant_node': {
        'name': 'Plant Node',
        'state': 'connected',
        'last_connected': DateTime.now().toIso8601String(),
      },
      'camera': {
        'name': 'Camera',
        'state': 'disconnected',
        'last_connected': DateTime.now().toIso8601String(),
        'message': 'Not responding',
      },
      'sensors': {
        'moisture': {
          'name': 'Moisture Sensor',
          'state': 'connected',
          'last_connected': DateTime.now().toIso8601String(),
        },
      },
    };

    when(mockApiService.getConnectionStatus()).thenAnswer((_) async => updatedMockData);

    // Act
    await container.read(connectionStatusProvider.notifier).refreshConnectionStatus();
    final result = container.read(connectionStatusProvider).value;

    // Assert
    expect(result, isA<SystemConnectionStatus>());
    expect(result?.mainHub.state, DeviceConnectionState.degraded);
    expect(result?.mainHub.message, 'Intermittent connection');
    expect(result?.plantNode.state, DeviceConnectionState.connected);
    expect(result?.camera.state, DeviceConnectionState.disconnected);
    expect(result?.camera.message, 'Not responding');
    expect(result?.sensors.length, 1);
    expect(result?.sensors['moisture']?.state, DeviceConnectionState.connected);
  });
}
