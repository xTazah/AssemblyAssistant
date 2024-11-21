import cv2
import paho.mqtt.client as mqtt
import numpy as np

client = mqtt.Client()
client.connect("localhost", 1883)

#holds latest_frame
latest_frame = None

def on_message(client, userdata, msg):
    global latest_frame
    
    byte_array = np.frombuffer(msg.payload, dtype=np.uint8)
    frame = cv2.imdecode(byte_array, cv2.IMREAD_COLOR)
    
    latest_frame = frame

client.subscribe("image_topic")
client.on_message = on_message

client.loop_start()

cv2.namedWindow("Received Frame", cv2.WINDOW_NORMAL)
while True:
    # new frame?
    if latest_frame is not None:
        cv2.imshow("Received Frame", latest_frame)
        cv2.waitKey(1)  # waits for delay
        latest_frame = None

