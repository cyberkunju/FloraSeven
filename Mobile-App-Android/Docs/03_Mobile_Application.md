# Mobile Application

This document provides detailed information about the Flutter mobile application component of the IoT Plant Monitoring and Watering System.

## Overview

The mobile application is built using Flutter, a cross-platform UI toolkit by Google. It allows users to monitor plant status, control watering, and manage their plant collection. The app communicates with the ESP32 hardware (or demo server) via HTTP requests and discovers servers using mDNS.

## Features

- **Plant Management**: Add, edit, and remove plants from your collection
- **Real-time Monitoring**: View current moisture levels and system status
- **Manual Watering**: Trigger watering with a single tap
- **Auto-watering Configuration**: Set moisture thresholds for automated watering
- **Server Discovery**: Automatically find ESP32 devices on the local network
- **Notifications**: Receive alerts for low moisture levels and system events
- **Dark/Light Theme**: Switch between dark and light themes
- **Demo/Hardware Mode**: Choose between demo mode and hardware mode

## Technical Details

### Dependencies

The application uses the following key dependencies:

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.4.9      # State management
  shared_preferences: ^2.2.2    # Local storage
  http: ^1.1.2                  # HTTP requests
  multicast_dns: ^0.3.2         # mDNS for server discovery
  lottie: ^2.7.0                # Animation support
  flutter_animate: ^4.5.0       # UI animations
  google_fonts: ^6.1.0          # Custom fonts
  logger: ^2.0.2+1              # Logging
```

### Project Structure

```
lib/
├── main.dart                   # Application entry point
├── models/                     # Data models
│   ├── plant.dart              # Plant model
│   ├── plant_status.dart       # Plant status model
│   └── server_info.dart        # Server information model
├── providers/                  # State management
│   ├── providers.dart          # Provider exports
│   ├── plant_provider.dart     # Plant collection management
│   ├── plant_status_provider.dart # Real-time status management
│   ├── server_discovery_provider.dart # Server discovery
│   └── theme_provider.dart     # Theme management
├── screens/                    # UI screens
│   ├── add_edit_plant_screen.dart # Add/Edit plant screen
│   ├── home_screen.dart        # Home screen with plant list
│   ├── new_splash_screen.dart  # Splash screen
│   ├── plant_detail_screen.dart # Plant details and controls
│   └── settings_screen.dart    # App settings
├── services/                   # Business logic
│   ├── api_service.dart        # API communication
│   ├── notification_service.dart # Notification management
│   └── server_discovery_service.dart # mDNS discovery
└── utils/                      # Utilities
    ├── app_constants.dart      # Constants and theme
    ├── app_logger.dart         # Logging configuration
    └── extensions.dart         # Extension methods
```

### State Management

The application uses Riverpod for state management. Key providers include:

1. **PlantProvider**: Manages the collection of plants
   ```dart
   final plantProvider = StateNotifierProvider<PlantNotifier, List<Plant>>((ref) {
     return PlantNotifier();
   });
   ```

2. **PlantStatusProvider**: Manages real-time plant status
   ```dart
   final plantStatusProvider = StateNotifierProvider<PlantStatusNotifier, PlantStatus>((ref) {
     return PlantStatusNotifier();
   });
   ```

3. **ServerDiscoveryProvider**: Manages server discovery
   ```dart
   final serverDiscoveryProvider = StateNotifierProvider<ServerDiscoveryNotifier, List<ServerInfo>>((ref) {
     return ServerDiscoveryNotifier();
   });
   ```

4. **ThemeProvider**: Manages app theme
   ```dart
   final themeModeProvider = StateProvider<ThemeMode>((ref) {
     return ThemeMode.system;
   });
   ```

### Key Classes

#### Plant Model

```dart
class Plant {
  final String id;
  final String name;
  final String species;
  final String imageUrl;
  final int moistureThresholdLow;
  final int moistureThresholdHigh;
  final bool autoWatering;
  final DateTime lastWatered;

  Plant({
    required this.id,
    required this.name,
    required this.species,
    this.imageUrl = '',
    this.moistureThresholdLow = 30,
    this.moistureThresholdHigh = 70,
    this.autoWatering = false,
    DateTime? lastWatered,
  }) : this.lastWatered = lastWatered ?? DateTime.now();

  // Factory methods, copyWith, toJson, fromJson methods...
}
```

#### PlantStatus Model

```dart
class PlantStatus {
  final int moisturePercent;
  final bool isWatering;
  final bool autoWateringEnabled;
  final DateTime lastUpdated;
  final bool isConnected;
  final String systemStatus;

  PlantStatus({
    this.moisturePercent = 0,
    this.isWatering = false,
    this.autoWateringEnabled = false,
    DateTime? lastUpdated,
    this.isConnected = false,
    this.systemStatus = 'Unknown',
  }) : this.lastUpdated = lastUpdated ?? DateTime.now();

  // Factory methods, copyWith, toJson, fromJson methods...
}
```

### API Communication

The application communicates with the ESP32 hardware (or demo server) using the ApiService:

```dart
class ApiService {
  final String baseUrl;
  final http.Client _client;
  final Logger _logger = Logger();

