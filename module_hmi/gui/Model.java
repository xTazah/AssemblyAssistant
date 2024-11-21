package gui;

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;

import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.json.JSONObject;
import org.json.JSONArray;

public class Model {
	private View view;
	
	// Data of the model 
	private String displayOutput;
	private Task currentTask;
	private int taskStep = -1;
	private IMqttClient client;
	
	// Constructor 
	public Model() {
		displayOutput = "Welcome to the component assembly wizard.\n"
				+ "Select the IPC for the assembly steps and click on 'Next'.";
	}
	
	// Getters/Setters
	
	/**
	 * Adds the view to the model.
	 * @param view The view
	 */
	public void setView(View view){
		this.view = view;
		view.refresh();
	}
	
	/**
	 * @return the displayOutput
	 */
	public String getOutput(){
		return displayOutput;
	}
	
	// Methods
	
	/**
	 * Connect to the MQTT broker and subscribe to master/choose_list, master/current_task and image_topic.
	 */
	public void mqttConnectAndSubscribe() {
		try {
			client = new MqttClient("tcp://192.168.137.1:1883", "hmi");
			MqttConnectOptions options = new MqttConnectOptions();
			options.setCleanSession(true);
			client.connect(options);

			client.subscribe("master/choose_list", 2, new IMqttMessageListener() {
			    @Override
			    public void messageArrived(String topic, MqttMessage message) throws Exception {
			    	String msgStr = new String(message.getPayload());
			        System.out.println(topic + ": " + msgStr);
			        JSONObject json = new JSONObject(msgStr);
			        JSONArray ipcs = json.getJSONArray("Available IPCs");
			        view.getComboBox().removeAllItems();
			        for (int i = 0; i < ipcs.length(); i++) {
			            view.getComboBox().addItem(ipcs.getString(i));
			        }
			        view.refresh();
			    }
			});
			client.subscribe("master/current_task", 2, new IMqttMessageListener() {
			    @Override
			    public void messageArrived(String topic, MqttMessage message) throws Exception {
			    	String msgStr = new String(message.getPayload());
			        System.out.println(topic + ": " + msgStr);
			        if (msgStr.equals("finished")) {
			        	toMenuPanel();
			        } else {
				        JSONObject json = new JSONObject(msgStr);
				        currentTask = new Task(
				        		(int) json.get("index"), 
				        		(String) json.get("name"), 
				        		(String) json.get("description"),
				        		(int) json.getInt("max_index")
				        );
				        taskStep = currentTask.getIndex();
				        switchPanel();
			        }
			        view.refresh();
			    }
			});
			client.subscribe("image_topic", 0, new IMqttMessageListener() {
			    @Override
				public void messageArrived(String topic, MqttMessage message) throws Exception {
					byte[] msg = message.getPayload();
//					System.out.println(topic + ": ");
					BufferedImage image = null;

					try (ByteArrayInputStream bis = new ByteArrayInputStream(msg)) {
						image = ImageIO.read(bis);
					} catch (Exception e) {
						e.printStackTrace();
					}

					if (image != null) {
						view.setImageLabel(new ImageIcon(image));
						view.refresh();
					}
				}
			});
		} catch (Exception e) {
			displayOutput = "The connection to the MQTT broker failed.\n" +
					"Please restart the application.";
		}
	}

	/**
	 * @return the client
	 */
	public IMqttClient getClient() {
		return client;
	}

	/**
	 * @param close the client
	 */
	public void closeClient() {
		try {
			client.close();
		} catch (MqttException e) {
			
		}
	}

	/**
	 * Switches to the correct panel according to taskStep and currentTask.
	 */
	public void switchPanel() {
		if (taskStep == -1) {
			publishAssemblyIndex();
//			setNameAndDescription();
			view.getBtnNextStep().setText("Next");
//			view.switchToPanel("Tasks");
		} else if (currentTask != null && taskStep >= 0) {
			setNameAndDescription();
			if (taskStep == currentTask.getMaxIndex()) {
				view.getBtnNextStep().setText("Done");
			} else {
				view.getBtnNextStep().setText("Next");
			}
			view.switchToPanel("Tasks");
		} else {
			displayOutput = "An error occurred.";
			view.switchToPanel("Menu");
		}
	}

	/**
	 * Switches to the correct panel when change is initiated by GUI.
	 * @param next The boolean used to determine whether to go a step forward or backward.
	 */
	public void switchPanel(boolean next) {
		if (currentTask != null && taskStep > -1 && next) {
			publishStep(taskStep, ++taskStep);
			if (taskStep > currentTask.getMaxIndex()) {
				toMenuPanel();
			} else {
				setNameAndDescription();
				if (taskStep == currentTask.getMaxIndex()) {
					view.getBtnNextStep().setText("Done");
				}
				view.refresh();
			}
		} else if (currentTask != null && taskStep > -1 && !next) {
			publishStep(taskStep, --taskStep);
			if (taskStep == -1) {
				toMenuPanel();
				displayOutput = "IPC is done. Please choose a new IPC.";
			} else {
				setNameAndDescription();
				view.getBtnNextStep().setText("Next");
				view.refresh();
			}
		} else {
			displayOutput = "An error occurred.";
			view.switchToPanel("Menu");
		}
	}
	
	/**
	 * Switches to the menu panel.
	 */
	public void toMenuPanel() {
		publishStep(taskStep, -1);
		taskStep = -1;
		displayOutput = "Select the IPC for the assembly steps and click on 'Next'.";
		view.switchToPanel("Menu");
	}
	
	/**
	 * Sets the name and the description according to currentTask.
	 */
	public void setNameAndDescription() {
		if (currentTask != null) {
			view.getTfTaskTitle().setText( (currentTask.getIndex() + 1) 
					+ " von " + (currentTask.getMaxIndex() + 1) + ": "
					+ currentTask.getName());
			displayOutput = currentTask.getDescription();
		}
	}
	
	/**
	 * Publishes the index of the current task and of the new task to initiate a change of the current step.
	 * @param currentIndex The integer of the current step
	 * @param nextIndex The integer of the next step
	 */
	public void publishStep(int currentIndex, int nextIndex) {
		try {
			client.publish(
					"submodule/task", 
					("{\"current_task\": " + currentIndex + ", \"new_task\": " + nextIndex + "}").getBytes(),
					1, true
			);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	/**
	 * Publishes the index of the chosen IPC of the combo box.
	 */
	public void publishAssemblyIndex() {
		try {
			client.publish(
					"submodule/choose_list", 
					(view.getComboBox().getSelectedIndex() + "").getBytes(), 
					1, true
			);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
