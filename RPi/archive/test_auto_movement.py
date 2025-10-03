#!/usr/bin/env python3
"""
Test script for autonomous movement functionality.
Tests the basic movement and detection logic without hardware.
"""

import time
from logger import prepare_logger


class MockSTMLink:
    """
    Mock STM32 link for testing without hardware.
    """
    
    def __init__(self):
        self.logger = prepare_logger()
        self.connected = False
        self.last_command = None
    
    def connect(self):
        self.connected = True
        self.logger.info("MOCK: Connected to STM32")
    
    def disconnect(self):
        self.connected = False
        self.logger.info("MOCK: Disconnected from STM32")
    
    def send(self, command):
        self.last_command = command
        self.logger.info(f"MOCK: Sent command to STM32: {command}")


def test_basic_auto_movement():
    """
    Test the basic autonomous movement logic.
    """
    logger = prepare_logger()
    stm_link = MockSTMLink()
    
    try:
        # Connect to mock STM32
        stm_link.connect()
        logger.info("Starting test autonomous movement...")
        
        # Start moving forward
        logger.info("Starting robot movement - moving forward")
        stm_link.send("00FW--")  # Move forward indefinitely
        
        # Dummy object detection loop
        logger.info("Starting object detection...")
        
        # DUMMY DETECTION LOGIC - Test different scenarios
        for i in range(5):  # Check 5 times
            logger.info(f"Checking for object... (attempt {i+1}/5)")
            
            # Test different dummy detection scenarios
            if i == 2:  # Detect object on 3rd check
                logger.info("DUMMY: Object detected on 3rd check!")
                break
            
            # Simulate other detection methods
            # distance = 25  # Simulate distance sensor reading
            # if distance < 30:
            #     logger.info("DUMMY: Object detected by distance sensor!")
            #     break
            
            time.sleep(0.5)  # Shorter delay for testing
        
        # Stop the robot
        logger.info("Stopping robot...")
        stm_link.send("00STOP")
        logger.info("Robot stopped")
        
        # Verify the commands were sent
        logger.info(f"Last command sent: {stm_link.last_command}")
        
    except Exception as e:
        logger.error(f"Test error: {e}")
    finally:
        stm_link.disconnect()
        logger.info("Test completed")


def test_detection_scenarios():
    """
    Test different object detection scenarios.
    """
    logger = prepare_logger()
    
    scenarios = [
        ("Time-based detection", lambda i: i >= 2),
        ("Random detection", lambda i: i == 1),
        ("Distance-based detection", lambda i: i == 3),
        ("No detection", lambda i: False)
    ]
    
    for scenario_name, detection_func in scenarios:
        logger.info(f"\n--- Testing {scenario_name} ---")
        
        for i in range(5):
            if detection_func(i):
                logger.info(f"Check {i+1}: Object detected!")
                break
            else:
                logger.info(f"Check {i+1}: No object")
        
        logger.info(f"{scenario_name} test completed")


if __name__ == "__main__":
    print("Testing Autonomous Movement Logic")
    print("This test runs without hardware - just tests the logic")
    print("=" * 50)
    
    # Test basic movement
    print("\n1. Testing basic autonomous movement...")
    test_basic_auto_movement()
    
    # Test detection scenarios
    print("\n2. Testing different detection scenarios...")
    test_detection_scenarios()
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("\nTo run with real hardware:")
    print("python3 basic_auto.py")
    print("python3 simple_auto_movement.py")
    print("python3 auto_movement.py")
