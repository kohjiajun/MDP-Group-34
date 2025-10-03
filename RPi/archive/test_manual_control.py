#!/usr/bin/env python3
"""
Test script for manual control program.
This simulates Android tablet sending commands to test the manual control system.
"""

import json
import socket
import time
import threading


class AndroidSimulator:
    """
    Simulates Android tablet sending commands to the RPi.
    """
    
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to RPi (simulated)"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print("Connected to RPi")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def send_command(self, command):
        """Send a manual command to RPi"""
        message = {
            "cat": "manual",
            "value": command
        }
        
        try:
            self.socket.send(f"{json.dumps(message)}\n".encode('utf-8'))
            print(f"Sent command: {command}")
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from RPi"""
        if self.socket:
            self.socket.close()
            print("Disconnected from RPi")


def interactive_test():
    """Interactive test mode"""
    print("Manual Control Test - Interactive Mode")
    print("=====================================")
    print("Available commands:")
    print("1. forward - Move forward")
    print("2. backward - Move backward")
    print("3. left - Turn left")
    print("4. right - Turn right")
    print("5. stop - Stop movement")
    print("6. forward_indef - Move forward indefinitely")
    print("7. backward_indef - Move backward indefinitely")
    print("8. quit - Exit test")
    print()
    
    # Note: This is a simulation - in real testing, you would connect to the actual RPi
    print("Note: This is a simulation script.")
    print("In real testing, connect your Android tablet to the RPi via Bluetooth")
    print("and send JSON messages with the format:")
    print()
    print("Simple format (friendly commands):")
    print('{"cat": "manual", "value": "forward"}')
    print('{"cat": "manual", "value": "stop"}')
    print()
    print("Direct STM32 format:")
    print('{"cat": "manual", "value": "FW--"}')
    print('{"cat": "manual", "value": "STOP"}')
    print('{"cat": "manual", "value": "FW05"}')
    print()
    print("Advanced format with detection code:")
    print('{"cat": "manual", "value": {"detection": "01", "command": "forward", "units": "10"}}')
    print()
    
    while True:
        try:
            command = input("Enter command (1-8): ").strip()
            
            if command == "1":
                print("Simulating: forward command -> STM32: 00FW05")
            elif command == "2":
                print("Simulating: backward command -> STM32: 00BW05")
            elif command == "3":
                print("Simulating: left command -> STM32: 00FL90")
            elif command == "4":
                print("Simulating: right command -> STM32: 00FR90")
            elif command == "5":
                print("Simulating: stop command -> STM32: 00STOP")
            elif command == "6":
                print("Simulating: forward_indef command -> STM32: 00FW--")
            elif command == "7":
                print("Simulating: backward_indef command -> STM32: 00BW--")
            elif command == "8":
                print("Exiting test...")
                break
            else:
                print("Invalid command. Please enter 1-8.")
                
        except KeyboardInterrupt:
            print("\nExiting test...")
            break


def automated_test():
    """Automated test sequence"""
    print("Manual Control Test - Automated Mode")
    print("====================================")
    
    # Test simple commands
    simple_commands = ["forward", "left", "right", "backward", "stop"]
    
    print("Testing simple commands:")
    for i, command in enumerate(simple_commands, 1):
        print(f"Test {i}: {command} -> STM32: 00{command.upper()}")
        time.sleep(1)  # Simulate command execution time
    
    print("\nTesting advanced commands with detection codes:")
    advanced_commands = [
        {"detection": "01", "command": "forward", "units": "10"},
        {"detection": "02", "command": "backward", "units": "05"},
        {"detection": "03", "command": "left", "units": "90"},
        {"detection": "04", "command": "forward_indef", "units": "--"}
    ]
    
    for i, cmd in enumerate(advanced_commands, 1):
        print(f"Test {i}: {cmd} -> STM32: {cmd['detection']}{cmd['command'].upper()}")
        time.sleep(1)
    
    print("Automated test completed!")


if __name__ == "__main__":
    print("Manual Control Test Script")
    print("=========================")
    print()
    print("This script helps you test the manual control program.")
    print("Choose test mode:")
    print("1. Interactive mode")
    print("2. Automated mode")
    print("3. Show JSON examples")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            interactive_test()
        elif choice == "2":
            automated_test()
        elif choice == "3":
            print("\nJSON Command Examples:")
            print("=====================")
            print("\nFriendly format (uses default detection '00' and 5 units):")
            print('{"cat": "manual", "value": "forward"}        -> STM32: 00FW05')
            print('{"cat": "manual", "value": "backward"}       -> STM32: 00BW05')
            print('{"cat": "manual", "value": "left"}           -> STM32: 00FL90')
            print('{"cat": "manual", "value": "right"}          -> STM32: 00FR90')
            print('{"cat": "manual", "value": "stop"}           -> STM32: 00STOP')
            print('{"cat": "manual", "value": "forward_indef"}  -> STM32: 00FW--')
            print('{"cat": "manual", "value": "backward_indef"} -> STM32: 00BW--')
            print("\nDirect STM32 format (converts to XXYYYY):")
            print('{"cat": "manual", "value": "FW--"}           -> STM32: 00FW--')
            print('{"cat": "manual", "value": "STOP"}           -> STM32: 00STOP')
            print('{"cat": "manual", "value": "FW05"}           -> STM32: 00FW05')
            print('{"cat": "manual", "value": "BW10"}           -> STM32: 00BW10')
            print('{"cat": "manual", "value": "FL90"}           -> STM32: 00FL90')
            print('{"cat": "manual", "value": "FR90"}           -> STM32: 00FR90')
            print("\nAdvanced format with detection code and units:")
            print('{"cat": "manual", "value": {"detection": "01", "command": "forward", "units": "10"}}  -> STM32: 01FW10')
            print('{"cat": "manual", "value": {"detection": "02", "command": "backward", "units": "05"}} -> STM32: 02BW05')
            print('{"cat": "manual", "value": {"detection": "03", "command": "left", "units": "90"}}     -> STM32: 03FL90')
            print('{"cat": "manual", "value": {"detection": "04", "command": "right", "units": "90"}}    -> STM32: 04FR90')
            print('{"cat": "manual", "value": {"detection": "05", "command": "stop", "units": ""}}       -> STM32: 05STOP')
            print("\nSTM32 Command Format (XXYYYY):")
            print("XX = Detection code (00-99)")
            print("YYYY = Command (FWxx, BWxx, FL90, FR90, STOP, FW--, BW--)")
            print("Examples: 00FW05, 01BW10, 02FL90, 03STOP, 04FW--")
        else:
            print("Invalid choice.")
            
    except KeyboardInterrupt:
        print("\nExiting...")
