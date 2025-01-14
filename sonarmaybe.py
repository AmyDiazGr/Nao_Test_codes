import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

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
        self.move_delay = 2



        memory.subscribeToEvent("SonarLeftDetected", "SonarHandler", "onSonarLeftDetected")
        memory.subscribeToEvent("SonarRightDetected", "SonarHandler", "onSonarRightDetected")
     	memory.subscribeToEvent("SonarLeftNothingDetected", "SonarHandler", "onSonarNothingDetected")
        memory.subscribeToEvent("SonarRightNothingDetected", "SonarHandler", "onSonarNothingDetected")


        self.start_moving_forward()

    def start_moving_forward(self):
        if not self.is_moving_forward:
            print("Starting to move forward...")
            self.motion.moveInit()
            self.motion.move(0.1, 0, 0)
            self.is_moving_forward = True

    def stop_moving_forward(self):
        if self.is_moving_forward:
            print("Stopping forward movement...")
            self.motion.stopMove()
            self.is_moving_forward = False
            
    def move_laterally(self, direction):
        print("Turning to the {}.".format(direction))
        self.motion.moveInit()

        if direction == 'left':
            self.motion.moveTo(0, 0, 0.5)
        elif direction == 'right':
            self.motion.moveTo(0, 0, -0.5)

        self.motion.waitUntilMoveIsFinished()
        self.is_turning = True
        time.sleep(self.move_delay)
        self.is_turning = False


    def onSonarRightDetected(self, *_args):
    print("RightSonarDetected")
    distance = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
    print("Right sonar detected an object at distance: {:.2f} m".format(distance))

    if distance < self.safe_distance and not self.is_turning:
        self.stop_moving_forward()
        self.move_laterally('left')
            
    def onSonarLeftDetected(self, *_args):
    print("LeftSonarDetected")
    distance = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
    print("Left sonar detected an object at distance: {:.2f} m".format(distance))

    if distance < self.safe_distance and not self.is_turning:
        self.stop_moving_forward()
        self.move_laterally('right')

    def onSonarNothingDetected(self, *_args):
        print("No obstacles detected by sonar, resuming forward movement.")
        self.start_moving_forward()

def main():
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, NAO_IP, 9559)
    global SonarHandler
    SonarHandler = SonarHandlerModule("SonarHandler")
    
def onSonarNothingDetected(self, *_args):
    print("No obstacles detected by sonar, resuming forward movement.")
    self.start_moving_forward()

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




            





