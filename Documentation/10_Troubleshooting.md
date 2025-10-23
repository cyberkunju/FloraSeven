# FloraSeven Troubleshooting Guide

This guide provides detailed troubleshooting steps for common issues you might encounter with the FloraSeven system. It covers hardware, server, and mobile application issues.

## Hardware Troubleshooting

### Plant Node Issues

#### Node Not Powering On

**Symptoms:**
- No LED indicators
- No serial output when connected to computer
- Not appearing in MQTT messages

**Possible Causes:**
1. Depleted battery
2. Faulty power circuit
3. Hardware damage

**Troubleshooting Steps:**
1. Check battery voltage with a multimeter (should be >3.6V)
2. Connect to USB power and check if it powers on
3. Check for physical damage to the circuit board
4. Verify that the power switch is in the ON position
5. Check voltage regulator output (should be 3.3V)

**Resolution:**
- Recharge or replace the battery
- Replace the voltage regulator if faulty
- Repair or replace the node if damaged

#### Node Not Connecting to WiFi

**Symptoms:**
- Serial output shows WiFi connection failures
- Node resets repeatedly
- No MQTT messages from node

**Possible Causes:**
1. Incorrect WiFi credentials
2. Weak WiFi signal
3. WiFi network issues
4. ESP32 WiFi hardware issues

**Troubleshooting Steps:**
1. Connect to the node via serial and check error messages
2. Verify WiFi credentials in the firmware
3. Check WiFi signal strength at node location
4. Try connecting to a different WiFi network
5. Reset the WiFi router

**Resolution:**
- Update firmware with correct WiFi credentials
- Move the node closer to the WiFi router
- Use a WiFi range extender if necessary
- Replace the ESP32 if WiFi hardware is faulty

#### Erratic Sensor Readings

**Symptoms:**
- Wildly fluctuating sensor values
- Negative or impossibly high readings
- Missing sensor data

**Possible Causes:**
1. Loose sensor connections
2. Sensor hardware failure
3. Power supply issues
4. ADC interference
5. Software bugs

**Troubleshooting Steps:**
1. Check all sensor connections
2. Test sensors individually with a simple test program
3. Check power supply voltage stability
4. Verify sensor calibration
5. Check for interference from other devices

**Resolution:**
- Secure loose connections
- Replace faulty sensors
- Improve power supply filtering
- Recalibrate sensors
- Update firmware to fix bugs

#### Short Battery Life

**Symptoms:**
- Battery depletes much faster than expected (< 24 hours)
- Node resets frequently
- Low battery warnings

**Possible Causes:**
1. Deep sleep not working properly
2. High power consumption components
3. Battery degradation
4. Parasitic power drain
5. Frequent wake-ups

**Troubleshooting Steps:**
1. Monitor current consumption during sleep and active modes
2. Check if deep sleep is functioning correctly
3. Verify sleep duration settings
4. Check for components that remain powered during sleep
5. Test with a new battery

**Resolution:**
- Fix deep sleep implementation
- Optimize power consumption in firmware
- Replace degraded battery
- Remove unnecessary power-consuming components
- Increase sleep duration

### Hub Node Issues

#### Camera Not Working

**Symptoms:**
- No images captured
- Black or corrupted images
- Error messages related to camera

**Possible Causes:**
1. Loose camera ribbon cable
2. Camera hardware failure
3. Insufficient power
4. ESP32-CAM configuration issues
5. Software bugs

**Troubleshooting Steps:**
1. Check camera ribbon cable connection
2. Verify camera initialization in serial output
3. Test with a simple camera test program
4. Check power supply stability
5. Verify camera configuration settings

**Resolution:**
- Reseat or replace camera ribbon cable
- Replace camera module if faulty
- Improve power supply
- Update camera configuration
- Update firmware to fix bugs

#### Pump Not Activating

**Symptoms:**
- Pump doesn't turn on when commanded
- No water flow
- No pump activation sound

**Possible Causes:**
1. Loose pump connections
2. MOSFET failure
3. Pump hardware failure
4. I2C communication issues between ESP32-CAM and R4 Minima
5. Software bugs

**Troubleshooting Steps:**
1. Check all pump connections
2. Test MOSFET with a multimeter
3. Test pump directly with a battery
4. Verify I2C communication with a logic analyzer
5. Check for error messages in serial output

**Resolution:**
- Secure loose connections
- Replace faulty MOSFET
- Replace pump if faulty
- Fix I2C communication issues
- Update firmware to fix bugs

