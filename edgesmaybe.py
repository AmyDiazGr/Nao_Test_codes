import cv2
import numpy as np
from naoqi import ALProxy
import time

def detect_edges(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edges = cv2.Canny(blurred_image, 50, 150)
    edge_count = cv2.countNonZero(edges)
    return edges, edge_count

def main():
    robot_ip = "localhost"
    port = 9559
    try:
        video_proxy = ALProxy("ALVideoDevice", robot_ip, port)
    except Exception as e:
        print "No se pudo conectar al NAO en {0}:{1}. Error: {2}".format(robot_ip, port, e)
        return

    resolution = 2  
    color_space = 13
    fps = 30

    client_top = video_proxy.subscribeCamera("TopCamera", 0, resolution, color_space, fps)
    client_bottom = video_proxy.subscribeCamera("BottomCamera", 1, resolution, color_space, fps) 

    try:
        while True:
            top_result = video_proxy.getImageRemote(client_top)
            if top_result[0] is not None:
                top_image = bytearray(top_result[6])
                top_image = np.frombuffer(top_image, np.uint8).reshape((top_result[1], top_result[0], 3))
                edges, edge_count = detect_edges(top_image)
                print "Camara superior: Bordes detectados = {0}".format(edge_count)
                if edge_count > 1000: 
                    print "Objeto detectado en la cámara superior."
                else:
                    print "No se detectó objeto en la cámara superior."
                cv2.imwrite("edges_top.jpg", edges) 

            bottom_result = video_proxy.getImageRemote(client_bottom)
            if bottom_result[0] is not None:
                bottom_image = bytearray(bottom_result[6])
                bottom_image = np.frombuffer(bottom_image, np.uint8).reshape((bottom_result[1], bottom_result[0], 3))
                edges, edge_count = detect_edges(bottom_image)
                print "Camara inferior: Bordes detectados = {0}".format(edge_count)
                if edge_count > 1000:  # Ajusta este umbral según tus pruebas
                    print "Objeto detectado en la cámara inferior."
                else:
                    print "No se detectó objeto en la cámara inferior."
                cv2.imwrite("edges_bottom.jpg", edges)  # Guardar imagen de bordes para ver los resultados

            time.sleep(1)

    except KeyboardInterrupt:
        print "Interrupción manual del programa."
    finally:
        video_proxy.unsubscribe(client_top)
        video_proxy.unsubscribe(client_bottom)

if __name__ == "__main__":
    main()
