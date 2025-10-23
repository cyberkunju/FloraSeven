# FloraSeven Implementation Guide

This document provides a comprehensive guide to the implementation of the FloraSeven mobile application.

## Table of Contents

1. [Architecture](#architecture)
2. [Data Flow](#data-flow)
3. [Key Components](#key-components)
4. [API Communication](#api-communication)
5. [State Management](#state-management)
6. [UI Components](#ui-components)
7. [Error Handling](#error-handling)
8. [Testing](#testing)
9. [Performance Considerations](#performance-considerations)
10. [Future Improvements](#future-improvements)

## Architecture

The FloraSeven mobile application follows Clean Architecture principles, with a clear separation of concerns:

### Presentation Layer
- **Screens**: UI screens that display data to the user and handle user interactions.
- **Widgets**: Reusable UI components used across multiple screens.

### Application Layer
- **Providers**: Riverpod providers that manage the application state and business logic.
- **Notifiers**: StateNotifier classes that handle state updates and business logic.

### Domain Layer
- **Models**: Data models that represent the core business entities.

### Data Layer
- **Services**: Services that handle communication with external systems (e.g., API).

## Data Flow

1. **User Interaction**: User interacts with the UI (e.g., taps a button).
2. **UI Event**: The UI sends an event to the appropriate provider.
3. **Provider Action**: The provider processes the event and calls the appropriate service.
4. **Service Call**: The service makes an API call to the Laptop Server.
5. **Response Processing**: The service processes the response and returns the result to the provider.
6. **State Update**: The provider updates its state based on the result.
7. **UI Update**: The UI rebuilds based on the updated state.

## Key Components

### Models

- **PlantData**: Represents the complete data for a plant, including sensor readings, health status, and system information.
- **PlantNodeData**: Represents data from the Plant Node, including moisture, temperature, light, and EC.
- **HubNodeData**: Represents data from the Hub Node, including pH and UV.
- **HealthStatus**: Represents the overall health status of the plant, including condition index and visual health.
- **ConditionIndex**: Represents the condition status of each sensor (Optimal, Warning, Critical).
- **VisualHealth**: Represents the visual health assessment from AI analysis.
- **Thresholds**: Represents the thresholds for various sensors.

### Providers

- **PlantDataProvider**: Manages the state of the plant data, including fetching and updating.
- **ThresholdsProvider**: Manages the state of the thresholds, including fetching and updating.
- **ApiServiceProvider**: Provides the API service for communication with the Laptop Server.

### Services

- **ApiService**: Handles communication with the Laptop Server API.
- **EnhancedNotificationService**: Handles system-level notifications.

### Screens

- **EnhancedSplashScreen**: The initial screen shown when the app starts.
- **EnhancedDashboardScreen**: The main screen showing a summary of the plant status.
- **PlantDetailScreen**: A detailed view of the plant status, including all sensor readings and health assessments.
- **SettingsScreen**: Allows the user to configure the app settings, including server URL and thresholds.

## API Communication

The app communicates with the Laptop Server via a REST API using the Dio HTTP client. The API endpoints are:

- `GET /api/v1/status`: Fetches the latest aggregated status from both Plant and Hub nodes, including health assessments.
- `GET /api/v1/image/latest`: Fetches the actual latest JPEG image data captured by the ESP32-CAM.
- `GET /api/v1/settings/thresholds`: Fetches the currently stored optimal thresholds from the server.
- `POST /api/v1/settings/thresholds`: Updates the optimal thresholds on the server.
- `POST /api/v1/command/water`: Sends a command to manually trigger the water pump.
- `POST /api/v1/settings/auto_watering`: Enables or disables automatic watering.

The ApiService class handles all communication with the API, including error handling and response processing.

## State Management

The app uses Riverpod for state management, with the following key providers:

- **PlantDataProvider**: A StateNotifierProvider that manages the state of the plant data.
- **ThresholdsProvider**: A StateNotifierProvider that manages the state of the thresholds.
- **ApiServiceProvider**: A Provider that provides the API service.

The providers use AsyncValue to represent the state of asynchronous operations, with three possible states:
- **Loading**: The operation is in progress.
- **Data**: The operation completed successfully with data.
- **Error**: The operation failed with an error.

## UI Components

The app includes several reusable UI components:

- **SensorCard**: A card that displays a sensor reading with a status indicator.
- **SensorDetailCard**: A detailed card that displays a sensor reading with a status indicator and additional information.
- **MoistureGauge**: A custom gauge that displays the moisture level with thresholds.
- **LoadingIndicator**: A loading indicator with a message.
- **ErrorDisplay**: An error display with a retry option.

## Error Handling

The app includes a comprehensive error handling strategy:

- **API Errors**: The ApiService catches and handles API errors, including network errors, timeouts, and server errors.
- **State Errors**: The providers use AsyncValue.error to propagate errors to the UI.
- **UI Errors**: The UI displays user-friendly error messages with retry options.

The CustomErrorHandler class provides helper methods for logging errors and generating user-friendly error messages.

## Testing

The app includes three types of tests:

- **Unit Tests**: Testing individual components like models and business logic.
- **Widget Tests**: Testing UI components in isolation.
- **Integration Tests**: Testing the app as a whole.

The tests are located in the `test` and `integration_test` directories.

## Performance Considerations

The app includes several performance optimizations:

- **Cached Network Image**: The app uses CachedNetworkImage to efficiently load and cache images.
- **Selective Rebuilds**: The app uses Riverpod's select modifier to minimize UI rebuilds.
- **Efficient Data Fetching**: The app fetches data only when needed and caches it for future use.
- **Optimized Animations**: The app uses Flutter Animate for efficient animations.

## Future Improvements

The app could be improved in several ways:

- **Offline Mode**: Add support for offline mode with local caching of data.
- **Push Notifications**: Add support for push notifications for important events.
- **Historical Data**: Add support for viewing historical data with charts and graphs.
- **User Authentication**: Add support for user authentication and multiple users.
- **Multiple Plants**: Add support for monitoring multiple plants.
- **Bluetooth Connectivity**: Add support for direct Bluetooth connectivity to the hardware nodes.
- **Advanced Analytics**: Add support for advanced analytics and insights.
- **Customizable Dashboard**: Add support for a customizable dashboard with widgets.
- **Dark Mode**: Add support for a dark mode theme.
- **Localization**: Add support for multiple languages.
- **Accessibility**: Improve accessibility features for users with disabilities.
