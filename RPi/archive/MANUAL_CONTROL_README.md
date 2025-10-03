# Manual Control Program

This program allows you to demonstrate manual robot movement commands from Android tablet to RPi to STM32.

## Files

- `manual_control.py` - Main manual control program
- `test_manual_control.py` - Test script for simulation
- `MANUAL_CONTROL_README.md` - This documentation

## How to Use

### 1. Run the Manual Control Program

```bash
cd /home/gavkujo/MDP-Group-34/RPi
python3 manual_control.py
```

The program will:
- Connect to Android tablet via Bluetooth
- Connect to STM32 via UART
- Wait for manual movement commands

### 2. Send Commands from Android Tablet

Send JSON messages with the following format:

**Simple format (uses default detection '00' and 5 units):**
```json
{"cat": "manual", "value": "forward"}
{"cat": "manual", "value": "backward"}
{"cat": "manual", "value": "left"}
{"cat": "manual", "value": "right"}
{"cat": "manual", "value": "stop"}
{"cat": "manual", "value": "forward_indef"}
{"cat": "manual", "value": "backward_indef"}
```

**Advanced format with detection code and units:**
```json
{"cat": "manual", "value": {"detection": "01", "command": "forward", "units": "10"}}
{"cat": "manual", "value": {"detection": "02", "command": "backward", "units": "05"}}
{"cat": "manual", "value": {"detection": "03", "command": "left", "units": "90"}}
{"cat": "manual", "value": {"detection": "04", "command": "right", "units": "90"}}
{"cat": "manual", "value": {"detection": "05", "command": "stop", "units": ""}}
```

### 3. Available Commands

| Android Command | STM32 Format | Description |
|----------------|--------------|-------------|
| `forward` | `00FW05` | Move forward 5 units (default) |
| `backward` | `00BW05` | Move backward 5 units (default) |
| `left` | `00FL90` | Turn left 90 degrees |
| `right` | `00FR90` | Turn right 90 degrees |
| `stop` | `00STOP` | Stop all movement |
| `forward_indef` | `00FW--` | Move forward indefinitely |
| `backward_indef` | `00BW--` | Move backward indefinitely |

### 4. STM32 Command Format (XXYYYY)

- **XX**: Detection code from RPi camera (00-99)
- **YYYY**: Command to execute
  - `FWxx`: Move forward xx units
  - `BWxx`: Move backward xx units  
  - `FL90`: Turn left 90 degrees
  - `FR90`: Turn right 90 degrees
  - `FW--`: Move forward indefinitely
  - `BW--`: Move backward indefinitely
  - `STOP`: Stop all movement

### 5. Testing

You can test the program using the test script:

```bash
python3 test_manual_control.py
```

## Program Structure

The manual control program uses the same communication infrastructure as `task1.py` but simplified for manual control:

- **Android Communication**: Bluetooth connection for receiving commands
- **STM32 Communication**: UART serial connection for sending movement commands
- **Command Queue**: Simple queue system for processing commands sequentially
- **Process Management**: Separate processes for receiving and sending messages

## Key Features

1. **Simple Command Interface**: Easy-to-use JSON command format
2. **Real-time Feedback**: Android receives status updates for each command
3. **Error Handling**: Graceful handling of connection issues
4. **Reconnection Support**: Automatic reconnection if Android disconnects
5. **Movement Locking**: Prevents overlapping commands

## Troubleshooting

1. **Bluetooth Connection Issues**: Ensure Android tablet is paired with RPi
2. **STM32 Connection Issues**: Check UART port and baud rate in settings.py
3. **Command Not Executing**: Check if STM32 is responding with ACK messages
4. **Android Disconnection**: Program will automatically attempt reconnection

## Example Usage

1. Start the program: `python3 manual_control.py`
2. Connect Android tablet via Bluetooth
3. Send command: `{"cat": "manual", "value": "forward"}`
4. Robot moves forward and sends ACK back
5. Android receives confirmation message

This simple program demonstrates the complete communication chain: Android → RPi → STM32 → Robot Movement.
