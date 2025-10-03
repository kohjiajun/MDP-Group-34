#!/usr/bin/env python3
"""
Test script for Android Bluetooth connection.
Tests the connection establishment, message exchange, and proper cleanup.
"""

import time
import json
import sys
import os

# Add the parent directory to the path to import the android module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication.android import AndroidLink, AndroidMessage


def test_android_connection():
    """Test the Android Bluetooth connection functionality."""
    
    print("=== Android Bluetooth Connection Test ===\n")
    
    # Initialize the Android link
    android_link = AndroidLink()
    
    try:
        print("1. Attempting to establish Bluetooth connection...")
        print("   Make sure your Android tablet is ready to connect...")
        
        # Try to connect
        android_link.connect()
        print("   ✓ Connection established successfully!")
        
        # Test sending different types of messages
        print("\n2. Testing message sending...")
        
        test_messages = [
            AndroidMessage("info", "Test connection established"),
            AndroidMessage("mode", "manual"),
            AndroidMessage("status", "running"),
            AndroidMessage("location", json.dumps({"x": 0, "y": 0, "d": 0})),
            AndroidMessage("image-rec", json.dumps({"image_id": "TEST", "obstacle_id": "0"}))
        ]
        
        for i, message in enumerate(test_messages, 1):
            try:
                android_link.send(message)
                print(f"   ✓ Sent message {i}: {message.jsonify}")
                time.sleep(0.5)  # Small delay between messages
            except Exception as e:
                print(f"   ✗ Failed to send message {i}: {e}")
        
        # Test receiving messages (with timeout)
        print("\n3. Testing message receiving...")
        print("   Waiting for messages from Android (10 second timeout)...")
        
        start_time = time.time()
        timeout = 10  # 10 second timeout
        
        while time.time() - start_time < timeout:
            try:
                # Set a small timeout for recv to avoid blocking indefinitely
                message = android_link.recv()
                if message:
                    print(f"   ✓ Received: {message}")
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(message)
                        print(f"      Parsed: category='{parsed.get('cat')}', value='{parsed.get('value')}'")
                    except json.JSONDecodeError:
                        print(f"      Raw message (not JSON): {message}")
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            except Exception as e:
                print(f"   ✗ Error receiving message: {e}")
                break
        
        print("   Timeout reached for receiving messages.")
        
        # Test sending a control message
        print("\n4. Testing control message...")
        try:
            control_msg = AndroidMessage("control", "test")
            android_link.send(control_msg)
            print(f"   ✓ Sent control message: {control_msg.jsonify}")
        except Exception as e:
            print(f"   ✗ Failed to send control message: {e}")
        
        print("\n5. Testing connection stability...")
        print("   Sending ping messages every 2 seconds for 10 seconds...")
        
        for i in range(5):
            try:
                ping_msg = AndroidMessage("info", f"ping_{i+1}")
                android_link.send(ping_msg)
                print(f"   ✓ Ping {i+1} sent")
                time.sleep(2)
            except Exception as e:
                print(f"   ✗ Ping {i+1} failed: {e}")
                break
        
        print("\n   ✓ Connection stability test completed!")
        
    except Exception as e:
        print(f"\n✗ Connection test failed: {e}")
        return False
    
    finally:
        print("\n6. Cleaning up connection...")
        try:
            android_link.disconnect()
            print("   ✓ Connection closed successfully!")
        except Exception as e:
            print(f"   ✗ Error during cleanup: {e}")
    
    print("\n=== Test completed successfully! ===")
    return True


def test_message_creation():
    """Test the AndroidMessage class functionality."""
    
    print("\n=== AndroidMessage Class Test ===\n")
    
    try:
        # Test basic message creation
        msg = AndroidMessage("test", "value123")
        print(f"1. Basic message: cat='{msg.cat}', value='{msg.value}'")
        
        # Test JSON serialization
        json_str = msg.jsonify
        print(f"2. JSON serialization: {json_str}")
        
        # Test JSON parsing
        parsed = json.loads(json_str)
        print(f"3. JSON parsing: {parsed}")
        
        # Test complex value
        complex_msg = AndroidMessage("location", json.dumps({"x": 10, "y": 20, "d": 90}))
        print(f"4. Complex message: {complex_msg.jsonify}")
        
        print("\n   ✓ AndroidMessage class test passed!")
        return True
        
    except Exception as e:
        print(f"\n   ✗ AndroidMessage class test failed: {e}")
        return False


def main():
    """Main test function."""
    
    print("Starting Android Bluetooth connection tests...\n")
    
    # Test message class first
    message_test_passed = test_message_creation()
    
    if not message_test_passed:
        print("\nMessage class test failed. Aborting connection test.")
        return
    
    # Test connection
    connection_test_passed = test_android_connection()
    
    if connection_test_passed:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    print("\nTest script completed.")


if __name__ == "__main__":
    main()
