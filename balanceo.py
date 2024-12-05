import sys
import time

from naoqi import ALProxy, ALBroker, ALModule

NAO_IP = "localhost"
SonarHandler = None
memory = None

class SonarHandlerModule(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)

        self.motion = ALProxy("ALMotion")
        global memory
        memory = ALProxy("ALMemory")
        sonarProxy = ALProxy("ALSonar")
        sonarProxy.subscribe("SonarApp")
        print("Sonar activated. Reading values...")

        self.safe_distance = 0.5
        self.is_moving_forward = False
        self.is_turning = False

        self.left_turn_attempts = 0
        self.right_turn_attempts = 0
        self.max_turn_attempts = 1

        self.subscribe_to_events()
        self.start_moving_forward()

    def subscribe_to_events(self):
        memory.subscribeToEvent("SonarLeftDetected", "SonarHandler", "onSonarLeftDetected")
        memory.subscribeToEvent("SonarRightDetected", "SonarHandler", "onSonarRightDetected")
        memory.subscribeToEvent("SonarLeftNothingDetected", "SonarHandler", "onSonarNothingDetected")
        memory.subscribeToEvent("SonarRightNothingDetected", "SonarHandler", "onSonarNothingDetected")

    def stop_sonar_events(self):
        memory.unsubscribeToEvent("SonarLeftDetected", "SonarHandler")
        memory.unsubscribeToEvent("SonarRightDetected", "SonarHandler")
        memory.unsubscribeToEvent("SonarLeftNothingDetected", "SonarHandler")
        memory.unsubscribeToEvent("SonarRightNothingDetected", "SonarHandler")

    def resume_sonar_events(self):
        self.subscribe_to_events()

    def start_moving_forward(self):
        if not self.is_moving_forward:
            print("Starting to move forward...")
            self.motion.moveInit()
            self.motion.moveToward(0.5, 0, -0.02)  
            self.is_moving_forward = True

    def stop_moving_forward(self):
        if self.is_moving_forward:
            print("Stopping forward movement...")
            self.motion.stopMove()
            self.motion.waitUntilMoveIsFinished()  
            self.is_moving_forward = False


    def move_laterally(self, direction):

        print("Turning to the {}.".format(direction))
        self.motion.moveInit()
        self.is_turning = True

        if direction == 'left':
            self.motion.moveTo(0, 0, 0.7)  
        elif direction == 'right':
            self.motion.moveTo(0, 0, -0.7)  

        self.motion.waitUntilMoveIsFinished()
        time.sleep(2)
        self.is_turning = False


    def reset_turn_attempts(self):
        self.left_turn_attempts = 0
        self.right_turn_attempts = 0

    def onSonarRightDetected(self, *_args):
        print("RightSonarDetected")
        distance = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
        print("Right sonar detected an object at distance: {}". format(distance))

        if distance < self.safe_distance and not self.is_turning:
            self.stop_moving_forward()
            if self.right_turn_attempts < self.max_turn_attempts:
                self.move_laterally('left')
                self.left_turn_attempts += 1
            else:
                self.move_laterally('right')
                self.right_turn_attempts += 1

    def onSonarLeftDetected(self, *_args):
        print("LeftSonarDetected")
        distance = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
        print("Left sonar detected an object at distance: {}".format(distance))

        if distance < self.safe_distance and not self.is_turning:
            self.stop_moving_forward()
            if self.left_turn_attempts < self.max_turn_attempts:
                self.move_laterally('right')
                self.right_turn_attempts += 1
            else:
                self.move_laterally('left')
                self.left_turn_attempts += 1

    def onSonarNothingDetected(self, *_args):
        print("No obstacles detected by sonar, resuming forward movement.")
        self.resume_sonar_events()
        self.start_moving_forward()
        self.reset_turn_attempts()


def main():
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, NAO_IP, 9559)
    global SonarHandler
    SonarHandler = SonarHandlerModule("SonarHandler")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print("Keyboard Interruption")
        SonarHandler.stop_moving_forward()
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
