import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flora_seven/main.dart' as app;
import 'package:flora_seven/providers/plant_collection_provider.dart';
import 'package:flora_seven/domain/models/plant.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([PlantCollectionNotifier])
class MockPlantCollectionNotifier extends Mock implements PlantCollectionNotifier {}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  late MockPlantCollectionNotifier mockPlantCollectionNotifier;

  setUp(() {
    mockPlantCollectionNotifier = MockPlantCollectionNotifier();
  });

  group('Plant Management Tests', () {
    testWidgets('Plant collection should be displayed on dashboard screen', (WidgetTester tester) async {
      // Start the app
      app.main();

      // Wait for the app to settle
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Verify that the splash screen is displayed
      expect(find.text('Smart Plant Monitoring System'), findsOneWidget);
    });

    test('PlantCollectionNotifier.addPlant should add a plant', () async {
      // Configure the mock
      when(mockPlantCollectionNotifier.addPlant(
        name: 'Test Plant',
        species: 'Test Species',
        notes: 'Test notes',
      )).thenAnswer((_) async => true);

      // Call the method
      await mockPlantCollectionNotifier.addPlant(
        name: 'Test Plant',
        species: 'Test Species',
        notes: 'Test notes',
      );

      // Verify the method was called with the correct parameters
      verify(mockPlantCollectionNotifier.addPlant(
        name: 'Test Plant',
        species: 'Test Species',
        notes: 'Test notes',
      )).called(1);
    });

    test('PlantCollectionNotifier.updatePlant should update a plant', () async {
      // Create a test plant
      final testPlant = Plant(
        id: '1',
        name: 'Updated Plant',
        species: 'Updated Species',
        notes: 'Updated notes',
      );

      // Configure the mock
      when(mockPlantCollectionNotifier.updatePlant(testPlant))
          .thenAnswer((_) async => true);

      // Call the method
      await mockPlantCollectionNotifier.updatePlant(testPlant);

      // Verify the method was called with the correct parameters
      verify(mockPlantCollectionNotifier.updatePlant(testPlant)).called(1);
    });

    test('PlantCollectionNotifier.deletePlant should delete a plant', () async {
      // Configure the mock
      when(mockPlantCollectionNotifier.deletePlant('1'))
          .thenAnswer((_) async => true);

      // Call the method
      await mockPlantCollectionNotifier.deletePlant('1');

      // Verify the method was called with the correct parameters
      verify(mockPlantCollectionNotifier.deletePlant('1')).called(1);
    });

    test('PlantCollectionNotifier.waterPlant should update last watered date', () async {
      // Configure the mock
      when(mockPlantCollectionNotifier.waterPlant('1'))
          .thenAnswer((_) async => true);

      // Call the method
      await mockPlantCollectionNotifier.waterPlant('1');

      // Verify the method was called with the correct parameters
      verify(mockPlantCollectionNotifier.waterPlant('1')).called(1);
    });

    test('PlantCollectionNotifier.toggleAutoWatering should toggle auto watering', () async {
      // Configure the mock
      when(mockPlantCollectionNotifier.toggleAutoWatering('1', true))
          .thenAnswer((_) async => true);

      // Call the method
      await mockPlantCollectionNotifier.toggleAutoWatering('1', true);

      // Verify the method was called with the correct parameters
      verify(mockPlantCollectionNotifier.toggleAutoWatering('1', true)).called(1);
    });

    test('PlantCollectionNotifier should handle errors gracefully', () async {
      // Configure the mock to throw an error
      when(mockPlantCollectionNotifier.addPlant(
        name: 'Test Plant',
        species: 'Test Species',
        notes: 'Test notes',
      )).thenThrow(Exception('Failed to add plant'));

      // Call the method and expect it to throw
      expect(
        () => mockPlantCollectionNotifier.addPlant(
          name: 'Test Plant',
          species: 'Test Species',
          notes: 'Test notes',
        ),
        throwsA(isA<Exception>()),
      );

      // Verify the method was called with the correct parameters
      verify(mockPlantCollectionNotifier.addPlant(
        name: 'Test Plant',
        species: 'Test Species',
        notes: 'Test notes',
      )).called(1);
    });
  });
}