#### I2C Communication Failure

**Symptoms:**
- Error messages about I2C failures
- Commands not being executed
- Missing sensor data from R4 Minima

**Possible Causes:**
1. Loose I2C connections
2. Incorrect I2C address
3. Missing pull-up resistors
4. Bus contention
5. Software bugs

**Troubleshooting Steps:**
1. Check I2C connections between ESP32-CAM and R4 Minima
2. Verify I2C addresses in firmware
3. Check for pull-up resistors on SDA and SCL lines
4. Use a logic analyzer to monitor I2C traffic
5. Test with a simple I2C test program

**Resolution:**
- Secure loose connections
- Update firmware with correct I2C addresses
- Add appropriate pull-up resistors
- Fix bus contention issues
- Update firmware to fix bugs

#### Image Upload Failures

**Symptoms:**
- Images not appearing in the server
- HTTP error messages
- Timeout errors

**Possible Causes:**
1. Network connectivity issues
2. Server not running or not accessible
3. Incorrect server URL
4. Image size too large
5. Server disk space full

**Troubleshooting Steps:**
1. Check WiFi connectivity
2. Verify server is running and accessible
3. Check server URL in firmware
4. Reduce image resolution or quality
5. Check server disk space

**Resolution:**
- Improve network connectivity
- Ensure server is running
- Update firmware with correct server URL
- Adjust image settings
- Free up server disk space

## Server Troubleshooting

### Server Not Starting

**Symptoms:**
- Error messages when starting server
- Server process terminates immediately
- Port already in use errors

**Possible Causes:**
1. Missing dependencies
2. Configuration errors
3. Port conflicts
4. Permission issues
5. Python environment issues

**Troubleshooting Steps:**
1. Check error messages in console output
2. Verify all dependencies are installed
3. Check if another process is using the same port
4. Verify configuration settings
5. Check Python environment

**Resolution:**
- Install missing dependencies
- Fix configuration errors
- Change port or stop conflicting process
- Run with appropriate permissions
- Fix Python environment issues

### Database Errors

**Symptoms:**
- Database-related error messages
- Missing or corrupt data
- Server crashes when accessing database

**Possible Causes:**
1. Database file corruption
2. Disk space issues
3. Permission problems
4. Schema version mismatch
5. Concurrent access issues

**Troubleshooting Steps:**
1. Check database file integrity
2. Verify disk space availability
3. Check file permissions
4. Verify database schema version
5. Check for concurrent access issues

**Resolution:**
- Restore database from backup
- Free up disk space
- Fix permission issues
- Update database schema
- Implement proper concurrency controls

### MQTT Connection Issues

**Symptoms:**
- MQTT connection error messages
- No data from hardware nodes
- Cannot send commands to nodes

**Possible Causes:**
1. MQTT broker not running
2. Incorrect broker address or port
3. Authentication issues
4. Network connectivity problems
5. Firewall blocking MQTT traffic

**Troubleshooting Steps:**
1. Verify MQTT broker is running
2. Check broker address and port in configuration
3. Verify MQTT credentials if authentication is enabled
4. Check network connectivity to broker
5. Check firewall settings

**Resolution:**
- Start MQTT broker
- Update configuration with correct broker details
- Fix authentication issues
- Resolve network connectivity problems
- Adjust firewall settings

### API Errors

**Symptoms:**
- HTTP error responses
- Timeout errors
- Incorrect or missing data in responses

**Possible Causes:**
1. Route not implemented correctly
2. Input validation errors
3. Database access issues
4. Authentication problems
5. Internal server errors

**Troubleshooting Steps:**
1. Check server logs for error messages
2. Verify route implementation
3. Test API endpoint with a tool like Postman
4. Check authentication configuration
5. Debug server code

**Resolution:**
- Fix route implementation
- Improve input validation
- Resolve database access issues
- Fix authentication problems
- Fix server code bugs

### High CPU or Memory Usage

**Symptoms:**
- Server becomes slow or unresponsive
- High CPU usage
- Memory leaks
- Out of memory errors

**Possible Causes:**
1. Inefficient code
2. Memory leaks
3. Too many concurrent requests
4. Large image processing
5. Database queries without limits

**Troubleshooting Steps:**
1. Monitor CPU and memory usage
2. Profile the application to identify bottlenecks
3. Check for memory leaks
4. Optimize image processing
5. Review database queries

**Resolution:**
- Optimize inefficient code
- Fix memory leaks
- Implement request throttling
- Optimize image processing
- Add limits to database queries

