# 🛠️ AssemblyAssistant  

### 🌟 Key Features  
- **📹 Live Camera GUI:**  
  Displays a top-down live feed of the assembly desk, showing the worker’s hands and the current step in the assembly process.  
- **🖐️ Hand Tracking with Mediapipe:**  
  Tracks the worker's hands to detect actions using a self-trained neural network. The system automatically progresses to the next step when an action (e.g., welding) is completed.  
- **🔊 Speech Recognition:**  
  Wake word detection ("Roxy”) triggers voice commands processed via ChatGPT API, enabling navigation between assembly steps.  
- **🔄 Modular Components:**  
  - **Main GUI:** Central hub for step tracking, live video, and user navigation.  
  - **Camera Module:** Tracks actions and sends MQTT messages to the GUI for step progression.  
  - **Voice Control Module:** Enables hands-free interaction via speech commands.  

### 💻 How It Works  
1. **Initialization:**  
   - The worker starts the assembly process via the GUI, which displays the current step and a live desk view.  
2. **Hand Tracking and Step Detection:**  
   - A camera tracks hand movements using Mediapipe.  
   - A neural network processes the hand data to determine if the current step is complete.  
   - Upon completion, an MQTT message is sent to the GUI, progressing to the next step.  
3. **Voice Control:**  
   - The system listens for the wake word “Roxy.”  
   - Commands like “Repeat the last step” or “Skip to the next one” are processed via the ChatGPT API.  
4. **Manual Control:**  
   - Workers can navigate steps directly through the GUI for added flexibility.  
