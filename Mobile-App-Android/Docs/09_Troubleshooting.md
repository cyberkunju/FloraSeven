# Troubleshooting

This document provides solutions for common issues that may arise when setting up, using, or maintaining the IoT Plant Monitoring and Watering System.

## Mobile Application Issues

### Installation Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| App won't install | Insufficient storage space | Free up storage space on your device |
| | Incompatible device | Verify your device meets the minimum requirements |
| | Corrupted APK file | Download the APK file again |
| "App not installed" error | Conflicting app version | Uninstall the existing version first |
| | Security settings | Allow installation from unknown sources in settings |

### Startup Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| App crashes on startup | Corrupted app data | Clear app data in device settings |
| | Incompatible device | Verify your device meets the minimum requirements |
| | Outdated app version | Update to the latest version |
| Splash screen freezes | Slow device | Wait longer for the app to load |
| | Network connectivity issues | Check your internet connection |
| | App initialization failure | Restart the app |

### Connection Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| No servers found | Server not running | Start the demo server or power on the hardware |
| | Different networks | Ensure your device and server are on the same network |
| | mDNS issues | Try entering the server IP address manually |
| | Firewall blocking | Check firewall settings |
| Connection lost | Network instability | Check your Wi-Fi connection |
| | Server crashed | Restart the server |
| | Power loss to hardware | Check power connections |
| Slow response time | Network latency | Move closer to your Wi-Fi router |
| | Server overloaded | Restart the server |
| | App needs restart | Close and reopen the app |

### UI Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Text too small/large | Display scaling | Adjust display settings on your device |
| | Accessibility settings | Check app and device accessibility settings |
| UI elements misaligned | Device resolution | Report the issue with your device model |
| | Outdated app version | Update to the latest version |
| Dark mode issues | Theme implementation bugs | Toggle theme settings or restart the app |
| | Device compatibility | Report the issue with your device model |

### Functionality Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Water button not working | Cooldown period active | Wait for the cooldown period to end |
| | Connection issues | Check server connection |
| | Server error | Check server logs |
| Auto-watering not working | Feature disabled | Enable auto-watering in settings |
| | Threshold set too low | Adjust moisture thresholds |
| | Connection issues | Check server connection |
| Moisture readings not updating | Connection issues | Check server connection |
| | Sensor issues | Check sensor connections |
| | Server not running | Restart the server |
| Notifications not appearing | Notifications disabled | Check app and device notification settings |
| | Background restrictions | Allow app to run in background |
| | Do Not Disturb mode | Check device DND settings |

## Demo Server Issues

### Installation Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Python not found | Python not installed | Install Python 3.8 or higher |
| | Python not in PATH | Add Python to your system PATH |
| Package installation fails | Internet connectivity | Check your internet connection |
| | Incompatible package versions | Use a virtual environment |
| | Permission issues | Run as administrator or use `sudo` |

### Startup Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Server won't start | Port already in use | Change the port in `server.py` |
| | Missing dependencies | Run `pip install -r requirements.txt` |
| | Python version mismatch | Use Python 3.8 or higher |
| "Address already in use" error | Another instance running | Stop the existing server instance |
| | Another application using port | Change the port in `server.py` |
| mDNS registration fails | Network restrictions | Run with administrator privileges |
| | Firewall blocking | Check firewall settings |
| | Zeroconf issues | Update the zeroconf package |

### Runtime Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Server crashes | Unhandled exception | Check server logs for error details |
| | Memory issues | Restart the server |
| | System resource limitations | Close other applications |
| High CPU usage | Infinite loop | Check for code issues |
| | Too many clients | Limit client connections |
| | Debug mode enabled | Disable debug mode in production |
| Slow response time | System overloaded | Close other applications |
| | Network congestion | Check network traffic |
| | Inefficient code | Optimize server code |

