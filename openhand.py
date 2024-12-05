import sys
from naoqi import ALProxy 

def main(robotIP):
    PORT=9559

    try : 
        motionProxy = ALProxy("ALMotion", robotIP,PORT)
    except Exception,e:
        print "No se pudo crear proxy a ALMotion"
        print "Error was: ",e
        sys.exit(1)

    motionProxy.openHand('LHand')

if __name__ == "__main__":
    robotIp = "10.42.0.134"

    if len(sys.argv) <=1:
        print"dunno"
    else:
        robotIp = sys.argv[1]
    
    main(robotIp)
