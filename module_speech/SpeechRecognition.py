import speech_recognition as sr
import pyaudio
import threading
import paho.mqtt.client as mqtt
from transformers import pipeline
import time
import json
from enum import Enum
import asyncio
import json
import threading
import openai
import os
import dotenv
from pydantic import ValidationError

from module_speech.response_format import ConfidenceScores

dotenv.load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = openai_api_key


WAKE_WORD = "roxy"
CONFIDENCE = 0.70
TIMEOUT = 30
USE_CHATGPT_API = True
DEBUG = False
#forward_labels = ["forward", "next"]
forward_labels = ["step forward"]
#backward_labels = ["backward", "previous"]
backward_labels = ["step backward"]

class NextStep(Enum):
    FORWARD = 1
    BACKWARD = 2

class SpeechRecognition:
    #MQTT methods
    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("master/current_task")
        print("Waiting for task from master")


    def on_message(self,client, userdata, msg):
        print("Message received: ")
        if msg.topic == "master/current_task":
            print(msg.topic+" "+str(msg.payload))
            if msg.payload == "finished":
                print("Finished... Waiting for new task")
            else:
                try:
                    payload = json.loads(msg.payload)
                    self.task = payload['index']
                    self.gotTask = True
                    print("Listening for wake word...")
                except Exception as e:
                    print(e)
        else:
            print(msg.topic+" "+str(msg.payload))

    def __init__(self):
        print("Initializing...")
        start = time.time()
        self.client = mqtt.Client(client_id="speech")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        if DEBUG:
            self.client.connect("localhost", 1883, 60)
        else:
            self.client.connect("192.168.137.1", 1883, 60)
        print("MQTT client initialized")
        self.gotTask = False
        if not USE_CHATGPT_API:
            print("Using tranformer pipeline")
            self.processor = pipeline(model="facebook/bart-large-mnli", multi_label = True)
            print("Processing-Model initialized")

        end = time.time()
        print("Init took " + str(end-start) + " seconds")
        #start = time.time()
        #while(not self.gotTask):
        #    if time.time() - start  >= TIMEOUT:
        #        raise TimeoutError("Did not receive a task from master in specified timeout period (" + str(TIMEOUT) + " seconds)")
        #    time.sleep(0.1)

        if DEBUG:
            self.task = 0
            t = threading.Thread(target=SpeechRecognition.wake_word_callback, args=(self,"im finished",))
            t.daemon = True
            t.start()
        else:
            t = threading.Thread(target=SpeechRecognition.listen, args=(self,))
            t.daemon = True
            t.start()

    async def send_to_openai(self,text):
        with open('./module_speech/system_prompt.txt', 'r') as file:
            system_prompt = file.read()

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ],
            temperature=0.63,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "confidence_scores",
                    "schema": ConfidenceScores.schema()
                }
            }
        )
        content_json_str = response["item"]["messages"][1]["text"]

        try:
            content_dict = json.loads(content_json_str)
            confidence_scores = ConfidenceScores(**content_dict)
            print(confidence_scores)

            confidence_dict = confidence_scores.dict()
            selected_labels = [
                label for label, confidence in confidence_dict.items() if confidence > 80
            ]

            # handle the selected labels
            if selected_labels and "Other" not in selected_labels:
                next_step = NextStep.FORWARD if "Forward" in selected_labels else NextStep.BACKWARD
                self.publishTask(next_step, self.task)
            else:
                # handle 'Other' or no high-confidence labels
                pass

        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)

        except ValidationError as e:
            print("Error parsing confidence scores:", e)

    # callback function
    def wake_word_callback(self, text):
        try:
            print("Wake word detected! Processing text: "+text)
            if USE_CHATGPT_API:
                asyncio.run(self.send_to_openai(text))
            else:
                response = self.processor(
                    text,
                    #candidate_labels= forward_labels + backward_labels + ["other"],
                    candidate_labels= forward_labels + backward_labels,
                )
                print(response)
                forward_confidence = 0
                backward_confidence = 0
                for i, label in enumerate(response["labels"]):
                    if(label in forward_labels):
                        forward_confidence += (response["scores"][i])
                    if(label in backward_labels):
                        backward_confidence += (response["scores"][i])

                #if(forward_confidence > CONFIDENCE or backward_confidence > CONFIDENCE and not response["labels"][0] =="other"):
                if(forward_confidence > CONFIDENCE or backward_confidence > CONFIDENCE):
                    self.publishTask(NextStep.FORWARD if response["labels"][0] in forward_labels else NextStep.BACKWARD, self.task)
                else:
                    #other
                    pass
        except Exception as e:
            print("Error processing text {0}".format(e))

    def publishTask(self, nextStep: NextStep, currentTask):
        old_task = currentTask
        print("currentTask: {}".format(currentTask))
        new_task = currentTask-1 if nextStep == NextStep.BACKWARD else currentTask+1
        print("newTask: {}".format(new_task))
        payload = json.dumps({"current_task": old_task, "new_task": new_task})
        print(payload)
        self.client.publish("submodule/task", payload, qos=1)

    def play_audio(self,audio_data):
        try:
            print("Playing audio")
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(audio_data.sample_width),
                            channels=1,
                            rate=44100,
                            output=True)
            stream.write(audio_data.get_wav_data())
            stream.stop_stream()
            stream.close()
            p.terminate()
            print("Finished playing audio")
        except Exception as e:
            print("Error playing audio: {0}".format(e))

    def listen(self):
        # Initialize the recognizer
        r = sr.Recognizer()

        # Use the default microphone as the audio source
        with sr.Microphone() as source:
            # Calibrate the microphone to remove noise
            r.adjust_for_ambient_noise(source)
            r.energy_threshold = 1000  # TODO bringt das was?

            while True:
                if self.gotTask:
                    # Listen for audio input
                    #audio = r.listen(source)
                    #TODO improve listening
                    audio = r.listen(source,5,5)
                    # DEBUG -- play audio in separate thread
                    #t = threading.Thread(target=SpeechRecognition.play_audio, args=(self,audio,))
                    #t.deamon = True
                    #t.start()

                    try:
                        #  google speech recognitoin TODO funktionieren die andere besser?
                        text = r.recognize_google(audio).lower()
                        print(text)
                        # Check if the wake word is in the transcribed text
                        if WAKE_WORD in text:
                            #only process text after wake word
                            text = text.partition(WAKE_WORD)[2]
                            t = threading.Thread(target=SpeechRecognition.wake_word_callback, args=(self,text,))
                            t.daemon = True
                            t.start()
                    except sr.UnknownValueError:
                        # audio not recognised
                        print("Could not understand audio")
                    except sr.RequestError as e:
                        # error in google Speech recognition
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
                    else:
                        time.sleep(0.1)

if __name__ == '__main__':
    speechrecognition = SpeechRecognition()
    speechrecognition.client.loop_forever()