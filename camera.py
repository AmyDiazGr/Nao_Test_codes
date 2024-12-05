import cv2
import numpy as np
from naoqi import ALProxy

ip = "10.42.0.134"
port = 9559
video_proxy = ALProxy("ALVideoDevice", ip, port)

resolution = 2    
color_space = 11    
fps = 30
name_id = video_proxy.subscribe("python_client", resolution, color_space, fps)

try:
    while True:
        image_container = video_proxy.getImageRemote(name_id)
        image_width = image_container[0]
        image_height = image_container[1]
        raw_image = image_container[6]

        image_array = np.frombuffer(raw_image, dtype=np.uint8).reshape((image_height, image_width, 3))

        cv2.imshow("NAO Camera Feed", image_array)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    video_proxy.unsubscribe(name_id)
    cv2.destroyAllWindows()