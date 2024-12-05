# -*- encoding: UTF-8 -*-
from naoqi import ALProxy
import time

def sonar_test(nao_ip, nao_port):
    # Crear un proxy para el módulo ALSonar
    sonarProxy = ALProxy("ALSonar", nao_ip, nao_port)
    
    # Crear un proxy para ALMemory (para leer los datos del sonar)
    memoryProxy = ALProxy("ALMemory", nao_ip, nao_port)
    
    # Activar los sensores de sonar
    sonarProxy.subscribe("SonarApp")

    print("Sonar activated. Reading values...")
    
    try:
        while(1):
        # for i in range(10):  # Leer datos durante un tiempo limitado
            # Leer la distancia detectada por el sonar izquierdo
            left_distance = memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
            # Leer la distancia detectada por el sonar derecho
            right_distance = memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
            
            # Comprobamos que los datos no sean None y que sean números
            if isinstance(left_distance, (int, float)) and isinstance(right_distance, (int, float)):
                print("Left Sonar Distance: {:.2f} m".format(left_distance))
                print("Right Sonar Distance: {:.2f} m".format(right_distance))
            else:
                print("Error: Invalid data received from sonar sensors.")
            
            time.sleep(1)  # Esperar un segundo entre lecturas
            
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    
    # Desactivar los sensores de sonar cuando se termine el test
    sonarProxy.unsubscribe("SonarApp")
    print("Sonar deactivated.")

def main():
    nao_ip = "10.42.0.134"  # Cambia a la IP de tu robot
    nao_port = 9559  # Puerto estándar

    sonar_test(nao_ip, nao_port)

if __name__ == "__main__":
    main()
