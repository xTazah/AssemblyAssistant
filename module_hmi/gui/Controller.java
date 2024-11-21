package gui;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.KeyStroke;

/**
 * The superclass implementing ActionListener for all controller related classes.
 */
public abstract class Controller implements ActionListener {
	private Model model;

	// Constructor
	public Controller(Model model) {
		this.setModel(model);
	}
	
	public abstract void actionPerformed(ActionEvent e);

	/**
	 * @return the model
	 */
	public Model getModel() {
		return model;
	}

	/**
	 * @param model the model to set
	 */
	public void setModel(Model model) {
		this.model = model;
	}

}

/**
 * The controller for a 'Next' button on the homepage.
 */
class nextButtonControl extends Controller {

	public nextButtonControl(Model model) {
		super(model);
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		getModel().switchPanel();
	}
	
}

/**
 * The controller for a 'Back' button on a task page.
 */
class backButtonControl extends Controller {

	public backButtonControl(Model model) {
		super(model);
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		getModel().switchPanel(false);
	}
	
}

/**
 * The controller for a 'Next' button on a task page.
 */
class nextButtonTaskControl extends Controller {

	public nextButtonTaskControl(Model model) {
		super(model);
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		getModel().switchPanel(true);
	}
	
}

/**
 * The controller for the menu option 'About'.
 */
class aboutMenuControl extends AbstractAction {
	private static final long serialVersionUID = 1L;

	public aboutMenuControl() {
		putValue(Action.NAME, "About...");
		putValue(Action.ACCELERATOR_KEY, KeyStroke.getKeyStroke(KeyEvent.VK_H, KeyEvent.CTRL_DOWN_MASK));
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		String aboutText = "Projekt im Rahmen des Moduls Assistenzsysteme bei Prof. Dr. Alexander Maier.\n"
				+ "Von Jona Brockhaus, Finn Köhler und Janis Paul.";
		JOptionPane.showMessageDialog(new JFrame(), aboutText, "Über", JOptionPane.PLAIN_MESSAGE);
	}
}

/**
 * The controller for the menu option 'Homepage'.
 */
class homeMenuControl extends AbstractAction {
	private static final long serialVersionUID = 1L;
	
	private Model model;

	public homeMenuControl(Model model) {
		putValue(Action.NAME, "Homepage");
		putValue(Action.ACCELERATOR_KEY, KeyStroke.getKeyStroke(KeyEvent.VK_0, KeyEvent.CTRL_DOWN_MASK));
		this.model = model;
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		model.toMenuPanel();
	}
}

/**
 * The controller for the menu option 'Exit'.
 *
 */
class quitMenuControl extends AbstractAction {
	private static final long serialVersionUID = 1L;

	public quitMenuControl() {
		putValue(Action.NAME, "Exit");
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		System.exit(0);
	}
}
