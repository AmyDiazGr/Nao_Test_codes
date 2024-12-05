from naoqi import ALProxy
import time
motion = ALProxy("ALMotion", "169.254.90.104", 9559)
motion.setStiffnesses("Body", 1.0) #Con rigidez en 1.0 se activan todos los motores 

time.sleep(10)#Realiza la accion por 10s 

motion.setStiffnesses("Body", 0.0)#Rigidez a 0.0 se desactivan todos los motores

