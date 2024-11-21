package gui;

import java.awt.BorderLayout;
import java.awt.CardLayout;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SwingConstants;
import javax.swing.border.EmptyBorder;

public class View extends JFrame {
	private static final long serialVersionUID = 1L;

	// Reference to the model 
	private Model model;
	
	// AWT related variables
	private CardLayout cardLayout;

	// Swing related variables
	private JTextArea txtOutputMenu, txtOutputTasks;
	private JTextField tfTaskTitle;
	private JButton btnNext, btnNextStep;
	private JComboBox<String> cb;
	private String[] ipcs = {"No IPCs available"};
	private JLabel imageLabel = new JLabel();
	private JLabel imageLabelTask = new JLabel();

	// Constructor
	public View(Model model) {
		this.model = model;
		
		cardLayout = new CardLayout(0, 0);
		setOutputTxtAreas();

		setTitle("Assembly Wizard GUI");
		setMinimumSize(new Dimension(900, 800));
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setLayout(cardLayout);
		
		JPanel menuPanel = new JPanel();
		menuPanel.setBorder(new EmptyBorder(5, 5, 5, 5));
		menuPanel.setLayout(new BorderLayout(3, 3));
		add(menuPanel, "Menu");
		
		// Menubar
		createMenuBar();
		
		JPanel optionsPanel = createOptionsPanel();
		menuPanel.add(optionsPanel);

		JPanel southArea = createNextButtonOutputPanel();
		menuPanel.add(southArea, BorderLayout.SOUTH);
		
		// Create panels for tasks
		JPanel tasksPanel = new JPanel();
//		tasksPanel.setBorder(new EmptyBorder(5, 5, 5, 5));
		tasksPanel.setLayout(new BorderLayout(3, 3));
		getContentPane().add(tasksPanel, "Tasks");
		
		JPanel taskInfo = new JPanel();
//		taskInfo.setBorder(new EmptyBorder(5, 5, 5, 5));
		taskInfo.setLayout(new BorderLayout(3, 3));
		tfTaskTitle = new JTextField();
		tfTaskTitle.setEditable(false);
		tfTaskTitle.setText("");
		tfTaskTitle.setHorizontalAlignment(SwingConstants.CENTER);
		taskInfo.add(tfTaskTitle, BorderLayout.NORTH);
		JPanel imagePanel = new JPanel();
		imagePanel.add(imageLabelTask);
		taskInfo.add(imagePanel, BorderLayout.CENTER);
		tasksPanel.add(taskInfo);
		JPanel southAreaTasks = createBackNextButtonsOutputPanel(txtOutputTasks);
		tasksPanel.add(southAreaTasks, BorderLayout.SOUTH);
		
		refresh();

		setLocation(250, 60);
//		setBounds(100, 100, 450, 310);
		setStandardBounds();
		setVisible(true);
		
		model.mqttConnectAndSubscribe();
	}

	// Getters/Setters
	
	/**
	 * @return the ipcs
	 */
	public String[] getIpcs() {
		return ipcs;
	}
	
	/**
	 * @param ipcs the ipcs to set
	 */
	public void setIpcs(String[] ipcs) {
		this.ipcs = ipcs;
	}
	
	/**
	 * @return the tfInputOptionOne
	 */
	public JTextField getTfTaskTitle() {
		return tfTaskTitle;
	}

	/**
	 * @return the cb
	 */
	public JComboBox<String> getComboBox() {
		return cb;
	}

	/**
	 * @return the btnNext
	 */
	public JButton getBtnNext() {
		return btnNext;
	}

	/**
	 * @return the btnStart
	 */
	public JButton getBtnNextStep() {
		return btnNextStep;
	}

	/**
	 * @param imageLabel the imageLabel to set
	 */
	public void setImageLabel(ImageIcon icon) {
	    this.imageLabel.setIcon(icon);
	    this.imageLabelTask.setIcon(icon);
	}

	// Methods

	/**
	 * Sets standard bounds to maximized.
	 */
	public void setStandardBounds() {
		setExtendedState(JFrame.MAXIMIZED_BOTH);
	}
	
	/**
	 * Creates the necessaryoutput text areas.
	 */
	public void setOutputTxtAreas() {
		txtOutputMenu = new JTextArea(6, 10);
		txtOutputMenu.setEditable(false);
		txtOutputMenu.setLineWrap(true);
		txtOutputMenu.setWrapStyleWord(true);
		
		txtOutputTasks = new JTextArea(6, 10);
		txtOutputTasks.setEditable(false);
		txtOutputTasks.setLineWrap(true);
		txtOutputTasks.setWrapStyleWord(true);
	}
	
	/**
	 * Refreshes output text areas.
	 */
	public void refresh() {
		txtOutputMenu.setText(model.getOutput());
		txtOutputTasks.setText(model.getOutput());
	}
	
