# Contributing to FloraSeven

First off, thank you for considering contributing to FloraSeven! It's people like you that make FloraSeven such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples**
* **Describe the behavior you observed and what you expected**
* **Include screenshots if relevant**
* **Include your environment details** (OS, Python version, Flutter version, hardware)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List any similar features in other projects**

### Pull Requests

* Fill in the required template
* Follow the coding style used throughout the project
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline

## Development Process

### Setting Up Development Environment

1. Fork the repo and create your branch from `main`
2. Set up the development environment as described in README.md
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes using clear commit messages

### Coding Standards

#### Python (Server)
* Follow PEP 8 style guide
* Use type hints where appropriate
* Write docstrings for functions and classes
* Keep functions focused and small
* Use meaningful variable names

```python
def calculate_sensor_average(readings: List[float], window_size: int = 10) -> float:
    """
    Calculate the moving average of sensor readings.
    
    Args:
        readings: List of sensor readings
        window_size: Number of readings to average (default: 10)
        
    Returns:
        float: The calculated average
    """
    return sum(readings[-window_size:]) / min(len(readings), window_size)
```

#### Dart (Mobile App)
* Follow Dart style guide
* Use meaningful widget names
* Keep widgets small and focused
* Use const constructors where possible
* Document public APIs

```dart
/// Displays real-time sensor data in a card format.
class SensorDataCard extends StatelessWidget {
  const SensorDataCard({
    Key? key,
    required this.sensorType,
    required this.value,
    required this.unit,
  }) : super(key: key);

  final String sensorType;
  final double value;
  final String unit;

  @override
  Widget build(BuildContext context) {
    // Implementation
  }
}
```

#### C++ (Hardware)
* Follow Arduino/ESP32 conventions
* Comment complex logic
* Use meaningful variable names
* Keep functions focused
* Document pin assignments

```cpp
// Pin Definitions
const int MOISTURE_PIN = 34;  // GPIO34 (ADC1_CH6) - Capacitive Moisture Sensor
const int TEMP_SENSOR_PIN = 4;  // GPIO4 - DS18B20 OneWire Temperature Sensor

/**
 * Read moisture sensor and return calibrated percentage
 * @return Moisture level as percentage (0-100)
 */
float readMoisturePercentage() {
    int raw = analogRead(MOISTURE_PIN);
    return map(raw, DRY_VALUE, WET_VALUE, 0, 100);
}
```

### Testing

* Write unit tests for new functionality
* Ensure all existing tests pass
* Test on actual hardware when possible
* Include integration tests for API endpoints

#### Running Tests

```bash
# Server tests
cd Server
python -m pytest tests/

# Mobile app tests
cd Mobile-App-Android
flutter test
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests after the first line

Examples:
```
Add moisture sensor calibration feature

- Implement two-point calibration
- Add calibration UI in settings
- Store calibration values in local storage
- Fixes #123
```

### Documentation

* Update README.md if you change functionality
* Update API documentation for new endpoints
* Add inline comments for complex logic
* Update user guide for user-facing changes

## Project Structure

```
FloraSeven/
├── Mobile-App-Android/     # Flutter mobile application
├── Server/                 # Python Flask backend
├── Hardware/               # Firmware and schematics
│   └── Firmware/          # ESP32 and Arduino code
├── Documentation/          # Project documentation
└── README.md              # Main project README
```

## Areas for Contribution

### High Priority
* Multi-plant support
* iOS app development
* Advanced disease detection
* Cloud integration
* Comprehensive testing

### Medium Priority
* Watering schedules
* Weather API integration
* Web dashboard
* OTA firmware updates
* Solar charging support

### Good First Issues
* UI/UX improvements
* Documentation enhancements
* Bug fixes
* Code refactoring
* Additional sensor support

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