### API Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| 404 Not Found | Incorrect endpoint URL | Verify the API endpoint URL |
| | Server not running | Start the server |
| 500 Internal Server Error | Server exception | Check server logs |
| | Implementation error | Debug the server code |
| | Resource limitations | Restart the server |
| Timeout errors | Network latency | Check network connection |
| | Server overloaded | Restart the server |
| | Long-running operation | Increase client timeout |

## Hardware Issues

### Power and Connectivity

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| ESP32 won't power on | Power supply issue | Check power adapter and connections |
| | Faulty ESP32 | Replace the ESP32 |
| | Wiring issue | Check all connections |
| ESP32 won't connect to Wi-Fi | Incorrect credentials | Verify Wi-Fi SSID and password |
| | Wi-Fi signal too weak | Move closer to the router or use a Wi-Fi extender |
| | Incompatible Wi-Fi settings | Ensure router uses compatible settings (2.4GHz) |
| ESP32 keeps disconnecting | Power instability | Use a stable power supply |
| | Wi-Fi interference | Change Wi-Fi channel |
| | ESP32 overheating | Improve ventilation |

### Sensor Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Moisture readings always high/low | Sensor calibration | Recalibrate the sensor |
| | Sensor placement | Adjust sensor position in soil |
| | Wiring issue | Check sensor connections |
| Fluctuating moisture readings | Loose connections | Secure all connections |
| | Interference | Keep sensor wires away from power lines |
| | Sensor degradation | Replace the sensor |
| Sensor not detected | Wiring issue | Check sensor connections |
| | Faulty sensor | Replace the sensor |
| | Incorrect pin configuration | Verify pin settings in firmware |

### Water Pump Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Pump won't activate | Relay issue | Check relay connections |
| | Power issue | Verify pump power supply |
| | Wiring issue | Check all connections |
| | Firmware issue | Verify pump control code |
| Pump runs but no water flows | Air lock | Prime the pump |
| | Clogged tube | Clean or replace the tube |
| | Water reservoir empty | Refill the water reservoir |
| Pump leaks | Loose connections | Secure tube connections |
| | Damaged tube | Replace the tube |
| | Pump damage | Replace the pump |

### Firmware Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Upload fails | Connection issue | Check USB connection |
| | Wrong board selected | Select the correct board in Arduino IDE |
| | ESP32 in boot loop | Press and hold BOOT button during upload |
| ESP32 keeps restarting | Power issue | Use a stable power supply |
| | Memory leak | Check for memory leaks in code |
| | Watchdog timer | Add yield() calls in long loops |
| Wrong behavior after upload | Incorrect settings | Verify configuration parameters |
| | Code bugs | Debug the firmware |
| | Hardware mismatch | Verify hardware matches firmware expectations |

## System Integration Issues

### Communication Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| App can't find hardware | Different networks | Ensure both are on the same network |
| | mDNS issues | Try direct IP connection |
| | Hardware not advertising | Restart the ESP32 |
| Intermittent connection | Network instability | Check Wi-Fi signal strength |
| | Power issues | Ensure stable power to ESP32 |
| | Software bugs | Update to latest versions |
| Delayed response | Network latency | Check network performance |
| | Server processing time | Optimize server code |
| | Client-side delays | Check app performance |

### Data Synchronization

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Outdated readings | Polling interval too long | Decrease polling interval |
| | Connection issues | Check network connection |
| | Server not updating | Restart the server |
| Inconsistent data | Race conditions | Implement proper synchronization |
| | Caching issues | Clear app cache |
| | Multiple clients | Ensure only one client controls the system |
| History data missing | Storage issues | Check server storage |
| | Data not being saved | Verify data persistence code |
| | Clearing on restart | Implement persistent storage |

## Advanced Troubleshooting

### Debugging the Mobile App

1. **Enable Developer Options**
   - Go to Settings > About Phone
   - Tap Build Number 7 times
   - Return to Settings > Developer Options
   - Enable USB Debugging

2. **View Logs**
   - Connect your device to a computer
   - Run `adb logcat` to view logs
   - Filter for app logs: `adb logcat | grep "iot.waterpump"`

