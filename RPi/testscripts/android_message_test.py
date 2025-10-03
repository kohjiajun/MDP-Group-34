#!/usr/bin/env python3
"""
Comprehensive Android message test script based on task1.py.
Tests all message types and communication patterns used in the main application.
"""

import json
import time
import sys
import os
from typing import Optional

# Add the parent directory to the path to import the android module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from communication.android import AndroidLink, AndroidMessage


class AndroidMessageTester:
    """
    Test class for Android message communication based on task1.py patterns.
    """
    
    def __init__(self):
        self.android_link = AndroidLink()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results."""
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"   {status}: {test_name}")
        if details:
            print(f"      {details}")
        self.test_results.append((test_name, success, details))
        
    def connect(self) -> bool:
        """Establish connection to Android."""
        try:
            print("1. Establishing Bluetooth connection...")
            print("   Make sure your Android tablet is ready to connect...")
            self.android_link.connect()
            self.log_test("Bluetooth Connection", True, "Connection established successfully")
            return True
        except Exception as e:
            self.log_test("Bluetooth Connection", False, f"Connection failed: {e}")
            return False
    
    def test_initialization_messages(self) -> bool:
        """Test the initialization messages sent in task1.py start() method."""
        print("\n2. Testing initialization messages...")
        
        try:
            # Test connection confirmation message (line 84-85 in task1.py)
            conn_msg = AndroidMessage('info', 'You are connected to the RPi!')
            self.android_link.send(conn_msg)
            self.log_test("Connection Confirmation", True, f"Sent: {conn_msg.jsonify}")
            
            time.sleep(0.5)
            
            # Test robot ready message (line 108 in task1.py)
            ready_msg = AndroidMessage('info', 'Robot is ready!')
            self.android_link.send(ready_msg)
            self.log_test("Robot Ready Message", True, f"Sent: {ready_msg.jsonify}")
            
            time.sleep(0.5)
            
            # Test mode setting message (line 109 in task1.py)
            mode_msg = AndroidMessage('mode', 'path')
            self.android_link.send(mode_msg)
            self.log_test("Mode Setting", True, f"Sent: {mode_msg.jsonify}")
            
            return True
            
        except Exception as e:
            self.log_test("Initialization Messages", False, f"Failed: {e}")
            return False
    
    def test_obstacle_messages(self) -> bool:
        """Test obstacle-related messages (lines 182-186 in task1.py)."""
        print("\n3. Testing obstacle messages...")
        
        try:
            # Test obstacle data format (based on lines 348-351 in task1.py)
            obstacle_data = {
                "obstacles": [
                    {"x": 5, "y": 10, "id": 1, "d": 2},
                    {"x": 8, "y": 12, "id": 2, "d": 4},
                    {"x": 3, "y": 7, "id": 3, "d": 6}
                ],
                "mode": "0"
            }
            
            # Simulate receiving obstacle message from Android
            obstacle_msg = AndroidMessage('obstacles', json.dumps(obstacle_data))
            self.log_test("Obstacle Data Format", True, f"Format: {obstacle_msg.jsonify}")
            
            # Test algorithm request message (line 500 in task1.py)
            algo_msg = AndroidMessage('info', 'Requesting path from algo...')
            self.android_link.send(algo_msg)
            self.log_test("Algorithm Request", True, f"Sent: {algo_msg.jsonify}")
            
            time.sleep(0.5)
            
            # Test commands received message (line 530-531 in task1.py)
            commands_msg = AndroidMessage('info', 'Commands and path received Algo API. Robot is ready to move.')
            self.android_link.send(commands_msg)
            self.log_test("Commands Received", True, f"Sent: {commands_msg.jsonify}")
            
            return True
            
        except Exception as e:
            self.log_test("Obstacle Messages", False, f"Failed: {e}")
            return False
    
    def test_control_messages(self) -> bool:
        """Test control flow messages (lines 188-214 in task1.py)."""
        print("\n4. Testing control messages...")
        
        try:
            # Test start command received message (line 205-206 in task1.py)
            start_msg = AndroidMessage('info', 'Starting robot on path!')
            self.android_link.send(start_msg)
            self.log_test("Start Command", True, f"Sent: {start_msg.jsonify}")
            
            time.sleep(0.5)
            
            # Test status running message (line 208 in task1.py)
            status_msg = AndroidMessage('status', 'running')
            self.android_link.send(status_msg)
            self.log_test("Status Running", True, f"Sent: {status_msg.jsonify}")
            
            time.sleep(0.5)
            
            # Test error message for empty queue (line 212-213 in task1.py)
            error_msg = AndroidMessage("error", "Command queue is empty, did you set obstacles?")
            self.android_link.send(error_msg)
            self.log_test("Error Message", True, f"Sent: {error_msg.jsonify}")
            
            return True
            
        except Exception as e:
            self.log_test("Control Messages", False, f"Failed: {e}")
            return False
    
    def test_location_messages(self) -> bool:
        """Test location update messages (lines 244-248 in task1.py)."""
        print("\n5. Testing location messages...")
        
        try:
            # Test location update format
            test_locations = [
                {"x": 1, "y": 1, "d": 0},
                {"x": 2, "y": 3, "d": 90},
                {"x": 5, "y": 7, "d": 180},
                {"x": 8, "y": 10, "d": 270}
            ]
            
            for i, location in enumerate(test_locations):
                location_msg = AndroidMessage('location', location)
                self.android_link.send(location_msg)
                self.log_test(f"Location Update {i+1}", True, f"Sent: {location_msg.jsonify}")
                time.sleep(0.3)
            
            return True
            
        except Exception as e:
            self.log_test("Location Messages", False, f"Failed: {e}")
            return False
    
    def test_image_recognition_messages(self) -> bool:
        """Test image recognition messages (line 491 in task1.py)."""
        print("\n6. Testing image recognition messages...")
        
        try:
            # Test successful image recognition
            success_result = {"image_id": "A", "obstacle_id": "1"}
            success_msg = AndroidMessage("image-rec", success_result)
            self.android_link.send(success_msg)
            self.log_test("Image Recognition Success", True, f"Sent: {success_msg.jsonify}")
            
            time.sleep(0.5)
            
            # Test failed image recognition
            failed_result = {"image_id": "NA", "obstacle_id": "2"}
            failed_msg = AndroidMessage("image-rec", failed_result)
            self.android_link.send(failed_msg)
            self.log_test("Image Recognition Failed", True, f"Sent: {failed_msg.jsonify}")
            
            time.sleep(0.5)
            
            # Test image capture info message (line 365-366 in task1.py)
            capture_msg = AndroidMessage("info", "Capturing image for obstacle id: 1")
            self.android_link.send(capture_msg)
            self.log_test("Image Capture Info", True, f"Sent: {capture_msg.jsonify}")
            
            return True
            
        except Exception as e:
            self.log_test("Image Recognition Messages", False, f"Failed: {e}")
            return False
    
    def test_completion_messages(self) -> bool:
        """Test completion and status messages (lines 332-334 in task1.py)."""
        print("\n7. Testing completion messages...")
        
        try:
            # Test commands finished message
            finished_msg = AndroidMessage("info", "Commands queue finished.")
            self.android_link.send(finished_msg)
            self.log_test("Commands Finished", True, f"Sent: {finished_msg.jsonify}")
            
            time.sleep(0.5)
            
            # Test status finished message
            status_finished_msg = AndroidMessage("status", "finished")
            self.android_link.send(status_finished_msg)
            self.log_test("Status Finished", True, f"Sent: {status_finished_msg.jsonify}")
            
            time.sleep(0.5)
            
            # Test stitch message (line 550 in task1.py)
            stitch_msg = AndroidMessage("info", "Images stitched!")
            self.android_link.send(stitch_msg)
            self.log_test("Images Stitched", True, f"Sent: {stitch_msg.jsonify}")
            
            return True
            
        except Exception as e:
            self.log_test("Completion Messages", False, f"Failed: {e}")
            return False
    
    def test_message_receiving(self) -> bool:
        """Test receiving messages from Android."""
        print("\n8. Testing message receiving...")
        print("   Waiting for messages from Android (10 second timeout)...")
        
        received_messages = []
        start_time = time.time()
        timeout = 10
        
        while time.time() - start_time < timeout:
            try:
                message = self.android_link.recv()
                if message:
                    received_messages.append(message)
                    print(f"   ✓ Received: {message}")
                    
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(message)
                        print(f"      Parsed: category='{parsed.get('cat')}', value='{parsed.get('value')}'")
                    except json.JSONDecodeError:
                        print(f"      Raw message (not JSON): {message}")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ✗ Error receiving message: {e}")
                break
        
        if received_messages:
            self.log_test("Message Receiving", True, f"Received {len(received_messages)} messages")
        else:
            self.log_test("Message Receiving", False, "No messages received within timeout")
        
        return len(received_messages) > 0
    
    def continuous_message_scan(self, duration: int = 0):
        """
        Continuously scan for messages from Android tablet.
        
        Args:
            duration: Duration in seconds to scan (0 = infinite until Ctrl+C)
        """
        print(f"\n=== Continuous Message Scanning ===")
        if duration > 0:
            print(f"Scanning for {duration} seconds...")
        else:
            print("Scanning continuously (Press Ctrl+C to stop)...")
        
        print("Timestamp format: [HH:MM:SS]")
        print("-" * 50)
        
        received_count = 0
        start_time = time.time()
        
        try:
            while True:
                try:
                    message = self.android_link.recv()
                    if message:
                        received_count += 1
                        timestamp = time.strftime("%H:%M:%S", time.localtime())
                        print(f"[{timestamp}] Message #{received_count}: {message}")
                        
                        # Try to parse as JSON
                        try:
                            parsed = json.loads(message)
                            print(f"[{timestamp}]   Category: {parsed.get('cat')}")
                            print(f"[{timestamp}]   Value: {parsed.get('value')}")
                        except json.JSONDecodeError:
                            print(f"[{timestamp}]   Raw message (not JSON)")
                        
                        print("-" * 50)
                    
                    # Check if duration limit reached
                    if duration > 0 and (time.time() - start_time) >= duration:
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
        """Test connection stability with continuous messaging."""
        print("\n9. Testing connection stability...")
        print("   Sending continuous messages for 10 seconds...")
        
        try:
            start_time = time.time()
            message_count = 0
            
            while time.time() - start_time < 10:
                ping_msg = AndroidMessage("info", f"stability_test_{message_count}")
                self.android_link.send(ping_msg)
                message_count += 1
                time.sleep(1)  # Send every second
            
            self.log_test("Connection Stability", True, f"Sent {message_count} messages successfully")
            return True
            
        except Exception as e:
            self.log_test("Connection Stability", False, f"Failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Android."""
        print("\n10. Cleaning up connection...")
        try:
            self.android_link.disconnect()
            self.log_test("Disconnection", True, "Connection closed successfully")
        except Exception as e:
            self.log_test("Disconnection", False, f"Error during cleanup: {e}")
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success."""
        print("=== Android Message Test Suite (Based on task1.py) ===\n")
        
        # Connect first
        if not self.connect():
            return False
        
        # Run all test categories
        tests = [
            self.test_initialization_messages,
            self.test_obstacle_messages,
            self.test_control_messages,
            self.test_location_messages,
            self.test_image_recognition_messages,
            self.test_completion_messages,
            self.test_message_receiving,
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
    
    parser = argparse.ArgumentParser(description='Android Message Test Script')
    parser.add_argument('--scan', action='store_true', 
                       help='Run continuous message scanning mode')
    parser.add_argument('--duration', type=int, default=0,
                       help='Duration for scanning in seconds (0 = infinite)')
    parser.add_argument('--test-only', action='store_true',
                       help='Run only the test suite without scanning')
    
    args = parser.parse_args()
    
    tester = AndroidMessageTester()
    
    if args.scan:
        # Continuous scanning mode
        print("Starting continuous Android message scanning...\n")
        
        if not tester.connect():
            print("Failed to establish connection. Exiting.")
            return
        
        try:
            tester.continuous_message_scan(duration=args.duration)
        finally:
            tester.disconnect()
            
    elif args.test_only:
        # Test suite only
        print("Starting comprehensive Android message test based on task1.py...\n")
        success = tester.run_all_tests()
        print(f"\nTest script completed. Overall result: {'SUCCESS' if success else 'FAILURE'}")
        
    else:
        # Default: Run tests then offer scanning
        print("Starting comprehensive Android message test based on task1.py...\n")
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
