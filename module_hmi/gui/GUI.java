package gui;

/**
 * Main class to start the GUI.
 */
public class GUI {
	
	public static void main(String[] args) {
		// Create model
		Model model = new Model();
		// Create view
		View view = new View(model);
	
		// Register view in model 
		model.setView(view);
	}

}
