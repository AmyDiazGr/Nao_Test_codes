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
            self.initialize_head_position()


        except Exception as e:
            print("Error initializing proxies: {}".format(e))
            sys.exit(1)

    def subscribe_to_events(self):
        try:
            memory.subscribeToEvent("SonarLeftDetected", "SonarHandler", "onSonarLeftDetected")
            memory.subscribeToEvent("SonarRightDetected", "SonarHandler", "onSonarRightDetected")
        except Exception as e:
            print("Error subscribing to events: {}".format(e))

    def initialize_head_position(self):
        try:
            print("Initializing head position...")
            self.motion.setStiffnesses("Head", 1.0) 
            self.motion.setAngles(["HeadYaw", "HeadPitch"], [0.0, 0.0], 0.2) 
            time.sleep(0.5)  
        except Exception as e:
            print("Error initializing head position: {}".format(e))


    def start_moving_forward(self):
        try:
            if not self.is_moving_forward:
                print("Starting to move forward...")
                self.motion.moveInit()
                self.motion.moveToward(0.5, 0, -0.02) 
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

    def move_laterally(self):
        try:
            print("Turning to the {}.".format(self.turning_direction))
            self.motion.moveInit()
            self.is_turning = True

            if self.turning_direction == 'left':
                self.motion.moveTo(0, 0, 0.6)  
            elif self.turning_direction == 'right':
                self.motion.moveTo(0, 0, -0.6)  

            self.motion.waitUntilMoveIsFinished()
            time.sleep(1)  
            self.is_turning = False
        except Exception as e:
            print("Error turning: {}".format(e))

    def onSonarRightDetected(self, *_args):
        print("Obstacle detected by right sonar.")
        try:
            distance = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
            print("Right sonar detected an object at distance: {}".format(distance))
            if distance < self.safe_distance:
                self.stop_moving_forward()
                self.turning_direction = 'left' 
                self.avoid_obstacle()
        except Exception as e:
            print("Error handling right sonar detection: {}".format(e))

    def onSonarLeftDetected(self, *_args):
        print("Obstacle detected by left sonar.")
        try:
            distance = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
            print("Left sonar detected an object at distance: {}".format(distance))
            if distance < self.safe_distance:
                self.stop_moving_forward()
                self.turning_direction = 'right' 
                self.avoid_obstacle()
        except Exception as e:
            print("Error handling left sonar detection: {}".format(e))

    def avoid_obstacle(self):
        while not self.is_clear_path():
            print("Turning to find a clear path...")
            self.move_laterally()
            time.sleep(0.5)
        print("Path is clear. Resuming forward movement.")
        self.motion.stopMove()
        time.sleep(0.5)
        self.motion.waitUntilMoveIsFinished()
        time.sleep(0.5)
        self.start_moving_forward()

    def process_image(self):
        try:
            resolution = 2
            colorSpace = 13
            video = cameraProxy.getImageRemote(cameraProxy.subscribe("CameraBottom", resolution, colorSpace, 5))

            if video is None:
                return False

            image = np.frombuffer(video[6], dtype=np.uint8)
            image = image.reshape((video[1], video[0], 3))
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_image, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50)

            return lines is None or len(lines) <= 4
        except Exception as e:
            print("Error processing image: {}".format(e))
            return False

    def is_clear_path(self):
        try:
            right_distance = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
            left_distance = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
            camera_clear = self.process_image()

            path_clear = (
                right_distance > self.safe_distance
                and left_distance > self.safe_distance
                and camera_clear
            )

            print("Right distance: {}, Left distance: {}, Camera clear: {}".format(
                right_distance, left_distance, camera_clear))
            print("Path clear status: {}".format(path_clear))
            return path_clear
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