3. **Debug Builds**
   - Build the app in debug mode: `flutter run --debug`
   - Use Flutter DevTools for detailed debugging

### Debugging the Demo Server

1. **Run in Verbose Mode**
   - Modify `server.py` to increase logging detail
   - Add `logging.basicConfig(level=logging.DEBUG)` at the top

2. **Use Python Debugger**
   - Add `import pdb; pdb.set_trace()` at problematic points
   - Run the server and interact with the debugger

3. **Monitor Network Traffic**
   - Use Wireshark to capture and analyze network packets
   - Filter for traffic on port 8080

### Debugging the Hardware

1. **Serial Monitoring**
   - Connect ESP32 to computer via USB
   - Open Serial Monitor in Arduino IDE
   - Set baud rate to match firmware (typically 115200)

2. **Test Components Individually**
   - Test moisture sensor directly
   - Test relay and pump with simple test code
   - Verify Wi-Fi connectivity with basic example

3. **Firmware Debugging**
   - Add debug print statements
   - Implement error handling with status codes
   - Use ESP32's built-in debugging features

## Common Error Messages

### Mobile App Errors

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "Server not found" | App cannot discover or connect to server | Check server status and network |
| "Connection timeout" | Server not responding in time | Check server status and network latency |
| "Failed to load plant data" | Error retrieving plant information | Check server connection and data storage |
| "Watering failed" | Error triggering watering | Check server and hardware status |
| "Auto-watering setting failed" | Error changing auto-watering setting | Check server connection |

### Demo Server Errors

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "Address already in use" | Port 8080 is already in use | Change port or stop other service |
| "Error registering service" | mDNS registration failed | Check network and permissions |
| "ModuleNotFoundError" | Missing Python dependency | Install required packages |
| "Permission denied" | Insufficient permissions | Run with administrator privileges |
| "Connection refused" | Client cannot connect to server | Check firewall and network settings |

### Hardware Errors

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "Failed to connect to WiFi" | ESP32 cannot connect to Wi-Fi | Check credentials and signal strength |
| "Sensor reading error" | Error reading from moisture sensor | Check sensor connections |
| "Pump activation failed" | Error activating water pump | Check relay and pump connections |
| "EEPROM write error" | Error saving settings | Check EEPROM initialization |
| "OTA update failed" | Error during over-the-air update | Check network and firmware file |

## Preventive Maintenance

### Mobile Application

- Keep the app updated to the latest version
- Periodically clear app cache
- Restart the app occasionally
- Backup plant data regularly

### Demo Server

- Restart the server periodically
- Monitor server logs for warnings
- Update Python and dependencies
- Check for available disk space

### Hardware

- Clean the moisture sensor every 2-3 months
- Check water tubes for blockages
- Verify all connections are secure
- Update firmware when new versions are available
- Check water reservoir level regularly

## Getting Help

If you've tried the troubleshooting steps and still have issues:

1. **Check Documentation**
   - Review all documentation in the Docs folder
   - Check for updated documentation online

2. **Search for Solutions**
   - Search online forums and communities
   - Check GitHub issues for similar problems

3. **Ask for Help**
   - Create a detailed GitHub issue
   - Include system information, logs, and steps to reproduce
   - Provide screenshots or videos if applicable

4. **Community Support**
   - Join related forums or Discord channels
   - Participate in discussions about the project

## Reporting Bugs

When reporting bugs, include:

1. **System Information**
   - Mobile app version
   - Device model and OS version
   - Server version (if applicable)
   - Hardware configuration (if applicable)

2. **Problem Description**
   - What happened
   - What you expected to happen
   - Steps to reproduce the issue
   - Frequency of occurrence

3. **Logs and Error Messages**
   - App logs
   - Server logs
   - Hardware serial output

4. **Screenshots or Videos**
   - Visual evidence of the issue
   - UI state when the problem occurred

5. **Environment Details**
   - Network configuration
   - Special conditions or settings
