#!/usr/bin/env python3
"""
Simple script to continuously scan for messages from Android tablet.
This is a lightweight version focused only on message scanning.
"""

import json
import time
import sys
import os
import signal

# Add the parent directory to the path to import the android module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from communication.android import AndroidLink


class AndroidMessageScanner:
    """Simple Android message scanner."""
    
    def __init__(self):
        self.android_link = AndroidLink()
        self.running = True
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals for graceful shutdown."""
        print(f"\n[{time.strftime('%H:%M:%S')}] Received signal {signum}. Stopping scanner...")
        self.running = False
    
    def connect(self) -> bool:
        """Establish connection to Android."""
        try:
            print("Establishing Bluetooth connection...")
            print("Make sure your Android tablet is ready to connect...")
            self.android_link.connect()
            print("✓ Connection established successfully!")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def scan_messages(self, duration: int = 0):
        """
        Continuously scan for messages from Android tablet.
        
        Args:
            duration: Duration in seconds to scan (0 = infinite until Ctrl+C)
        """
        print(f"\n=== Android Message Scanner ===")
        if duration > 0:
            print(f"Scanning for {duration} seconds...")
        else:
            print("Scanning continuously (Press Ctrl+C to stop)...")
        
        print("Timestamp format: [HH:MM:SS]")
        print("Message format: [timestamp] Message #N: content")
        print("-" * 60)
        
        received_count = 0
        start_time = time.time()
        
        try:
            while self.running:
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
                            
                            # Special handling for different message types
                            if parsed.get('cat') == 'obstacles':
                                print(f"[{timestamp}]   → Obstacle data received")
                            elif parsed.get('cat') == 'control':
                                print(f"[{timestamp}]   → Control command: {parsed.get('value')}")
                            elif parsed.get('cat') == 'location':
                                print(f"[{timestamp}]   → Location update")
                                
                        except json.JSONDecodeError:
                            print(f"[{timestamp}]   Raw message (not JSON)")
                        
                        print("-" * 60)
                    
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
    
    def disconnect(self):
        """Disconnect from Android."""
        try:
            print(f"\n[{time.strftime('%H:%M:%S')}] Disconnecting...")
            self.android_link.disconnect()
            print("✓ Connection closed successfully")
        except Exception as e:
            print(f"✗ Error during cleanup: {e}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Android Message Scanner')
    parser.add_argument('--duration', type=int, default=0,
                       help='Duration for scanning in seconds (0 = infinite)')
    parser.add_argument('--help-usage', action='store_true',
                       help='Show usage examples')
    
    args = parser.parse_args()
    
    if args.help_usage:
        print("Usage Examples:")
        print("  python3 scan_android_messages.py                    # Scan indefinitely")
        print("  python3 scan_android_messages.py --duration 60      # Scan for 60 seconds")
        print("  python3 scan_android_messages.py --duration 300     # Scan for 5 minutes")
        return
    
    scanner = AndroidMessageScanner()
    
    try:
        if not scanner.connect():
            print("Failed to establish connection. Exiting.")
            return
        
        scanner.scan_messages(duration=args.duration)
        
    finally:
        scanner.disconnect()


if __name__ == "__main__":
    main()