## Mobile Application Troubleshooting

### App Not Connecting to Server

**Symptoms:**
- Connection error messages
- Cannot log in
- No data displayed
- Timeout errors

**Possible Causes:**
1. Incorrect server address
2. Server not running
3. Network connectivity issues
4. Firewall blocking traffic
5. API version mismatch

**Troubleshooting Steps:**
1. Verify server address in app settings
2. Check if server is running
3. Verify mobile device is on the same network as server
4. Check firewall settings
5. Verify API compatibility

**Resolution:**
- Update server address in app settings
- Start server
- Connect to the correct network
- Adjust firewall settings
- Update app or server to compatible versions

### Authentication Failures

**Symptoms:**
- Cannot log in
- Authentication error messages
- Session expired messages

**Possible Causes:**
1. Incorrect credentials
2. User not registered
3. Server authentication issues
4. Session timeout
5. Clock synchronization issues

**Troubleshooting Steps:**
1. Verify username and password
2. Check if user exists in server configuration
3. Check server authentication logs
4. Verify session timeout settings
5. Check device clock

**Resolution:**
- Use correct credentials
- Register user on server
- Fix server authentication issues
- Adjust session timeout settings
- Synchronize device clock

### App Crashes

**Symptoms:**
- App closes unexpectedly
- Error messages before crash
- Unresponsive UI

**Possible Causes:**
1. Unhandled exceptions
2. Memory issues
3. Resource leaks
4. Incompatible device
5. Corrupted app data

**Troubleshooting Steps:**
1. Check crash logs
2. Monitor memory usage
3. Test on different devices
4. Clear app cache and data
5. Reinstall the app

**Resolution:**
- Fix unhandled exceptions
- Optimize memory usage
- Fix resource leaks
- Update app for better device compatibility
- Clear corrupted data

### UI Display Issues

**Symptoms:**
- Elements not displaying correctly
- Text overlapping
- Missing UI components
- Incorrect colors or themes

**Possible Causes:**
1. Layout constraints issues
2. Screen size/resolution incompatibility
3. Theme configuration problems
4. Missing assets
5. Rendering bugs

**Troubleshooting Steps:**
1. Test on different screen sizes
2. Check layout constraints
3. Verify theme configuration
4. Check for missing assets
5. Debug rendering issues

**Resolution:**
- Fix layout constraints
- Improve responsiveness for different screen sizes
- Fix theme configuration
- Add missing assets
- Fix rendering bugs

### Notification Issues

**Symptoms:**
- Not receiving notifications
- Delayed notifications
- Incorrect notification content

**Possible Causes:**
1. Notifications disabled in app or system settings
2. Battery optimization killing background services
3. Notification service not running
4. Incorrect notification configuration
5. Missing notification permissions

**Troubleshooting Steps:**
1. Check app notification settings
2. Check system notification settings
3. Disable battery optimization for the app
4. Verify notification service is running
5. Check notification permissions

**Resolution:**
- Enable notifications in app settings
- Enable notifications in system settings
- Disable battery optimization for the app
- Fix notification service issues
- Grant notification permissions

## System Integration Issues

### Hardware-Server Communication Issues

**Symptoms:**
- No data from hardware in server
- Cannot send commands to hardware
- Intermittent communication

**Possible Causes:**
1. Network connectivity issues
2. MQTT configuration problems
3. Hardware not sending data
4. Server not processing messages
5. Topic mismatches

**Troubleshooting Steps:**
1. Verify network connectivity
2. Check MQTT broker logs
3. Monitor MQTT traffic with a tool like MQTT Explorer
4. Check hardware serial output
5. Verify topic names in hardware and server

**Resolution:**
- Fix network connectivity issues
- Correct MQTT configuration
- Fix hardware data sending
- Fix server message processing
- Ensure topic names match

### Server-App Communication Issues

**Symptoms:**
- App shows no data
- Cannot send commands from app
- Error messages about API

**Possible Causes:**
1. Network connectivity issues
2. API endpoint issues
3. Authentication problems
4. Data format mismatches
5. Server not processing requests

**Troubleshooting Steps:**
1. Verify network connectivity
2. Test API endpoints with a tool like Postman
3. Check authentication configuration
4. Verify data formats
5. Check server logs for request processing

**Resolution:**
- Fix network connectivity issues
- Correct API endpoint implementation
- Fix authentication issues
- Ensure data formats match
- Fix server request processing

### Time Synchronization Issues

