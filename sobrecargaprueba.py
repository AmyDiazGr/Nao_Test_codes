import sys
import time
from naoqi import ALProxy, ALBroker, ALModule

NAO_IP = "10.42.0.134"
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

        self.safe_distance = 0.6
        self.is_moving_forward = False
        self.is_turning = False
        self.move_delay = 5

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

    def unsubscribe_from_events(self):
        memory.unsubscribeToEvent("SonarLeftDetected", "SonarHandler")
        memory.unsubscribeToEvent("SonarRightDetected", "SonarHandler")
        memory.unsubscribeToEvent("SonarLeftNothingDetected", "SonarHandler")
        memory.unsubscribeToEvent("SonarRightNothingDetected", "SonarHandler")

    def start_moving_forward(self):
        if not self.is_moving_forward and not self.motion.moveIsActive():
            print("Starting to move forward...")
            self.motion.moveInit()
            time.sleep(0.5)
            self.motion.move(0.05, 0, 0)
            self.is_moving_forward = True

    def stop_moving_forward(self):
        if self.is_moving_forward:
            print("Stopping forward movement...")
            self.motion.stopMove()
            self.is_moving_forward = False

    def move_laterally(self, direction):
        if self.motion.moveIsActive():
            self.motion.stopMove()
        print("Turning to the {}.".format(direction))
        self.unsubscribe_from_events()
        self.motion.moveInit()

        if direction == 'left':
            self.motion.moveTo(0, 0, 1)
            self.left_turn_attempts += 1
        elif direction == 'right':
            self.motion.moveTo(0, 0, -1)
            self.right_turn_attempts += 1

        self.motion.waitUntilMoveIsFinished()
        time.sleep(0.5)
        self.is_turning = False
        self.subscribe_to_events()

    def reset_turn_attempts(self):
        self.left_turn_attempts = 0
        self.right_turn_attempts = 0

    def onSonarRightDetected(self, *_args):
        print("RightSonarDetected")
        distance = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
        print("Right sonar detected an object at distance: {:.2f} m".format(distance))

        if distance < self.safe_distance and not self.is_turning:
            self.stop_moving_forward()
            if self.right_turn_attempts < self.max_turn_attempts:
                self.move_laterally('left')
            else:
                self.move_laterally('right')

    def onSonarLeftDetected(self, *_args):
        print("LeftSonarDetected")
        distance = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
        print("Left sonar detected an object at distance: {:.2f} m".format(distance))

        if distance < self.safe_distance and not self.is_turning:
            self.stop_moving_forward()
            if self.left_turn_attempts < self.max_turn_attempts:
                self.move_laterally('right')
            else:
                self.move_laterally('left')

    def onSonarNothingDetected(self, *_args):
        if not self.is_turning and not self.is_moving_forward:
            print("No obstacles detected by sonar, resuming forward movement.")
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
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
