import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flora_seven/presentation/widgets/sensor_card.dart';

void main() {
  group('SensorCard', () {
    testWidgets('should display title, value, and unit', (WidgetTester tester) async {
      // Arrange
      const title = 'Temperature';
      const value = '24.8';
      const unit = '°C';
      
      // Act
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SensorCard(
              title: title,
              value: value,
              unit: unit,
              icon: Icons.thermostat,
              iconColor: Colors.orange,
              lowThreshold: 18.0,
              highThreshold: 28.0,
              currentValue: 24.8,
            ),
          ),
        ),
      );
      
      // Assert
      expect(find.text(title), findsOneWidget);
      expect(find.text(value), findsOneWidget);
      expect(find.text(unit), findsOneWidget);
    });
    
    testWidgets('should display icon', (WidgetTester tester) async {
      // Arrange
      const icon = Icons.thermostat;
      
      // Act
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SensorCard(
              title: 'Temperature',
              value: '24.8',
              unit: '°C',
              icon: icon,
              iconColor: Colors.orange,
              lowThreshold: 18.0,
              highThreshold: 28.0,
              currentValue: 24.8,
            ),
          ),
        ),
      );
      
      // Assert
      expect(find.byIcon(icon), findsOneWidget);
    });
    
    testWidgets('should call onTap when tapped', (WidgetTester tester) async {
      // Arrange
      bool wasTapped = false;
      
      // Act
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SensorCard(
              title: 'Temperature',
              value: '24.8',
              unit: '°C',
              icon: Icons.thermostat,
              iconColor: Colors.orange,
              lowThreshold: 18.0,
              highThreshold: 28.0,
              currentValue: 24.8,
              onTap: () {
                wasTapped = true;
              },
            ),
          ),
        ),
      );
      
      // Tap the card
      await tester.tap(find.byType(SensorCard));
      await tester.pump();
      
      // Assert
      expect(wasTapped, isTrue);
    });
    
    testWidgets('should show warning indicator when value is below low threshold', (WidgetTester tester) async {
      // Arrange
      const lowThreshold = 18.0;
      const currentValue = 15.0; // Below low threshold
      
      // Act
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SensorCard(
              title: 'Temperature',
              value: '15.0',
              unit: '°C',
              icon: Icons.thermostat,
              iconColor: Colors.orange,
              lowThreshold: lowThreshold,
              highThreshold: 28.0,
              currentValue: currentValue,
            ),
          ),
        ),
      );
      
      // Assert
      // We can't directly check the color, but we can check if the warning icon is present
      expect(find.byIcon(Icons.warning), findsOneWidget);
    });
    
    testWidgets('should show warning indicator when value is above high threshold', (WidgetTester tester) async {
      // Arrange
      const highThreshold = 28.0;
      const currentValue = 32.0; // Above high threshold
      
      // Act
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SensorCard(
              title: 'Temperature',
              value: '32.0',
              unit: '°C',
              icon: Icons.thermostat,
              iconColor: Colors.orange,
              lowThreshold: 18.0,
              highThreshold: highThreshold,
              currentValue: currentValue,
            ),
          ),
        ),
      );
      
      // Assert
      // We can't directly check the color, but we can check if the warning icon is present
      expect(find.byIcon(Icons.warning), findsOneWidget);
    });
    
    testWidgets('should show optimal indicator when value is within thresholds', (WidgetTester tester) async {
      // Arrange
      const lowThreshold = 18.0;
      const highThreshold = 28.0;
      const currentValue = 24.0; // Within thresholds
      
      // Act
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SensorCard(
              title: 'Temperature',
              value: '24.0',
              unit: '°C',
              icon: Icons.thermostat,
              iconColor: Colors.orange,
              lowThreshold: lowThreshold,
              highThreshold: highThreshold,
              currentValue: currentValue,
            ),
          ),
        ),
      );
      
      // Assert
      // We can't directly check the color, but we can check if the optimal icon is present
      expect(find.byIcon(Icons.check_circle), findsOneWidget);
    });
  });
}