	/**
	 * Creates the menu bar.
	 */
	public void createMenuBar() {
		JMenuBar menuBar = new JMenuBar();

		// Menu entries
		JMenu fileMenu = new JMenu("File");
		menuBar.add(fileMenu);
		JMenu helpMenu = new JMenu("Help");
		menuBar.add(helpMenu);

		helpMenu.add(new aboutMenuControl());

		fileMenu.add(new homeMenuControl(model));
		fileMenu.add(new quitMenuControl());

		// Connect menu bar and frame
		setJMenuBar(menuBar);

		setVisible(true);
	}
	
	/**
	 * Creates a panel with a combo box.
	 * @return The created options panel
	 */
	public JPanel createOptionsPanel() {
		JPanel panel = new JPanel();
		panel.setLayout(new BorderLayout(3,3));
		cb = new JComboBox<String>(ipcs);
		panel.add(cb, BorderLayout.NORTH);
		JPanel imagePanel = new JPanel();
		imagePanel.add(imageLabel);
		panel.add(imagePanel, BorderLayout.CENTER);
		return panel;
	}
	
	/**
	 * Creates a panel with 'Next' button and output text area.
	 * @return The created panel
	 */
	public JPanel createNextButtonOutputPanel() {
		JPanel panel = new JPanel();
		GridBagConstraints constraints = new GridBagConstraints();
		JScrollPane scrollTxt = new JScrollPane(txtOutputMenu);
		btnNext = new JButton("Next");
		btnNext.addActionListener(new nextButtonControl(model));
		Dimension btnSize = btnNext.getPreferredSize();
        btnSize.height = 50;
        btnNext.setPreferredSize(btnSize);
		panel.setLayout(new GridBagLayout());
		// Layout of the 'Next' button
		constraints.fill = GridBagConstraints.HORIZONTAL;
		constraints.ipady = 0;
		constraints.weightx = 0.5;
		constraints.gridx = 0;
		constraints.gridy = 1;
		constraints.insets = new Insets(10, 10, 10, 10);
		constraints.anchor = GridBagConstraints.PAGE_END;
		panel.add(btnNext, constraints);
		// Layout of the text area
		constraints.fill = GridBagConstraints.HORIZONTAL;
		constraints.ipady = 0;
		constraints.gridx = 0;
		constraints.gridy = 0;
		panel.add(scrollTxt, constraints);
		return panel;
	}
	
	/**
	 * Creates a panel with 'Next' button and output text area.
	 * @param txt The JTextArea to add to the panel
	 * @return The created panel
	 */
	public JPanel createBackNextButtonsOutputPanel(JTextArea txt) {
		JPanel panel = new JPanel();
		GridBagConstraints constraints = new GridBagConstraints();
		JScrollPane scrollTxt = new JScrollPane(txt);
		JButton btnBack = new JButton("Back");
		btnBack.setEnabled(true);
		btnBack.addActionListener(new backButtonControl(model));
		Dimension btnSize = btnBack.getPreferredSize();
        btnSize.height = 50;
        btnBack.setPreferredSize(btnSize);
		btnNextStep = new JButton("Next");
		btnNextStep.setEnabled(true);
		btnNextStep.addActionListener(new nextButtonTaskControl(model));
//		btnSize = btnNextStep.getPreferredSize();
//      btnSize.height = 50;
        btnNextStep.setPreferredSize(btnSize);
		panel.setLayout(new GridBagLayout());
		// Layout for 'Back' button 
		constraints.fill = GridBagConstraints.HORIZONTAL;
		constraints.ipady = 0;
		constraints.weightx = 0.5;
		constraints.gridx = 0;
		constraints.gridy = 0;
		constraints.insets = new Insets(10, 10, 10, 10);
		constraints.anchor = GridBagConstraints.PAGE_START;
		panel.add(btnBack, constraints);
		// Layout for 'Next' button 
		constraints.fill = GridBagConstraints.HORIZONTAL;
		constraints.ipady = 0;
		constraints.weightx = 0.5;
		constraints.gridx = 1;
		constraints.gridy = 0;
		constraints.insets = new Insets(10, 10, 10, 10);
		constraints.anchor = GridBagConstraints.PAGE_END;
		panel.add(btnNextStep, constraints);
		// Layout for text area 
		constraints.fill = GridBagConstraints.HORIZONTAL;
		constraints.ipady = 0;
		constraints.gridwidth = 2;
		constraints.gridx = 0;
		constraints.gridy = 1;
		panel.add(scrollTxt, constraints);
		return panel;
	}
	
	/**
	 * Switches to a panel.
	 * @param panel The name of the panel
	 */
	public void switchToPanel(String panel) {
		cardLayout.show(getContentPane(), panel);
		refresh();
	}
}
