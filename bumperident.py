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

        self.safe_distance = 0.4  # Distancia para evitar obstáculos
        self.is_moving_forward = False
        self.is_turning = False

        self.left_turn_attempts = 0
        self.right_turn_attempts = 0
        self.max_turn_attempts = 2

        # Asegura rigidez inicial
        self.motion.setStiffnesses("Body", 0.8)

        self.subscribe_to_events()
        self.start_moving_forward()

    def subscribe_to_events(self):
        memory.subscribeToEvent("SonarLeftDetected", "SonarHandler", "onSonarLeftDetected")
        memory.subscribeToEvent("SonarRightDetected", "SonarHandler", "onSonarRightDetected")
        memory.subscribeToEvent("SonarLeftNothingDetected", "SonarHandler", "onSonarNothingDetected")
        memory.subscribeToEvent("SonarRightNothingDetected", "SonarHandler", "onSonarNothingDetected")
        memory.subscribeToEvent("FootContactChanged", "SonarHandler", "onFootBumperPressed")

    def unsubscribe_from_events(self):
        memory.unsubscribeToEvent("SonarLeftDetected", "SonarHandler")
        memory.unsubscribeToEvent("SonarRightDetected", "SonarHandler")
        memory.unsubscribeToEvent("SonarLeftNothingDetected", "SonarHandler")
        memory.unsubscribeToEvent("SonarRightNothingDetected", "SonarHandler")
        memory.unsubscribeToEvent("FootContactChanged", "SonarHandler")

    def start_moving_forward(self):
        if not self.is_moving_forward and not self.motion.moveIsActive() and not self.is_turning:
            print("Starting to move forward...")
            self.motion.moveInit()
            self.motion.move(0.03, 0, 0)  # Velocidad reducida
            self.is_moving_forward = True

    def stop_moving_forward(self):
        if self.is_moving_forward:
            print("Stopping forward movement...")
            self.motion.stopMove()
            self.is_moving_forward = False
            time.sleep(0.5)  # Pausa para estabilizar el robot

    def move_laterally(self, direction):
        if self.is_turning or self.is_moving_forward:  # Evitar giros si está moviéndose hacia adelante o girando
            return

        print("Turning to the {}.".format(direction))
        self.is_turning = True
        self.stop_moving_forward()

        if direction == 'left':
            self.motion.moveTo(0, 0, 0.4)  # Giros más pequeños
            self.left_turn_attempts += 1
        elif direction == 'right':
            self.motion.moveTo(0, 0, -0.4)
            self.right_turn_attempts += 1

        time.sleep(0.5)  
        self.is_turning = False

    def reset_turn_attempts(self):
        self.left_turn_attempts = 0
        self.right_turn_attempts = 0

    def onSonarLeftDetected(self, *_args):
        print("Left sonar detected an object.")
        left_distance = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
        print(f"Left sonar distance: {left_distance}")

        if left_distance < self.safe_distance and not self.is_turning:
            self.stop_moving_forward()
            if self.left_turn_attempts < self.max_turn_attempts:
                self.move_laterally('right')
            else:
                self.move_laterally('left')

    def onSonarRightDetected(self, *_args):
        print("Right sonar detected an object.")
        right_distance = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
        print(f"Right sonar distance: {right_distance}")

        if right_distance < self.safe_distance and not self.is_turning:
            self.stop_moving_forward()
            if self.right_turn_attempts < self.max_turn_attempts:
                self.move_laterally('left')
            else:
                self.move_laterally('right')

    def onSonarNothingDetected(self, *_args):
        if not self.is_turning and not self.is_moving_forward:
            print("No obstacles detected by sonar, resuming forward movement.")
            self.start_moving_forward()
            self.reset_turn_attempts()

    def onFootBumperPressed(self, event_name, value, *_args):
        # Manejo de impacto con bumpers
        print("Foot bumper detected an impact. Stopping movement.")
        self.stop_moving_forward()

        left_pressed, right_pressed = value
        if left_pressed:
            print("Left bumper pressed.")
        if right_pressed:
            print("Right bumper pressed.")

        time.sleep(1.5)  
        print("Resubscribing to sonar events.")
        self.subscribe_to_events()

def main():
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, NAO_IP, 9559)
    global SonarHandler
    SonarHandler = SonarHandlerModule("SonarHandler")

    try:
        while True:
            time.sleep(0.1) 
    except KeyboardInterrupt:
        print("Keyboard Interruption")
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