**Symptoms:**
- Incorrect timestamps
- Events out of sequence
- Scheduling issues

**Possible Causes:**
1. Device clocks not synchronized
2. Timezone configuration issues
3. NTP not working
4. Incorrect time format parsing
5. Daylight saving time issues

**Troubleshooting Steps:**
1. Check device clock settings
2. Verify timezone configurations
3. Check NTP connectivity
4. Test time format parsing
5. Check for daylight saving time handling

**Resolution:**
- Synchronize device clocks
- Correct timezone configurations
- Fix NTP connectivity
- Fix time format parsing
- Implement proper daylight saving time handling

## Advanced Troubleshooting

### Using Serial Monitoring

For hardware issues, connecting to the serial port can provide valuable debugging information:

1. **ESP32 and ESP32-CAM**:
   - Connect USB-to-Serial adapter
   - Open Arduino IDE Serial Monitor at 115200 baud
   - Observe boot and operation messages
   - Look for error messages or unexpected behavior

2. **Arduino R4 Minima**:
   - Connect via USB
   - Open Arduino IDE Serial Monitor at 115200 baud
   - Observe operation messages
   - Look for I2C communication issues

### Using MQTT Explorer

MQTT Explorer is a valuable tool for debugging MQTT communication:

1. **Installation**:
   - Download and install MQTT Explorer from [mqtt-explorer.com](http://mqtt-explorer.com/)

2. **Connection**:
   - Connect to your MQTT broker
   - Subscribe to all topics (`#`)

3. **Monitoring**:
   - Watch for messages from hardware nodes
   - Verify message format and content
   - Check for missing messages
   - Publish test messages to command topics

### Using Network Analysis

For network-related issues, network analysis tools can help:

1. **Ping Test**:
   - Test basic connectivity between devices
   - Check for packet loss or high latency

2. **Port Scanning**:
   - Verify that required ports are open
   - Check for services running on expected ports

3. **Wireshark**:
   - Capture and analyze network traffic
   - Look for connection issues or unexpected behavior
   - Verify data formats and protocols

### Database Inspection

For database issues, direct inspection can be helpful:

1. **SQLite Browser**:
   - Open the database file with a tool like DB Browser for SQLite
   - Examine table structure
   - Check data integrity
   - Run test queries

2. **Command Line**:
   - Use the `sqlite3` command-line tool
   - Run SQL queries to inspect data
   - Check for database corruption

### Log Analysis

Detailed log analysis can reveal issues not immediately apparent:

1. **Server Logs**:
   - Examine `floraseven_server.log`
   - Look for error patterns
   - Check for recurring issues
   - Analyze timing of events

2. **App Logs**:
   - Enable verbose logging in app settings
   - Capture logs using logcat (Android)
   - Look for error patterns
   - Correlate with user actions

## Preventive Maintenance

Regular maintenance can prevent many issues:

1. **Hardware Maintenance**:
   - Regularly check and clean sensors
   - Inspect connections for corrosion or damage
   - Calibrate sensors monthly
   - Replace batteries before they fail
   - Update firmware when new versions are available

2. **Server Maintenance**:
   - Regularly backup the database
   - Monitor disk space
   - Check for software updates
   - Review logs for potential issues
   - Test system functionality periodically

3. **App Maintenance**:
   - Keep the app updated
   - Clear cache periodically
   - Check for configuration issues
   - Verify notification settings
   - Test all features regularly

## When to Seek Help

If you've tried the troubleshooting steps and still have issues, it may be time to seek help:

1. **Hardware Issues**:
   - Contact the hardware development team
   - Provide detailed description of the issue
   - Include serial output logs
   - Describe troubleshooting steps already taken

2. **Server Issues**:
   - Contact the server development team
   - Provide server logs
   - Describe the issue in detail
   - Include information about your environment

3. **App Issues**:
   - Contact the app development team
   - Provide app logs
   - Describe the issue in detail
   - Include device information and OS version

## Reporting Issues

When reporting issues, include the following information:

1. **Issue Description**:
   - What is happening
   - When it started
   - How frequently it occurs
   - Impact on functionality

2. **Environment**:
   - Hardware versions
   - Server version
   - App version
   - Network configuration
   - Operating system

3. **Logs and Data**:
   - Relevant log files
   - Screenshots or photos
   - Error messages
   - Sensor data if relevant

4. **Reproduction Steps**:
   - Detailed steps to reproduce the issue
   - Any workarounds discovered
   - What was expected vs. what happened
