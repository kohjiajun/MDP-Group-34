#!/usr/bin/env python3
"""
Simple test script for Android Bluetooth connection.
Basic connection test without complex message handling.
"""

import time
import sys
import os

# Add the parent directory to the path to import the android module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from communication.android import AndroidLink, AndroidMessage


def simple_connection_test():
    """Simple connection test for Android Bluetooth."""
    
    print("=== Simple Android Bluetooth Connection Test ===\n")
    
    # Initialize the Android link
    android_link = AndroidLink()
    
    try:
        print("1. Attempting to establish Bluetooth connection...")
        print("   Make sure your Android tablet is ready to connect...")
        print("   The RPi will be discoverable for Bluetooth pairing.")
        
        # Try to connect
        android_link.connect()
        print("   ✓ Connection established successfully!")
        
        # Send a simple test message
        print("\n2. Sending test message...")
        test_msg = AndroidMessage("info", "Hello from Raspberry Pi!")
        android_link.send(test_msg)
        print(f"   ✓ Sent: {test_msg.jsonify}")
        
        # Wait a bit and try to receive
        print("\n3. Waiting for response (5 seconds)...")
        start_time = time.time()
        
        while time.time() - start_time < 5:
            try:
                message = android_link.recv()
                if message:
                    print(f"   ✓ Received: {message}")
                    break
                time.sleep(0.1)
            except Exception as e:
                print(f"   ✗ Error receiving: {e}")
                break
        
        print("   Timeout reached.")
        
        # Send one more message
        print("\n4. Sending final message...")
        final_msg = AndroidMessage("status", "test_complete")
        android_link.send(final_msg)
        print(f"   ✓ Sent: {final_msg.jsonify}")
        
        print("\n   ✓ Basic connection test completed!")
        
    except Exception as e:
        print(f"\n✗ Connection test failed: {e}")
        print("   Make sure:")
        print("   - Bluetooth is enabled on the RPi")
        print("   - Android tablet is in pairing mode")
        print("   - No other Bluetooth connections are active")
        return False
    
    finally:
        print("\n5. Cleaning up connection...")
        try:
            android_link.disconnect()
            print("   ✓ Connection closed successfully!")
        except Exception as e:
            print(f"   ✗ Error during cleanup: {e}")
    
    print("\n=== Test completed! ===")
    return True


if __name__ == "__main__":
    print("Starting simple Android Bluetooth connection test...\n")
    
    success = simple_connection_test()
    
    if success:
        print("\n🎉 Connection test successful!")
    else:
        print("\n❌ Connection test failed.")
    
    print("\nTest script completed.")
