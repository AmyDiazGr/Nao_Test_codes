from naoqi import ALProxy
import time 

motion = ALProxy("ALMotion", "10.42.0.134", 9559)
# motion.setStiffnesses("Body", 1.0)#Poner la rigidez a 1.0 para activiar los moteres
motion.moveInit()
motion.moveTo(0.1, 0, 0) 
###### moveTo(dist,desl,ang )#####

# dist = distancia hacia adelante (m)
# desl = desplazamiento lateral (para izq numeros + y para derecho numeros -) (m)
# ang = angulo de rotacion(rad)

# time.sleep(2)

# motion.stopMove()
