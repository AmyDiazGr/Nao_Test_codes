import sys
import time
import cv2
import numpy as np
from naoqi import ALProxy, ALBroker, ALModule

NAO_IP = "localhost"
SonarHandler = None
memory = None
cameraProxy = None

class SonarHandlerModule(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)

        try:
            self.motion = ALProxy("ALMotion")
            global memory
            memory = ALProxy("ALMemory")
            global cameraProxy
            cameraProxy = ALProxy("ALVideoDevice")

            sonarProxy = ALProxy("ALSonar")
            sonarProxy.subscribe("SonarApp")
            print("Sonar and camera activated. Reading values...")

            self.safe_distance = 0.5
            self.is_moving_forward = False
            self.is_turning = False
            self.turning_direction = 'left' 

            self.subscribe_to_events()
            self.start_moving_forward()

        except Exception as e:
            print("Error initializing proxies: {}".format(e))
            sys.exit(1)

    def subscribe_to_events(self):
        try:
            memory.subscribeToEvent("SonarLeftDetected", "SonarHandler", "onSonarLeftDetected")
            memory.subscribeToEvent("SonarRightDetected", "SonarHandler", "onSonarRightDetected")
            memory.subscribeToEvent("SonarLeftNothingDetected", "SonarHandler", "onSonarNothingDetected")
            memory.subscribeToEvent("SonarRightNothingDetected", "SonarHandler", "onSonarNothingDetected")
        except Exception as e:
            print("Error subscribing to events: {}".format(e))

    def stop_sonar_events(self):
        try:
            memory.unsubscribeToEvent("SonarLeftDetected", "SonarHandler")
            memory.unsubscribeToEvent("SonarRightDetected", "SonarHandler")
            memory.unsubscribeToEvent("SonarLeftNothingDetected", "SonarHandler")
            memory.unsubscribeToEvent("SonarRightNothingDetected", "SonarHandler")
        except Exception as e:
            print("Error unsubscribing from events: {}".format(e))

    def start_moving_forward(self):
        try:
            if not self.is_moving_forward:
                print("Starting to move forward...")
                self.motion.moveInit()
                self.motion.moveToward(0.5, 0, 0)  
                self.is_moving_forward = True
        except Exception as e:
            print("Error starting forward movement: {}".format(e))

    def stop_moving_forward(self):
        try:
            if self.is_moving_forward:
                print("Stopping forward movement...")
                self.motion.stopMove()
                self.motion.waitUntilMoveIsFinished()
                self.is_moving_forward = False
        except Exception as e:
            print("Error stopping forward movement: {}".format(e))

    def move_laterally(self, direction):
        try:
            print("Turning to the {}.".format(direction))
            self.motion.moveInit()
            self.is_turning = True

            if direction == 'left':
                self.motion.moveTo(0, 0, 0.6)
            elif direction == 'right':
                self.motion.moveTo(0, 0, -0.6)

            self.motion.waitUntilMoveIsFinished()
            time.sleep(1)  
            self.is_turning = False
        except Exception as e:
            print("Error turning {}: {}".format(direction)(e))

    def onSonarRightDetected(self, *_args):
        print("RightSonarDetected")
        try:
            distance = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
            print("Right sonar detected an object at distance: {}".format(distance))
            if distance < self.safe_distance and not self.is_turning:
                self.stop_moving_forward()
                self.move_laterally('left')  
                self.turning_direction = 'left'  
        except Exception as e:
            print("Error handling right sonar detection: {}".format(e))

    def onSonarLeftDetected(self, *_args):
        print("LeftSonarDetected")
        try:
            distance = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
            print("Left sonar detected an object at distance: {}".format(distance))
            if distance < self.safe_distance and not self.is_turning:
                self.stop_moving_forward()
                self.move_laterally('right')  
                self.turning_direction = 'right'  
        except Exception as e:
            print("Error handling left sonar detection: {}".format(e))

    def onSonarNothingDetected(self, *_args):
        print("No obstacles detected by sonar, checking camera for lines...")
        try:
            self.process_image()
            if self.is_clear_path():
                print("Path is clear, resuming forward movement.")
                self.start_moving_forward()
            else:
                print("Obstacle detected by camera, continuing to turn.")
                self.move_laterally(self.turning_direction)
        except Exception as e:
            print("Error handling sonar nothing detected: {}",format(e))

    def process_image(self):
        try:
            resolution = 2
            colorSpace = 13
            video = cameraProxy.getImageRemote(cameraProxy.subscribe("CameraBottom", resolution, colorSpace, 5))

            if video is None:
                return

            image = np.frombuffer(video[6], dtype=np.uint8)
            image = image.reshape((video[1], video[0], 3))
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_image, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

            if lines is not None and len(lines) > 4:
                print("Detected {} lines. Obstacle detected.".format(len(lines)))
                self.stop_moving_forward()
        except Exception as e:
            print("Error processing image: {}".format(e))

    def is_clear_path(self):
        try:
            right_distance = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
            left_distance = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
            return right_distance > self.safe_distance and left_distance > self.safe_distance
        except Exception as e:
            print("Error checking clear path: {}".format(e))
            return False

def main():
    try:
        myBroker = ALBroker("myBroker", "0.0.0.0", 0, NAO_IP, 9559)
        global SonarHandler
        SonarHandler = SonarHandlerModule("SonarHandler")

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard Interruption")
        if SonarHandler:
            SonarHandler.stop_moving_forward()
        sys.exit(0)
    except Exception as e:
        print("Error in main: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
