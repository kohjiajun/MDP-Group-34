#!/usr/bin/env python3
"""
Comprehensive STM32 connection test script based on task1.py.
Tests serial communication, command sending, and ACK response handling.
"""

import time
import sys
import os
import signal
from typing import Optional

# Add the parent directory to the path to import the stm32 module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from communication.stm32 import STMLink


class STM32ConnectionTester:
    """
    Test class for STM32 serial communication based on task1.py patterns.
    """
    
    def __init__(self):
        self.stm_link = STMLink()
        self.test_results = []
        self.running = True
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals for graceful shutdown."""
        print(f"\n[{time.strftime('%H:%M:%S')}] Received signal {signum}. Stopping tests...")
        self.running = False
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results."""
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"   {status}: {test_name}")
        if details:
            print(f"      {details}")
        self.test_results.append((test_name, success, details))
    
    def connect(self) -> bool:
        """Establish serial connection to STM32."""
        try:
            print("1. Establishing serial connection to STM32...")
            print("   Make sure your STM32 is connected via USB...")
            self.stm_link.connect()
            self.log_test("Serial Connection", True, "Connection established successfully")
            return True
        except Exception as e:
            self.log_test("Serial Connection", False, f"Connection failed: {e}")
            return False
    
    def test_basic_communication(self) -> bool:
        """Test basic send/receive functionality."""
        print("\n2. Testing basic communication...")
        
        try:
            # Test sending a simple command
            test_command = "STOP"
            self.stm_link.send(test_command)
            self.log_test("Command Sending", True, f"Sent: {test_command}")
            
            # Wait for ACK response
            print("   Waiting for ACK response (5 seconds)...")
            start_time = time.time()
            ack_received = False
            
            while time.time() - start_time < 5:
                try:
                    response = self.stm_link.recv()
                    if response:
                        if response.strip() == "ACK":
                            self.log_test("ACK Response", True, f"Received: {response}")
                            ack_received = True
                            break
                        else:
                            print(f"   Unexpected response: {response}")
                except Exception as e:
                    print(f"   Error receiving: {e}")
                    time.sleep(0.1)
            
            if not ack_received:
                self.log_test("ACK Response", False, "No ACK received within timeout")
            
            return ack_received
            
        except Exception as e:
            self.log_test("Basic Communication", False, f"Failed: {e}")
            return False
    
    def test_path_mode_commands(self) -> bool:
        """Test path mode commands (FW, BW, FL, FR, BL, BR)."""
        print("\n3. Testing path mode commands...")
        
        path_commands = [
            "FW01",  # Move forward 1 unit
            "BW01",  # Move backward 1 unit
            "FL00",  # Move to forward-left
            "FR00",  # Move to forward-right
            "BL00",  # Move to backward-left
            "BR00",  # Move to backward-right
        ]
        
        success_count = 0
        
        for i, command in enumerate(path_commands, 1):
            try:
                print(f"   Testing command {i}/{len(path_commands)}: {command}")
                self.stm_link.send(command)
                
                # Wait for ACK
                start_time = time.time()
                ack_received = False
                
                while time.time() - start_time < 3:  # 3 second timeout per command
                    try:
                        response = self.stm_link.recv()
                        if response and response.strip() == "ACK":
                            ack_received = True
                            success_count += 1
                            print(f"   ✓ ACK received for {command}")
                            break
                    except Exception as e:
                        print(f"   Error receiving ACK for {command}: {e}")
                        break
                    time.sleep(0.1)
                
                if not ack_received:
                    print(f"   ✗ No ACK received for {command}")
                
                # Small delay between commands
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ✗ Error sending {command}: {e}")
        
        success_rate = success_count / len(path_commands)
        self.log_test("Path Mode Commands", success_rate > 0.5, 
                     f"Success rate: {success_count}/{len(path_commands)} ({success_rate:.1%})")
        
        return success_rate > 0.5
    
    def test_manual_mode_commands(self) -> bool:
        """Test manual mode commands (FW--, BW--, TL--, TR--, STOP)."""
        print("\n4. Testing manual mode commands...")
        
        manual_commands = [
            "FW--",  # Move forward indefinitely
            "STOP",  # Stop all servos
            "BW--",  # Move backward indefinitely
            "STOP",  # Stop all servos
            "TL--",  # Steer left indefinitely
            "STOP",  # Stop all servos
            "TR--",  # Steer right indefinitely
            "STOP",  # Stop all servos
        ]
        
        success_count = 0
        
        for i, command in enumerate(manual_commands, 1):
            try:
                print(f"   Testing command {i}/{len(manual_commands)}: {command}")
                self.stm_link.send(command)
                
                # Wait for ACK
                start_time = time.time()
                ack_received = False
                
                while time.time() - start_time < 3:
                    try:
                        response = self.stm_link.recv()
                        if response and response.strip() == "ACK":
                            ack_received = True
                            success_count += 1
                            print(f"   ✓ ACK received for {command}")
                            break
                    except Exception as e:
                        print(f"   Error receiving ACK for {command}: {e}")
                        break
                    time.sleep(0.1)
                
                if not ack_received:
                    print(f"   ✗ No ACK received for {command}")
                
                # Longer delay for manual commands to see movement
                if command != "STOP":
                    time.sleep(1.0)  # Let the movement be visible
                else:
                    time.sleep(0.5)
                
            except Exception as e:
                print(f"   ✗ Error sending {command}: {e}")
        
        success_rate = success_count / len(manual_commands)
        self.log_test("Manual Mode Commands", success_rate > 0.5, 
                     f"Success rate: {success_count}/{len(manual_commands)} ({success_rate:.1%})")
        
        return success_rate > 0.5
    
    def test_special_commands(self) -> bool:
        """Test special commands used in task1.py."""
        print("\n5. Testing special commands...")
        
        special_commands = [
            "RS00",  # Gyro reset (line 200 in task1.py)
            "A",     # Special command A
            "C",     # Special command C
            "DT",    # Special command DT
            "ZZ",    # Special command ZZ
        ]
        
        success_count = 0
        
        for i, command in enumerate(special_commands, 1):
            try:
                print(f"   Testing special command {i}/{len(special_commands)}: {command}")
                self.stm_link.send(command)
                
                # Wait for ACK
                start_time = time.time()
                ack_received = False
                
                while time.time() - start_time < 3:
                    try:
                        response = self.stm_link.recv()
                        if response and response.strip() == "ACK":
                            ack_received = True
                            success_count += 1
                            print(f"   ✓ ACK received for {command}")
                            break
                    except Exception as e:
                        print(f"   Error receiving ACK for {command}: {e}")
                        break
                    time.sleep(0.1)
                
                if not ack_received:
                    print(f"   ✗ No ACK received for {command}")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ✗ Error sending {command}: {e}")
        
        success_rate = success_count / len(special_commands)
        self.log_test("Special Commands", success_rate > 0.5, 
                     f"Success rate: {success_count}/{len(special_commands)} ({success_rate:.1%})")
        
        return success_rate > 0.5
    
    def test_continuous_communication(self) -> bool:
        """Test continuous communication with multiple commands."""
        print("\n6. Testing continuous communication...")
        
        # Create a sequence of commands
        command_sequence = [
            "RS00",  # Reset
            "FW01",  # Forward
            "FL00",  # Forward-left
            "FR00",  # Forward-right
            "BW01",  # Backward
            "STOP",  # Stop
        ]
        
        success_count = 0
        total_commands = len(command_sequence)
        
        print(f"   Sending {total_commands} commands in sequence...")
        
        for i, command in enumerate(command_sequence, 1):
            try:
                print(f"   Command {i}/{total_commands}: {command}")
                self.stm_link.send(command)
                
                # Wait for ACK
                start_time = time.time()
                ack_received = False
                
                while time.time() - start_time < 2:  # 2 second timeout
                    try:
                        response = self.stm_link.recv()
                        if response and response.strip() == "ACK":
                            ack_received = True
                            success_count += 1
                            print(f"   ✓ ACK received")
                            break
                    except Exception as e:
                        print(f"   Error: {e}")
                        break
                    time.sleep(0.1)
                
                if not ack_received:
                    print(f"   ✗ No ACK received")
                
                time.sleep(0.3)  # Small delay between commands
                
            except Exception as e:
                print(f"   ✗ Error sending {command}: {e}")
        
        success_rate = success_count / total_commands
        self.log_test("Continuous Communication", success_rate > 0.8, 
                     f"Success rate: {success_count}/{total_commands} ({success_rate:.1%})")
        
        return success_rate > 0.8
    
    def continuous_message_scan(self, duration: int = 0):
        """
        Continuously scan for messages from STM32.
        
        Args:
            duration: Duration in seconds to scan (0 = infinite until Ctrl+C)
        """
        print(f"\n=== Continuous STM32 Message Scanning ===")
        if duration > 0:
            print(f"Scanning for {duration} seconds...")
        else:
            print("Scanning continuously (Press Ctrl+C to stop)...")
        
        print("Timestamp format: [HH:MM:SS]")
        print("-" * 50)
        
        received_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                try:
                    message = self.stm_link.recv()
                    if message:
                        received_count += 1
                        timestamp = time.strftime("%H:%M:%S", time.localtime())
                        print(f"[{timestamp}] Message #{received_count}: {message}")
                        
                        # Check if it's an ACK
                        if message.strip() == "ACK":
                            print(f"[{timestamp}]   → ACK received")
                        else:
                            print(f"[{timestamp}]   → Other message")
                        
                        print("-" * 50)
                    
                    # Check if duration limit reached
                    if duration > 0 and (time.time() - start_time) >= duration:
                        print(f"\n[{time.strftime('%H:%M:%S')}] Duration limit reached. Stopping...")
                        break
                        
                    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                    
                except Exception as e:
                    timestamp = time.strftime("%H:%M:%S", time.localtime())
                    print(f"[{timestamp}] Error receiving message: {e}")
                    time.sleep(1)  # Wait a bit before retrying
                    
        except KeyboardInterrupt:
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            print(f"\n[{timestamp}] Scanning stopped by user")
        
        elapsed_time = time.time() - start_time
        print(f"\n=== Scan Summary ===")
        print(f"Total messages received: {received_count}")
        print(f"Scan duration: {elapsed_time:.1f} seconds")
        if received_count > 0:
            print(f"Average rate: {received_count/elapsed_time:.2f} messages/second")
        
        return received_count > 0
    
    def test_connection_stability(self) -> bool:
        """Test connection stability with rapid commands."""
        print("\n7. Testing connection stability...")
        print("   Sending rapid commands for 10 seconds...")
        
        try:
            start_time = time.time()
            command_count = 0
            ack_count = 0
            
            while time.time() - start_time < 10:
                try:
                    # Send STOP command repeatedly
                    self.stm_link.send("STOP")
                    command_count += 1
                    
                    # Try to receive ACK
                    try:
                        response = self.stm_link.recv()
                        if response and response.strip() == "ACK":
                            ack_count += 1
                    except:
                        pass  # Ignore receive errors for this test
                    
                    time.sleep(0.5)  # Send every 0.5 seconds
                    
                except Exception as e:
                    print(f"   Error during stability test: {e}")
                    break
            
            success_rate = ack_count / command_count if command_count > 0 else 0
            self.log_test("Connection Stability", success_rate > 0.5, 
                         f"Sent: {command_count}, ACKs: {ack_count} ({success_rate:.1%})")
            
            return success_rate > 0.5
            
        except Exception as e:
            self.log_test("Connection Stability", False, f"Failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from STM32."""
        print("\n8. Cleaning up connection...")
        try:
            self.stm_link.disconnect()
            self.log_test("Disconnection", True, "Connection closed successfully")
        except Exception as e:
            self.log_test("Disconnection", False, f"Error during cleanup: {e}")
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success."""
        print("=== STM32 Connection Test Suite (Based on task1.py) ===\n")
        
        # Connect first
        if not self.connect():
            return False
        
        # Run all test categories
        tests = [
            self.test_basic_communication,
            self.test_path_mode_commands,
            self.test_manual_mode_commands,
            self.test_special_commands,
            self.test_continuous_communication,
            self.test_connection_stability
        ]
        
        all_passed = True
        for test in tests:
            try:
                if not test():
                    all_passed = False
            except Exception as e:
                print(f"   ✗ Test failed with exception: {e}")
                all_passed = False
        
        # Always try to disconnect
        self.disconnect()
        
        # Print summary
        print(f"\n=== Test Summary ===")
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        print(f"Passed: {passed}/{total}")
        
        if all_passed:
            print("\n🎉 All tests passed successfully!")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
        
        return all_passed


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='STM32 Connection Test Script')
    parser.add_argument('--scan', action='store_true', 
                       help='Run continuous message scanning mode')
    parser.add_argument('--duration', type=int, default=0,
                       help='Duration for scanning in seconds (0 = infinite)')
    parser.add_argument('--test-only', action='store_true',
                       help='Run only the test suite without scanning')
    
    args = parser.parse_args()
    
    tester = STM32ConnectionTester()
    
    if args.scan:
        # Continuous scanning mode
        print("Starting continuous STM32 message scanning...\n")
        
        if not tester.connect():
            print("Failed to establish connection. Exiting.")
            return
        
        try:
            tester.continuous_message_scan(duration=args.duration)
        finally:
            tester.disconnect()
            
    elif args.test_only:
        # Test suite only
        print("Starting comprehensive STM32 connection test based on task1.py...\n")
        success = tester.run_all_tests()
        print(f"\nTest script completed. Overall result: {'SUCCESS' if success else 'FAILURE'}")
        
    else:
        # Default: Run tests then offer scanning
        print("Starting comprehensive STM32 connection test based on task1.py...\n")
        success = tester.run_all_tests()
        
        if success:
            print(f"\nTest script completed. Overall result: SUCCESS")
            
            # Ask if user wants to continue with scanning
            try:
                response = input("\nWould you like to start continuous message scanning? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    print("\nStarting continuous scanning...")
                    try:
                        tester.continuous_message_scan()
                    finally:
                        tester.disconnect()
            except KeyboardInterrupt:
                print("\nExiting...")
        else:
            print(f"\nTest script completed. Overall result: FAILURE")


if __name__ == "__main__":
    main()
