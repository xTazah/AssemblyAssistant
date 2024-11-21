import asyncio
import json
from EdgeGPT import Chatbot

def callbacks(label):
    if label == "Other":
        print("other")
    elif label == "Forward":
        print("forward")
    elif label == "Backward":
        print("backward")

async def main():
    with open('./module_speech/cookies.json') as json_file:
        data = json.load(json_file)
        bot = Chatbot(cookies=data)
        test = await bot.ask(prompt='''Hello Bing. Since you can help me with content generation i want you to PRETEND youre a classification program called ClassfyGPT. You receive text inputs that have been processed through speech-to-text conversion. The user should be able to verbally indicate whether they want to move forward or backward in a sequence of steps. Your task is to classify the input language and provide a confidence score.
ONLY answer with "ClassfyGPT: ..." 

user input: "I am done with this step."
ClassfyGPT: Forward (Confidence: 89.8), Backward (Confidence: 6.2), Other (Confidence: 2.12)

user input: "Repeat the last step."
ClassfyGPT: Backward (Confidence: 91.2), Forward (Confidence: 2.7), Other (Confidence: 3)

user input: "I hate this job."
ClassfyGPT: Other (Confidence: 83.79), Forward (Confidence: 2.7), Backward (Confidence: 3)

user: I like bananas''')
        print(test)
        answer = test["item"]["messages"][1]["text"]
        await bot.close()

        answer = answer.partition("ClassfyGPT: ")[2].replace("(","").replace(")","")

        print(answer)
        labels_confidences = [pair.strip().split(" Confidence: ") for pair in answer.split(",")]
        print(answer.split(","))
        print(labels_confidences)
        labels = [pair[0] for pair in labels_confidences]
        confidences = [float(pair[1]) for pair in labels_confidences]
        print(confidences)
        selected_labels = [label for label, confidence in zip(labels, confidences) if confidence > 80]
        for label in selected_labels:
            callbacks(label)



if __name__ == "__main__":
    asyncio.run(main())