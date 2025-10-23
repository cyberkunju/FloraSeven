import 'package:flutter_test/flutter_test.dart';
import 'package:flora_seven/domain/models/connection_status.dart';

void main() {
  group('ConnectionStatus', () {
    test('should create a ConnectionStatus from JSON', () {
      final json = {
        'name': 'Test Sensor',
        'state': 'connected',
        'last_connected': '2023-01-01T12:00:00.000Z',
        'message': 'Test message',
      };

      final status = ConnectionStatus.fromJson(json);

      expect(status.name, 'Test Sensor');
      expect(status.state, DeviceConnectionState.connected);
      expect(status.lastConnected, DateTime.parse('2023-01-01T12:00:00.000Z'));
      expect(status.message, 'Test message');
    });

    test('should convert a ConnectionStatus to JSON', () {
      final status = ConnectionStatus(
        name: 'Test Sensor',
        state: DeviceConnectionState.connected,
        lastConnected: DateTime.parse('2023-01-01T12:00:00.000Z'),
        message: 'Test message',
      );

      final json = status.toJson();

      expect(json['name'], 'Test Sensor');
      expect(json['state'], 'connected');
      expect(json['last_connected'], '2023-01-01T12:00:00.000Z');
      expect(json['message'], 'Test message');
    });

    test('should create a copy with updated values', () {
      final status = ConnectionStatus(
        name: 'Test Sensor',
        state: DeviceConnectionState.connected,
        lastConnected: DateTime.parse('2023-01-01T12:00:00.000Z'),
        message: 'Test message',
      );

      final updatedStatus = status.copyWith(
        state: DeviceConnectionState.disconnected,
        message: 'Updated message',
      );

      expect(updatedStatus.name, 'Test Sensor');
      expect(updatedStatus.state, DeviceConnectionState.disconnected);
      expect(updatedStatus.lastConnected, DateTime.parse('2023-01-01T12:00:00.000Z'));
      expect(updatedStatus.message, 'Updated message');
    });
  });

  group('SystemConnectionStatus', () {
    test('should create a SystemConnectionStatus from JSON', () {
      final json = {
        'main_hub': {
          'name': 'Main Hub',
          'state': 'connected',
          'last_connected': '2023-01-01T12:00:00.000Z',
        },
        'plant_node': {
          'name': 'Plant Node',
          'state': 'degraded',
          'last_connected': '2023-01-01T11:00:00.000Z',
          'message': 'Intermittent connection',
        },
        'camera': {
          'name': 'Camera',
          'state': 'disconnected',
          'last_connected': '2023-01-01T10:00:00.000Z',
          'message': 'Not responding',
        },
        'sensors': {
          'moisture': {
            'name': 'Moisture Sensor',
            'state': 'connected',
            'last_connected': '2023-01-01T12:00:00.000Z',
          },
          'temperature': {
            'name': 'Temperature Sensor',
            'state': 'disconnected',
            'last_connected': '2023-01-01T10:00:00.000Z',
            'message': 'Sensor not responding',
          },
        },
      };

      final status = SystemConnectionStatus.fromJson(json);

      expect(status.mainHub.name, 'Main Hub');
      expect(status.mainHub.state, DeviceConnectionState.connected);

      expect(status.plantNode.name, 'Plant Node');
      expect(status.plantNode.state, DeviceConnectionState.degraded);
      expect(status.plantNode.message, 'Intermittent connection');

      expect(status.camera.name, 'Camera');
      expect(status.camera.state, DeviceConnectionState.disconnected);

      expect(status.sensors.length, 2);
      expect(status.sensors['moisture']?.name, 'Moisture Sensor');
      expect(status.sensors['moisture']?.state, DeviceConnectionState.connected);

      expect(status.sensors['temperature']?.name, 'Temperature Sensor');
      expect(status.sensors['temperature']?.state, DeviceConnectionState.disconnected);
      expect(status.sensors['temperature']?.message, 'Sensor not responding');
    });

    test('should convert a SystemConnectionStatus to JSON', () {
      final now = DateTime.now();

      final status = SystemConnectionStatus(
        mainHub: ConnectionStatus(
          name: 'Main Hub',
          state: DeviceConnectionState.connected,
          lastConnected: now,
        ),
        plantNode: ConnectionStatus(
          name: 'Plant Node',
          state: DeviceConnectionState.degraded,
          lastConnected: now,
          message: 'Intermittent connection',
        ),
        camera: ConnectionStatus(
          name: 'Camera',
          state: DeviceConnectionState.disconnected,
          lastConnected: now,
          message: 'Not responding',
        ),
        sensors: {
          'moisture': ConnectionStatus(
            name: 'Moisture Sensor',
            state: DeviceConnectionState.connected,
            lastConnected: now,
          ),
          'temperature': ConnectionStatus(
            name: 'Temperature Sensor',
            state: DeviceConnectionState.disconnected,
            lastConnected: now,
            message: 'Sensor not responding',
          ),
        },
      );

      final json = status.toJson();

      expect(json['main_hub']['name'], 'Main Hub');
      expect(json['main_hub']['state'], 'connected');

      expect(json['plant_node']['name'], 'Plant Node');
      expect(json['plant_node']['state'], 'degraded');
      expect(json['plant_node']['message'], 'Intermittent connection');

      expect(json['camera']['name'], 'Camera');
      expect(json['camera']['state'], 'disconnected');

      expect(json['sensors']['moisture']['name'], 'Moisture Sensor');
      expect(json['sensors']['moisture']['state'], 'connected');

      expect(json['sensors']['temperature']['name'], 'Temperature Sensor');
      expect(json['sensors']['temperature']['state'], 'disconnected');
      expect(json['sensors']['temperature']['message'], 'Sensor not responding');
    });

    test('should create an unknown SystemConnectionStatus', () {
      final status = SystemConnectionStatus.unknown();

      expect(status.mainHub.state, DeviceConnectionState.unknown);
      expect(status.plantNode.state, DeviceConnectionState.unknown);
      expect(status.camera.state, DeviceConnectionState.unknown);

      expect(status.sensors.length, 6);
      expect(status.sensors['moisture']?.state, DeviceConnectionState.unknown);
      expect(status.sensors['temperature']?.state, DeviceConnectionState.unknown);
      expect(status.sensors['light']?.state, DeviceConnectionState.unknown);
      expect(status.sensors['ec']?.state, DeviceConnectionState.unknown);
      expect(status.sensors['ph']?.state, DeviceConnectionState.unknown);
      expect(status.sensors['uv']?.state, DeviceConnectionState.unknown);
    });

    test('should create a mock SystemConnectionStatus', () {
      final status = SystemConnectionStatus.mock();

      expect(status.mainHub.state, DeviceConnectionState.connected);
      expect(status.plantNode.state, DeviceConnectionState.connected);
      expect(status.camera.state, DeviceConnectionState.connected);

      expect(status.sensors.length, 6);
      expect(status.sensors['moisture']?.state, DeviceConnectionState.connected);
      expect(status.sensors['temperature']?.state, DeviceConnectionState.connected);
      expect(status.sensors['light']?.state, DeviceConnectionState.connected);
      expect(status.sensors['ec']?.state, DeviceConnectionState.degraded);
      expect(status.sensors['ph']?.state, DeviceConnectionState.disconnected);
      expect(status.sensors['uv']?.state, DeviceConnectionState.connected);
    });
  });
}
