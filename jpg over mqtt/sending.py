import cv2
import paho.mqtt.client as mqtt
import time

#TODO maybe its best to not specify a framerate at all to get the smoothest performance possible
fps = 60
client = mqtt.Client()
client.connect("localhost", 1883)
cap = cv2.VideoCapture(1)
while True:
    start_time = time.time()

    ret, frame = cap.read()
    _, img_encoded = cv2.imencode('.jpg', frame)
    byte_array = img_encoded.tobytes()
    client.publish("image_topic", byte_array)

    elapsed_time = time.time() - start_time
    remaining_time = (1 / fps) - elapsed_time
    if remaining_time > 0:
        time.sleep(remaining_time)
    else:
        print("Cant keep up with framerate")
