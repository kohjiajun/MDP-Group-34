#!/usr/bin/env python3
"""
Basic autonomous movement for robot car.
Simple implementation: move forward, detect object, stop.
"""

import time
from communication.stm32 import STMLink
from logger import prepare_logger


def main():
    """
    Main function for basic autonomous movement.
    """
    logger = prepare_logger()
    stm_link = STMLink()
    
    try:
        # Connect to STM32
        stm_link.connect()
        logger.info("Connected to STM32")
        
        # Start moving forward
        logger.info("Starting robot movement - moving forward")
        stm_link.send("00FW--")  # Move forward indefinitely
        
        # Dummy object detection loop
        logger.info("Starting object detection...")
        
        # DUMMY DETECTION LOGIC - Replace with your actual detection
        for i in range(10):  # Check 10 times
            logger.info(f"Checking for object... (attempt {i+1}/10)")
            
            # DUMMY IF STATEMENTS - Replace with your detection logic
            # Example 1: Time-based detection
            if i >= 3:  # After 3 checks (simulate 3 seconds)
                logger.info("DUMMY: Object detected after 3 seconds!")
                break
            
            # Example 2: Simulate sensor reading
            # distance = read_distance_sensor()  # Replace with actual sensor
            # if distance < 30:  # 30cm threshold
            #     logger.info("DUMMY: Object detected by distance sensor!")
            #     break
            
            # Example 3: Simulate camera detection
            # image = capture_image()
            # if detect_object_in_image(image):
            #     logger.info("DUMMY: Object detected by camera!")
            #     break
            
            # Example 4: Simulate random detection
            import random
            if random.random() < 0.3:  # 30% chance each check
                logger.info("DUMMY: Object detected randomly!")
                break
            
            time.sleep(1)  # Wait 1 second between checks
        
        # Stop the robot
        logger.info("Stopping robot...")
        stm_link.send("00STOP")
        logger.info("Robot stopped")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        stm_link.send("00STOP")
    except Exception as e:
        logger.error(f"Error: {e}")
        stm_link.send("00STOP")
    finally:
        stm_link.disconnect()
        logger.info("Program ended")


if __name__ == "__main__":
    print("Basic Autonomous Movement Program")
    print("Robot will move forward and stop when object is detected")
    print("Using dummy detection logic - replace with real detection")
    print("Press Ctrl+C to exit\n")
    
    main()