  ApiService({required this.baseUrl, http.Client? client})
      : _client = client ?? http.Client();

  Future<PlantStatus> getStatus() async {
    try {
      final response = await _client.get(Uri.parse('$baseUrl/api/status'));
      
      if (response.statusCode == 200) {
        return PlantStatus.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to load status: ${response.statusCode}');
      }
    } catch (e) {
      _logger.e('Error getting status: $e');
      throw Exception('Failed to connect to server: $e');
    }
  }

  Future<bool> triggerWatering() async {
    try {
      final response = await _client.post(Uri.parse('$baseUrl/api/water'));
      
      return response.statusCode == 200;
    } catch (e) {
      _logger.e('Error triggering watering: $e');
      return false;
    }
  }

  Future<bool> setAutoWatering(bool enabled) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/api/auto_watering'),
        body: jsonEncode({'enabled': enabled}),
        headers: {'Content-Type': 'application/json'},
      );
      
      return response.statusCode == 200;
    } catch (e) {
      _logger.e('Error setting auto watering: $e');
      return false;
    }
  }
}
```

### Server Discovery

The application discovers ESP32 devices on the local network using mDNS:

```dart
class ServerDiscoveryService {
  final MDnsClient _client = MDnsClient();
  final Logger _logger = Logger();
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;
    
    await _client.start();
    _isInitialized = true;
    _logger.i('mDNS client started');
  }

  Future<List<ServerInfo>> discoverServers() async {
    await initialize();
    
    final List<ServerInfo> servers = [];
    
    await for (final PtrResourceRecord ptr in _client.lookup<PtrResourceRecord>(
      ResourceRecordQuery.serverPointer('_plantmonitor._tcp.local'),
    )) {
      await for (final SrvResourceRecord srv in _client.lookup<SrvResourceRecord>(
        ResourceRecordQuery.service(ptr.domainName),
      )) {
        await for (final IPAddressResourceRecord ip in _client.lookup<IPAddressResourceRecord>(
          ResourceRecordQuery.addressIPv4(srv.target),
        )) {
          final server = ServerInfo(
            name: ptr.domainName,
            host: ip.address.address,
            port: srv.port,
          );
          
          servers.add(server);
          _logger.i('Discovered server: ${server.name} at ${server.host}:${server.port}');
        }
      }
    }
    
    return servers;
  }

  void dispose() {
    if (_isInitialized) {
      _client.stop();
      _isInitialized = false;
      _logger.i('mDNS client stopped');
    }
  }
}
```

### Notification System

The application uses a notification service to alert users about important events:

```dart
class NotificationService {
  static bool _isInitialized = false;
  static final Logger _logger = Logger();
  static int _notificationCount = 0;

  // Initialize the notification service
  static Future<void> initialize() async {
    if (_isInitialized) return;

    _isInitialized = true;
    _logger.i('Notification service initialized');
  }

  // Show a notification when a plant needs watering
  static Future<void> showWateringNeededNotification(Plant plant) async {
    await initialize();
    
    // Update the notification count
    _notificationCount++;
    
    // In a real implementation, we would use a proper notification system
    // For now, we'll just log the notification
    _logger.i('Watering needed notification shown for ${plant.name}');
    _logger.i('Total notifications: $_notificationCount');
  }

  // Additional notification methods...
}
```

## UI Components

### Screens

1. **Splash Screen**: Initial loading screen with animation
2. **Home Screen**: Displays the plant collection with status indicators
3. **Plant Detail Screen**: Shows detailed information about a plant and controls
4. **Add/Edit Plant Screen**: Form for adding or editing plant information
5. **Settings Screen**: App configuration options

### Themes

The application supports both light and dark themes:

```dart
class AppTheme {
  static final ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      brightness: Brightness.light,
    ),
    // Additional theme settings...
  );

  static final ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      brightness: Brightness.dark,
    ),
    // Additional theme settings...
  );
}
```

## Building the Application

To build the application for different platforms:

### Android

```bash
flutter build apk
```

This will create an APK file at `build/app/outputs/flutter-apk/app-release.apk`.

### iOS

```bash
flutter build ios
```

Note: iOS builds require a Mac with Xcode installed.

## Testing

The application includes unit tests for core functionality:

```bash
flutter test
```

## Performance Considerations

1. **Polling Interval**: The app polls for status updates every 5 seconds to balance responsiveness and battery usage
2. **Image Caching**: Plant images are cached to reduce network usage
3. **Lazy Loading**: Lists use lazy loading for better performance with large collections

## Accessibility

The application follows Flutter's accessibility guidelines:

1. **Semantic Labels**: UI elements have semantic labels for screen readers
2. **Sufficient Contrast**: Text and UI elements have sufficient contrast
3. **Scalable Text**: Text scales according to system settings

## Future Enhancements

1. **Push Notifications**: Implement Firebase Cloud Messaging for push notifications
2. **Offline Mode**: Add support for offline operation with local caching
3. **Plant Recognition**: Integrate plant recognition using machine learning
4. **Water Usage Tracking**: Track and visualize water usage over time
5. **Multiple User Support**: Add user accounts and sharing capabilities
