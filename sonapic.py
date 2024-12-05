import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

NAO_IP = "10.42.0.134"

SonarHandler = None
memory = None

class SonarHandlerModule(ALModule):
    def __init__(self,name):
        ALModule.__init__(self,name)

        self.motion = ALProxy("ALMotion")
        global memory
        memory = ALProxy("ALMemory")
        sonarProxy = ALProxy("ALSonar")
        sonarProxy.subscribe("SonarApp")
        print("Sonar activated. Reading values...")

        #SonarDetected event subscription
        memory.subscribeToEvent("SonarLeftDetected",
                                "SonarHandler","onSonarLeftDetected")
        memory.subscribeToEvent("SonarRightDetected",
                                "SonarHandler","onSonarRightDetected")
        
        #SonarNothingDetected event subscription
        memory.subscribeToEvent("SonarLeftNothingDetected",
                                "SonarHandler","onSonarLeftNothingDetected")
        memory.subscribeToEvent("SonarRightNothingDetected",
                                "SonarHandler","onSonarRightNothingDetected")
    
    def onSonarRightDetected(self, *_args):
        print("RightSonarDetected")
        memory.unsubscribeToEvent("SonarRightDetected","SonarHandler")
        self.motion.stopMove()
        self.motion.moveTo(0,0,0.5)
        memory.subscribeToEvent("SonarRightDetected","SonarHandler")
        
    def onSonarLeftDetected(self, *_args):
        print("LeftSonarDetected")
        memory.unsubscribeToEvent("SonarLeftDetected","SonarHandler")
        self.motion.stopMove()
        self.motion.moveTo(0,0,-0.5)
        memory.subscribeToEvent("SonarLeftDetected","SonarHandler")

    def onSonarRightNothingDetected(self, *_args):
        print("RightSonarNothingDetected")
        memory.unsubscribeToEvent("SonarRightNothingDetected","SonarHandler")
        self.motion.stopMove()
        self.motion.moveTo(0.1,0,0)
        memory.subscribeToEvent("SonarRightNothingDetected","SonarHandler")
    
    def onSonarLeftNothingDetected(self, *_args):
        print("LeftSonarNothingDetected")
        memory.unsubscribeToEvent("SonarLeftNothingDetected","SonarHandler")
        self.motion.stopMove()
        self.motion.moveTo(0.1,0,0)
        memory.subscribeToEvent("SonarLeftNothingDetected","SonarHandler")


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
