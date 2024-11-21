import paho.mqtt.client as mqtt
import mediapipe as mp
import cv2
import keras
import tensorflow
import numpy as np
import os
import pickle
import time
import threading
import json
import copy
#from main import Task, AssemblyList
#import main.py

class CameraControl:
    #MQTT methods
    def on_connect(self,client, userdata, flags, rc):

        print("Connected with result code " + str(rc))
        client.subscribe("master/current_task")
       


    def on_message(self,client, userdata, msg):
        print("Message received: ")
        if msg.topic == "master/current_task":
            print(msg.payload)
            #print(type(msg.payload))
            try:
                jsondict = json.loads(msg.payload)
                self.currentTask = jsondict["name"]
                self.currentIndex = jsondict["index"]
            except:
                print("Test")
                
                #raise TypeError("Could not read json") 
        else:
            print(msg.topic+" "+str(msg.payload))

    def __init__(self):
        self.client = mqtt.Client(client_id="camera")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect("192.168.137.1", 1883, 60)
        dir_path = os.path.dirname(os.path.realpath(__file__))  
        self.path = os.path.join(dir_path, 'model1105_relativeTolWrist_smalldropout.h5')
        try:
            self.model = keras.models.load_model(self.path)
            self.sequence_length = self.model.layers[0].input_shape[1]
        except:
            raise Exception("Could not load task recognition model") 
        self.TaskPerformed = False
        self.timerStarted = False
        self.currentTask = ""
        self.imageAcqStarted = False

        with open('module_camera\\mappingActivity.pkl', 'rb') as f:
            mappingActivity = pickle.load(f)
            self.actions = [mappingActivity[i] for i in sorted(mappingActivity.keys(), reverse=False)]
            print(self.actions)

        poseEstimationThread = threading.Thread(target=self.getPoseEstimatedPicture)
        poseEstimationThread.daemon = True
        poseEstimationThread.start()

        sendImageThread = threading.Thread(target=self.sendPicture)
        sendImageThread.daemon = True
        sendImageThread.start()

        taskRecognitionThread = threading.Thread(target=self.get_Camera_Activity)
        taskRecognitionThread.daemon = True
        taskRecognitionThread.start()

    def getPoseEstimatedPicture(self):
        """
        captures the image from camera and runs the pose estimation (hand coordinates detection) as fast as possible
        """
        mp_drawing = mp.solutions.drawing_utils
        mp_hand = mp.solutions.hands
        cap = cv2.VideoCapture(1)

        with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            
            while cap.isOpened():
                startTime = time.time()
                timeLoopBegin = time.time()
                ret, frame = cap.read()
            
                
                # Recolor Feed
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timeImageAcquisition = time.time() - timeLoopBegin
                # Make Detections
                results = holistic.process(image)

                # Recolor image back to BGR for rendering
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                #add estimated pose (hand coordinates) to image
                if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
                    mp_drawing.draw_landmarks(image, results.multi_hand_landmarks[0], mp_hand.HAND_CONNECTIONS)
                    mp_drawing.draw_landmarks(image, results.multi_hand_landmarks[1], mp_hand.HAND_CONNECTIONS)

                #set to global var
                self.image = image.copy()
                self.results = copy.copy(results)
                self.imageAcqStarted = True

                cv2.imshow('camera feed', image)  
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    self.imageAcqStarted = False
                    break
                #print("Time PoseEst: ",time.time()-startTime)

        self.cap.release()
        cv2.destroyAllWindows()
        self.imageAcqStarted = False


    def sendPicture(self):
        """
        sends images (including hand coordinates visualisation) as fast as possible via MQTT for HMI
        """
        while True:
            startTime = time.time()
            if self.imageAcqStarted:
                image = self.image.copy()
                image = cv2.resize(image,[200,150])
                _, img_encoded = cv2.imencode('.jpg', image)
                byte_array = img_encoded.tobytes()
                self.client.publish("image_topic", byte_array)
            time.sleep(0.1)
            #print("Time SendPic: ",time.time()-startTime)


    def get_Camera_Activity(self,relativeCoordinates=True,relativeTolwrist=True):
        """
        task recognition by trained LSTM
        """
        data = []
        nextStateReseted = False
        self.TaskPerformednextState =False
        self.timeCorrectTask = 0.0
        #waiting for first image
        while not self.imageAcqStarted:
            time.sleep(0.05)

        while self.imageAcqStarted:
            startTime = time.time()
            results = self.results
            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
                
                datasetLeftHand = [i for i in results.multi_hand_landmarks[0].landmark]
                datasetRightHand = [i for i in results.multi_hand_landmarks[1].landmark]
                dataset = [datasetLeftHand + datasetRightHand]
                    
                datasettmp = []
                if relativeCoordinates:
                     if relativeTolwrist:
                        for i in dataset[0]:
                            datasettmp.append(i.x - dataset[0][0].x)
                            datasettmp.append(i.y - dataset[0][0].y)
                            datasettmp.append(i.z)
                     else:
                        tmpCnt = 0
                        for i in dataset[0]:
                            if tmpCnt > 0 and tmpCnt < 21:
                                datasettmp.append(i.x-datasettmp[0])
                                datasettmp.append(i.y-datasettmp[1])
                                datasettmp.append(i.z)
                            elif tmpCnt > 21:
                                datasettmp.append(i.x-datasettmp[63])
                                datasettmp.append(i.y-datasettmp[64])
                                datasettmp.append(i.z)
                            else:
                                datasettmp.append(i.x)
                                datasettmp.append(i.y)
                                datasettmp.append(i.z)
                            tmpCnt+=1
                else:
                    for i in dataset[0]:
                        datasettmp.append(i.x)
                        datasettmp.append(i.y)
                        datasettmp.append(i.z)
                if len(data) == self.sequence_length:
                    data.pop(0)
                data.append(datasettmp)

                #timeDataPreProcessing = time.time() - timeLoopBegin

                if len(data) == self.sequence_length and self.currentTask != "" and self.currentTask != "finished":
                    prediction = self.model.predict(np.expand_dims(data,axis=0))[0]
                    self.recognizedTask = self.actions[np.argmax(prediction)]

                    #timeTaskPredicition = time.time() - timeLoopBegin

                    print( "Recognition: " + self.recognizedTask + " ---- Task of Assembly List: " + self.currentTask)
  
                    if (self.recognizedTask == self.currentTask or self.recognizedTask == "nextState") and not self.TaskPerformed and not self.TaskPerformednextState:
                        #waiting for successfully recognized task (at least 2 seconds)
                        if time.time() - self.timeCorrectTask > 2.0:
                            if self.recognizedTask == "nextState":
                                self.TaskPerformednextState = True
                            else:
                                self.TaskPerformed = True
                    elif (self.TaskPerformed and self.recognizedTask != self.currentTask) or (self.TaskPerformednextState and self.recognizedTask == "nextState" and nextStateReseted):    #if task successfully performend and finished
                        self.TaskPerformed = False
                        self.TaskPerformednextState = False
                        nextStateReseted = False
                        self.timeCorrectTask = time.time()
                        print("MQTT Publish will be send!")
                        self.client.publish("submodule/task",json.dumps({"current_task": self.currentIndex, "new_task": self.currentIndex+1}),qos=2)
                        print("MQTT Publish was performed!")
                    elif self.recognizedTask != self.currentTask and self.recognizedTask != "nextState":
                        self.timeCorrectTask = time.time()
                        nextStateReseted = True
                        self.TaskPerformednextState = False
                    print("task performed:"+str(self.TaskPerformed)+"nextStatePerformed:"+str(self.TaskPerformednextState)+"reset:"+str(nextStateReseted)+"time"+str(time.time()-self.timeCorrectTask))
                    

            else:
                time.sleep(0.1)
            #print("Time TaskRec: ",time.time()-startTime)

                    #timeImageSending = time.time() - timeLoopBegin
                        #print("Timing")
                        #print("Image Ac.: "+str(timeImageAcquisition) 
                        #      + " Pose Est.: "+str(timeImagePoseEst-timeImageAcquisition)
                        #      + " Preproc: "+str(timeDataPreProcessing-timeImagePoseEst)
                        #      + " Task Pred.: "+str(timeTaskPredicition-timeDataPreProcessing)
                        #      + " Sending: "+str(timeImageSending-timeTaskPredicition))

                


    
        """
        TO DO:
        run programm on another pc -> checking frame rate
        possible solutions if fps still to low:
        -minimize neural network size -> maybe 10-20ms gain
        -run predicition and pose estimation in two seperate threads -> at least mqtt rate is high
        """




if __name__ == '__main__':
    camera = CameraControl()
    #camera.get_Camera_Activity()
    #activityRecognitionTask = threading.Thread(target=CameraControl.get_Camera_Activity)
    #activityRecognitionTask.daemon = True
    #activityRecognitionTask.start()
    camera.client.loop_forever()
    #activityRecognitionTask.stop()
    


