import json
import paho.mqtt.client as mqtt
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class AssemblyList:
    name: str
    task: list

    def __str__(self):
        return "Name: "+ self.name +  ''.join(["\n--> " + str(i) for i in self.task ])

@dataclass_json
@dataclass
class Task:
    index: int
    name: str #solder, screw, ...
    description: str
    max_index: int

    def __str__(self):
        return "Index: " + str(self.index) + "\t | Name: "+ self.name + "\t | Description: "+ self.description + " | Max_Index: " + str(self.max_index)

class Master:
    def __init__(self):
        self.assemblyLists = self.readAssembylLists()
        self.client = mqtt.Client(client_id="master")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("192.168.137.1", 1883, 60)
        
        #TODO dont hardcode
        self.currentAssemblyList = 0
        self.currentTask = 0
        print("Publish inital Task")
        self.publishAssemblyList()
        #self.client.publish("master/current_task",self.assemblyLists[self.currentAssemblyList].task[self.currentTask].to_json())
                            
        pass

    def publishAssemblyList(self):
        available = json.dumps({"Available IPCs": [str(i.name) for i in self.assemblyLists]})
        self.client.publish("master/choose_list", payload=available, retain= True, qos= 2)

    def publishCurrentTask(self):
        self.client.publish("master/current_task",self.assemblyLists[self.currentAssemblyList].task[self.currentTask].to_json(), retain= True, qos=2)
    #MQTT methods
    def on_connect(self,client, userdata, flags, rc):

        print("Connected with result code " + str(rc))
        client.subscribe("submodule/+")
        client.subscribe("master/#")

    def on_message(self,client, userdata, msg):
        print("topic: " + str(msg.topic)+ " payload: " + str(msg.payload))
        if msg.topic == "submodule/task":
            payload = json.loads(msg.payload)
            if payload["current_task"] == self.currentTask:
                if payload["new_task"] <= self.assemblyLists[self.currentAssemblyList].task[-1].index and payload["new_task"] >= 0:
                    self.currentTask = payload["new_task"]
                    self.publishCurrentTask()
                else:
                    self.publishAssemblyList()
                    self.currentTask = 0
                    self.client.publish("master/current_task", payload="finished", retain= True, qos= 2)
        elif msg.topic == "submodule/choose_list":
            if int(msg.payload) < len(self.assemblyLists) and int(msg.payload) >=0:
                self.currentAssemblyList = int(msg.payload)
                self.publishCurrentTask()
        #else:
        #    print("topic: " + str(msg.topic)+ " payload: " + str(msg.payload))


    def readAssembylLists(self):
        assemblyLists = []
        with open('assembly-list.json') as f:
            data = json.load(f)

        for ipc in data:
            assembyList = AssemblyList(name= ipc['IPC'],task= [])

            for i,task in enumerate(ipc['Tasks']):
                assembyList.task.append( Task(index = i, name = task['Name'], description=task['Description'], max_index= len(ipc['Tasks'])-1))
            
            assemblyLists.append(assembyList)

        return assemblyLists
    
    def printAssemblyLists():
        #TODO
        raise NotImplementedError

    
if __name__ == '__main__':
    master = Master()
    master.client.loop_forever()