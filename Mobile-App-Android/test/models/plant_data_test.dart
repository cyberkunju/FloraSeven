import 'package:flutter_test/flutter_test.dart';
import 'package:flora_seven/domain/models/plant_data.dart';
import 'package:flora_seven/domain/models/plant_node_data.dart';
import 'package:flora_seven/domain/models/hub_node_data.dart';
import 'package:flora_seven/domain/models/health_status.dart';
import 'package:flora_seven/domain/models/condition_index.dart';
import 'package:flora_seven/domain/models/visual_health.dart';
import 'package:flora_seven/domain/models/latest_image.dart';
import 'package:flora_seven/domain/models/pump_status.dart';
import 'package:flora_seven/domain/models/power_status.dart';
import 'package:flora_seven/domain/models/sensor_reading.dart';

void main() {
  group('PlantData', () {
    test('should parse from JSON correctly', () {
      // Arrange
      final json = {
        'timestamp': '2025-04-15T10:30:00Z',
        'plantNode': {
          'moisture': 65.5,
          'temperature_soil': 24.8,
          'light_lux': 15000,
          'uv_index_plant': 1.2,
          'ec_conductivity': 1.8
        },
        'hubNode': {
          'ph_water_tank': 6.5,
          'uv_index_ambient': 1.1
        },
        'health': {
          'conditionIndex': {
            'moisture': 'Optimal',
            'temperature_soil': 'Optimal',
            'light_lux': 'WarningLow',
            'uv_index_plant': 'Optimal',
            'ec_conductivity': 'WarningHigh',
            'ph_water_tank': 'Optimal'
          },
          'visualHealth': {
            'score': 85,
            'label': 'Appears Healthy',
            'lastCheckTimestamp': '2025-04-15T10:25:00Z'
          },
          'overallStatus': 'Good',
          'suggestions': ['Consider checking nutrient levels.']
        },
        'latestImage': {
          'url': '/api/v1/image/latest',
          'timestamp': '2025-04-15T10:25:00Z'
        },
        'pumpStatus': {
          'isActive': false,
          'lastWateredTimestamp': '2025-04-15T08:00:00Z'
        },
        'power': {
          'plantNodeVoltage': 4.1,
          'hubNodeVoltage': 4.0
        },
        'autoWateringEnabled': true
      };

      // Act
      final plantData = PlantData.fromJson(json);

      // Assert
      expect(plantData.timestamp, DateTime.parse('2025-04-15T10:30:00Z'));
      expect(plantData.plantNode.moisture, 65.5);
      expect(plantData.plantNode.temperatureSoil, 24.8);
      expect(plantData.plantNode.lightLux, 15000);
      expect(plantData.plantNode.uvIndexPlant, 1.2);
      expect(plantData.plantNode.ecConductivity, 1.8);

      expect(plantData.hubNode.phWaterTank, 6.5);
      expect(plantData.hubNode.uvIndexAmbient, 1.1);

      expect(plantData.health.conditionIndex.moisture, 'Optimal');
      expect(plantData.health.conditionIndex.temperatureSoil, 'Optimal');
      expect(plantData.health.conditionIndex.lightLux, 'WarningLow');
      expect(plantData.health.conditionIndex.ecConductivity, 'WarningHigh');
      expect(plantData.health.conditionIndex.phWaterTank, 'Optimal');

      expect(plantData.health.visualHealth.score, 85);
      expect(plantData.health.visualHealth.label, 'Appears Healthy');
      expect(plantData.health.visualHealth.lastCheckTimestamp, DateTime.parse('2025-04-15T10:25:00Z'));

      expect(plantData.health.overallStatus, 'Good');
      expect(plantData.health.suggestions, ['Consider checking nutrient levels.']);

      expect(plantData.latestImage.url, '/api/v1/image/latest');
      expect(plantData.latestImage.timestamp, DateTime.parse('2025-04-15T10:25:00Z'));

      expect(plantData.pumpStatus.isActive, false);
      expect(plantData.pumpStatus.lastWateredTimestamp, DateTime.parse('2025-04-15T08:00:00Z'));

      expect(plantData.power?.plantNodeVoltage, 4.1);
      expect(plantData.power?.hubNodeVoltage, 4.0);

      expect(plantData.autoWateringEnabled, true);
    });

    test('should convert to JSON correctly', () {
      // Arrange
      final plantData = PlantData(
        timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
        plantNode: PlantNodeData(
          moisture: SensorReading(
            value: 65.5,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: '%',
          ),
          temperature: SensorReading(
            value: 24.8,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: '°C',
          ),
          light: SensorReading(
            value: 15000,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'lux',
          ),
          uvIndexPlant: SensorReading(
            value: 1.2,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'UV index',
          ),
          ec: SensorReading(
            value: 1.8,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'μS/cm',
          ),
        ),
        hubNode: HubNodeData(
          ph: SensorReading(
            value: 6.5,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'pH',
          ),
          uv: SensorReading(
            value: 1.1,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'UV index',
          ),
        ),
        health: HealthStatus(
          conditionIndex: ConditionIndex(
            moisture: 'Optimal',
            temperatureSoil: 'Optimal',
            lightLux: 'WarningLow',
            uvIndexPlant: 'Optimal',
            ecConductivity: 'WarningHigh',
            phWaterTank: 'Optimal',
          ),
          visualHealth: VisualHealth(
            score: 85,
            label: 'Appears Healthy',
            lastCheckTimestamp: DateTime.parse('2025-04-15T10:25:00Z'),
          ),
          overallStatus: 'Good',
          suggestions: ['Consider checking nutrient levels.'],
        ),
        latestImage: LatestImage(
          url: '/api/v1/image/latest',
          timestamp: DateTime.parse('2025-04-15T10:25:00Z'),
        ),
        pumpStatus: PumpStatus(
          isActive: false,
          lastWateredTimestamp: DateTime.parse('2025-04-15T08:00:00Z'),
          isRunning: false,
          startTime: DateTime.parse('2025-04-15T08:00:00Z'),
          duration: 0,
          remainingTime: 0,
        ),
        power: PowerStatus(
          plantNodeVoltage: 4.1,
          hubNodeVoltage: 4.0,
        ),
        autoWateringEnabled: true,
      );

      // Act
      final json = plantData.toJson();

      // Assert
      expect(json['timestamp'], '2025-04-15T10:30:00.000Z');
      expect(json['plantNode']['moisture'], 65.5);
      expect(json['plantNode']['temperature_soil'], 24.8);
      expect(json['plantNode']['light_lux'], 15000);
      expect(json['plantNode']['uv_index_plant'], 1.2);
      expect(json['plantNode']['ec_conductivity'], 1.8);

      expect(json['hubNode']['ph_water_tank'], 6.5);
      expect(json['hubNode']['uv_index_ambient'], 1.1);

      expect(json['health']['conditionIndex']['moisture'], 'Optimal');
      expect(json['health']['conditionIndex']['temperature_soil'], 'Optimal');
      expect(json['health']['conditionIndex']['light_lux'], 'WarningLow');
      expect(json['health']['conditionIndex']['ec_conductivity'], 'WarningHigh');
      expect(json['health']['conditionIndex']['ph_water_tank'], 'Optimal');

      expect(json['health']['visualHealth']['score'], 85);
      expect(json['health']['visualHealth']['label'], 'Appears Healthy');
      expect(json['health']['visualHealth']['lastCheckTimestamp'], '2025-04-15T10:25:00.000Z');

      expect(json['health']['overallStatus'], 'Good');
      expect(json['health']['suggestions'], ['Consider checking nutrient levels.']);

      expect(json['latestImage']['url'], '/api/v1/image/latest');
      expect(json['latestImage']['timestamp'], '2025-04-15T10:25:00.000Z');

      expect(json['pumpStatus']['isActive'], false);
      expect(json['pumpStatus']['lastWateredTimestamp'], '2025-04-15T08:00:00.000Z');

      expect(json['power']['plantNodeVoltage'], 4.1);
      expect(json['power']['hubNodeVoltage'], 4.0);

      expect(json['autoWateringEnabled'], true);
    });

    test('helper methods should work correctly', () {
      // Arrange
      final plantData = PlantData(
        timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
        plantNode: PlantNodeData(
          moisture: SensorReading(
            value: 65.5,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: '%',
          ),
          temperature: SensorReading(
            value: 24.8,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: '°C',
          ),
          light: SensorReading(
            value: 15000,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'lux',
          ),
          uvIndexPlant: SensorReading(
            value: 1.2,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'UV index',
          ),
          ec: SensorReading(
            value: 1.8,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'μS/cm',
          ),
        ),
        hubNode: HubNodeData(
          ph: SensorReading(
            value: 6.5,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'pH',
          ),
          uv: SensorReading(
            value: 1.1,
            timestamp: DateTime.parse('2025-04-15T10:30:00Z'),
            unit: 'UV index',
          ),
        ),
        health: HealthStatus(
          conditionIndex: ConditionIndex(
            moisture: 'Optimal',
            temperatureSoil: 'Optimal',
            lightLux: 'WarningLow',
            uvIndexPlant: 'Optimal',
            ecConductivity: 'WarningHigh',
            phWaterTank: 'Optimal',
          ),
          visualHealth: VisualHealth(
            score: 85,
            label: 'Appears Healthy',
            lastCheckTimestamp: DateTime.parse('2025-04-15T10:25:00Z'),
          ),
          overallStatus: 'Good',
          suggestions: ['Consider checking nutrient levels.'],
        ),
        latestImage: LatestImage(
          url: '/api/v1/image/latest',
          timestamp: DateTime.parse('2025-04-15T10:25:00Z'),
        ),
        pumpStatus: PumpStatus(
          isActive: false,
          lastWateredTimestamp: DateTime.parse('2025-04-15T08:00:00Z'),
          isRunning: false,
          startTime: DateTime.parse('2025-04-15T08:00:00Z'),
          duration: 0,
          remainingTime: 0,
        ),
        power: PowerStatus(
          plantNodeVoltage: 4.1,
          hubNodeVoltage: 4.0,
        ),
        autoWateringEnabled: true,
      );

      // Act & Assert
      expect(plantData.moisturePercent, 66); // Rounded from 65.5
      expect(plantData.isPumpActive, false);
      expect(plantData.lastWatered, DateTime.parse('2025-04-15T08:00:00Z'));
      expect(plantData.temperature, 24.8);
      expect(plantData.lightIntensity, 15000);
      expect(plantData.ecValue, 1.8);
      expect(plantData.phValue, 6.5);
      expect(plantData.uvIndex, 1.1);
      expect(plantData.overallHealthStatus, 'Good');
      expect(plantData.visualHealthScore, 85);
      expect(plantData.visualHealthLabel, 'Appears Healthy');
      expect(plantData.suggestions, ['Consider checking nutrient levels.']);

      // Test getSensorReading
      expect(plantData.getSensorReading('moisture'), 65.5);
      expect(plantData.getSensorReading('temperature'), 24.8);
      expect(plantData.getSensorReading('light'), 15000);
      expect(plantData.getSensorReading('ec'), 1.8);
      expect(plantData.getSensorReading('ph'), 6.5);
      expect(plantData.getSensorReading('uv'), 1.1);
      expect(plantData.getSensorReading('unknown'), null);

      // Test getConditionStatus
      expect(plantData.getConditionStatus('moisture'), 'Optimal');
      expect(plantData.getConditionStatus('temperature'), 'Optimal');
      expect(plantData.getConditionStatus('light'), 'WarningLow');
      expect(plantData.getConditionStatus('ec'), 'WarningHigh');
      expect(plantData.getConditionStatus('ph'), 'Optimal');
      expect(plantData.getConditionStatus('uv'), null); // Using uvIndexAmbient which is not in conditionIndex
      expect(plantData.getConditionStatus('unknown'), null);
    });
  });
}
