# Android Bluetooth Connection Testing

This directory contains test scripts to verify the Bluetooth connection between the Raspberry Pi and Android tablet.

## Test Scripts

### 1. `simple_connection_test.py` (Recommended for first-time testing)
- Basic connection test
- Simple message sending/receiving
- Good for initial setup verification

### 2. `test_android_connection.py` (Comprehensive testing)
- Full connection testing
- Multiple message types
- Connection stability testing
- More detailed error reporting

## Prerequisites

Before running the tests, ensure:

1. **Bluetooth is enabled on Raspberry Pi:**
   ```bash
   sudo systemctl status bluetooth
   ```

2. **Bluetooth packages are installed:**
   ```bash
   sudo apt-get install python3-bluetooth bluetooth libbluetooth-dev
   pip3 install PyBluez
   ```

3. **Android tablet is ready:**
   - Bluetooth is enabled
   - Device is discoverable
   - No other active Bluetooth connections

## Running the Tests

### Simple Connection Test
```bash
cd RPi/communication
python3 simple_connection_test.py
```

### Comprehensive Test
```bash
cd RPi/communication
python3 test_android_connection.py
```

## Expected Output

### Successful Connection
```
=== Simple Android Bluetooth Connection Test ===

1. Attempting to establish Bluetooth connection...
   Make sure your Android tablet is ready to connect...
   The RPi will be discoverable for Bluetooth pairing.
   ✓ Connection established successfully!

2. Sending test message...
   ✓ Sent: {"cat": "info", "value": "Hello from Raspberry Pi!"}

3. Waiting for response (5 seconds)...
   ✓ Received: {"cat": "response", "value": "Hello from Android!"}

4. Sending final message...
   ✓ Sent: {"cat": "status", "value": "test_complete"}

   ✓ Basic connection test completed!

5. Cleaning up connection...
   ✓ Connection closed successfully!

=== Test completed! ===

🎉 Connection test successful!
```

## Troubleshooting

### Common Issues

1. **Permission Denied Errors:**
   ```bash
   sudo chmod +x simple_connection_test.py
   sudo python3 simple_connection_test.py
   ```

2. **Bluetooth Service Not Running:**
   ```bash
   sudo systemctl start bluetooth
   sudo systemctl enable bluetooth
   ```

3. **Port Already in Use:**
   ```bash
   sudo hciconfig hci0 down
   sudo hciconfig hci0 up
   ```

4. **Connection Timeout:**
   - Ensure Android tablet is in pairing mode
   - Check if other devices are connected
   - Restart Bluetooth on both devices

5. **Import Errors:**
   - Verify the `communication` module is in the correct path
   - Check Python path configuration

### Debug Commands

Check Bluetooth status:
```bash
sudo hciconfig -a
sudo bluetoothctl
```

Check for active connections:
```bash
sudo lsof -i :1
```

Reset Bluetooth:
```bash
sudo systemctl restart bluetooth
sudo hciconfig hci0 reset
```

## Test Scenarios

### Basic Connectivity
- Connection establishment
- Simple message exchange
- Proper disconnection

### Message Types
- Info messages
- Status updates
- Location data
- Image recognition results
- Control commands

### Connection Stability
- Continuous message sending
- Long-running connections
- Error handling and recovery

## Notes

- The RPi will be discoverable during testing
- Each test run creates a new Bluetooth service
- The service UUID is: `94f39d29-7d6d-437d-973b-fba39e49d4ee`
- Test scripts automatically clean up connections
- Timeouts are set to prevent indefinite waiting

## Next Steps

After successful testing:
1. Integrate with your main robot control application
2. Implement proper error handling and reconnection logic
3. Add message validation and security measures
4. Consider implementing heartbeat/ping mechanisms for connection monitoring
