import java.awt.EventQueue;
import javax.swing.JFrame;
import java.awt.GridLayout;
import javax.swing.JPanel;
import java.awt.GridBagLayout;
import java.awt.GridBagConstraints;
import java.awt.Insets;
import java.awt.KeyEventDispatcher;
import java.awt.KeyboardFocusManager;
import javax.swing.border.TitledBorder;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.text.DefaultFormatter;
import java.awt.FlowLayout;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JFormattedTextField;
import java.awt.Font;
import java.awt.Color;
import java.awt.Dimension;
import de.yadrone.base.ARDrone;
import de.yadrone.base.navdata.BatteryListener;
import javax.swing.JProgressBar;
import javax.swing.JLabel;
import javax.swing.SwingConstants;
import javax.swing.JTextField;
import javax.swing.JSpinner;
import javax.swing.SpinnerNumberModel;
import javax.swing.ImageIcon;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.io.*;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

public class DroneControlGUI {

	//Variables for GUI
	private JFrame frmBciDroneControl;
	private JButton btnConnect;
	private JButton btnReset;
	private JButton btnTakeOff;
	private JButton btnLanding;
	private JButton btnEmergency;
	private JProgressBar prgBattery;
	
	private JButton btnConnect_1;
	private JButton btnActiviateControl;
	private JLabel lblLeft;
	private JLabel lblIdle;
	private JLabel lblRight;
	private JTextField txtLeft;
	private JTextField txtRight;
	
	private JSpinner spnSpeed;
	private JSpinner spnForwardSpeed;
	private JSpinner spnTriggerThreshold;
	
	//Variables for Drone control
	private ARDrone drone;
	private int droneSpeed = 10;
	private int droneForwardSpeed = 0;
	private MyDispatcher dispatcher;
	
	//Variables for BCI-control
	private BCIAcquisitionClient acquisitionClient;
	private double triggerThreshold = 80;
	
	//Variables for Logging
	private LogWriter logWriter = new LogWriter();
	
	
	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					DroneControlGUI window = new DroneControlGUI();
					window.frmBciDroneControl.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public DroneControlGUI() {
		//write the (error) output stream into log file
		try {
			PrintStream ps = new PrintStream(new BufferedOutputStream(new FileOutputStream("log.txt", true)));
			System.setErr(ps);
			System.setOut(ps);
		} catch (FileNotFoundException e1) {
			e1.printStackTrace();
		}
		
		writeLog("+++BCI drone control startet");
		
		initialize();
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		writeLog("Start building GUI");
		
		frmBciDroneControl = new JFrame();
		frmBciDroneControl.setResizable(false);
		frmBciDroneControl.setTitle("BCI Drone Control");
		
		//complete log file on exit
		frmBciDroneControl.addWindowListener(new WindowAdapter() {
			@Override
			public void windowClosing(WindowEvent arg0) {
				if (drone != null){
					drone.stop();
					drone = null;
				}
				
				writeLog("+++BCI drone control stopped");
				
				System.out.flush();
				System.err.flush();
			}
		});
		frmBciDroneControl.setBounds(100, 100, 538, 390);
		frmBciDroneControl.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		GridBagLayout gridBagLayout = new GridBagLayout();
		gridBagLayout.columnWidths = new int[] {500, 0};
		gridBagLayout.rowHeights = new int[] {120, 130, 110};
		gridBagLayout.columnWeights = new double[]{0.0, Double.MIN_VALUE};
		gridBagLayout.rowWeights = new double[]{0.0, 0.0, 0.0};
		frmBciDroneControl.getContentPane().setLayout(gridBagLayout);
		
		JPanel pnlDrone = new JPanel();
		pnlDrone.setBorder(new TitledBorder(null, "Drone", TitledBorder.LEADING, TitledBorder.TOP, null, null));
		GridBagConstraints gbc_pnlDrone = new GridBagConstraints();
		gbc_pnlDrone.fill = GridBagConstraints.BOTH;
		gbc_pnlDrone.insets = new Insets(0, 0, 5, 0);
		gbc_pnlDrone.gridx = 0;
		gbc_pnlDrone.gridy = 0;
		frmBciDroneControl.getContentPane().add(pnlDrone, gbc_pnlDrone);
		pnlDrone.setLayout(new FlowLayout(FlowLayout.CENTER, 5, 5));
		
		JPanel plnDrone1 = new JPanel();
		pnlDrone.add(plnDrone1);
		GridBagLayout gbl_plnDrone1 = new GridBagLayout();
		gbl_plnDrone1.columnWidths = new int[] {400};
		gbl_plnDrone1.rowHeights = new int[] {40, 40};
		gbl_plnDrone1.columnWeights = new double[]{1.0};
		gbl_plnDrone1.rowWeights = new double[]{1.0, 1.0};
		plnDrone1.setLayout(gbl_plnDrone1);
		
		JPanel plnDrone1_1 = new JPanel();
		GridBagConstraints gbc_plnDrone1_1 = new GridBagConstraints();
		gbc_plnDrone1_1.insets = new Insets(0, 0, 5, 0);
		gbc_plnDrone1_1.fill = GridBagConstraints.BOTH;
		gbc_plnDrone1_1.gridx = 0;
		gbc_plnDrone1_1.gridy = 0;
		plnDrone1.add(plnDrone1_1, gbc_plnDrone1_1);
		plnDrone1_1.setLayout(new GridLayout(1, 4, 0, 0));
		
		btnConnect = new JButton("Connect");
		btnConnect.setBackground(Color.red);
		//connect/disconnect drone
		btnConnect.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				writeLog("Button pressed: Connect/Disconnect Drone");
				if (drone == null){
					//initialize new drone object and dispatcher for manual control with keyboard
					drone = new ARDrone("192.168.1.1",null);
					drone.setSpeed(droneSpeed);
					dispatcher = new MyDispatcher(drone);
				}
				if(!drone.getCommandManager().isConnected()){
					//establish drone connection
					writeLog("Trying to connect to drone");
					drone.start();
					//activate manual control with keyboard
					KeyboardFocusManager manager = KeyboardFocusManager.getCurrentKeyboardFocusManager();
			        manager.addKeyEventDispatcher(dispatcher);
			        //get battery status
			        drone.getNavDataManager().addBatteryListener(batteryListener);
			        
			        //update GUI
			        btnConnect.setText("Disconnect");
					btnConnect.setBackground(Color.green);
			        btnReset.setEnabled(true);
			        btnTakeOff.setEnabled(true);
			        btnLanding.setEnabled(true);
			        btnEmergency.setEnabled(true);
			        writeLog("Drone connected");
				}else{
					//stop drone connection
					drone.stop();
					drone = null;
					//stop manual control with keyboard
					KeyboardFocusManager manager = KeyboardFocusManager.getCurrentKeyboardFocusManager();
			        manager.removeKeyEventDispatcher(dispatcher);
			        
			        //update GUI
			        btnConnect.setText("Connect");
					btnConnect.setBackground(Color.red);
			        btnReset.setEnabled(false);
			        btnTakeOff.setEnabled(false);
			        btnLanding.setEnabled(false);
			        btnEmergency.setEnabled(false);
			        writeLog("Drone disconnected");
				}
			}
		});
		
		plnDrone1_1.add(btnConnect);
		
		btnReset = new JButton("Reset");
		btnReset.setEnabled(false);
		//sending reset-command to drone
		btnReset.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				writeLog("Button pressed: Drone reset");
				if (drone != null)
					drone.reset();
					writeLog("New drone command by GUI: reset");
			}
		});
		plnDrone1_1.add(btnReset);
		
		btnTakeOff = new JButton("Take Off");
		btnTakeOff.setEnabled(false);
		//sending takeOff-command to drone
		btnTakeOff.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				writeLog("Button pressed: Drone take off");
				if (drone != null){
					drone.takeOff();
					writeLog("New drone command by GUI: take off");
				}
			}
		});
		plnDrone1_1.add(btnTakeOff);
		
		btnLanding = new JButton("Landing");
		btnLanding.setEnabled(false);
		//sending landing-command to drone
		btnLanding.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				writeLog("Button pressed: Drone landing");
				if (drone != null){
					drone.landing();
					writeLog("New drone command by GUI: landing");
				}
			}
		});
		plnDrone1_1.add(btnLanding);
		
		JPanel plnDrone1_2 = new JPanel();
		GridBagConstraints gbc_plnDrone1_2 = new GridBagConstraints();
		gbc_plnDrone1_2.fill = GridBagConstraints.BOTH;
		gbc_plnDrone1_2.gridx = 0;
		gbc_plnDrone1_2.gridy = 1;
		plnDrone1.add(plnDrone1_2, gbc_plnDrone1_2);
		plnDrone1_2.setLayout(new GridLayout(1, 1, 0, 0));
		
		
		btnEmergency = new JButton("EMERGENCY");
		btnEmergency.setEnabled(false);
		//sending emergency-command to drone
		btnEmergency.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				writeLog("Button pressed: Drone EMERGENCY");
				if (drone != null){
					drone.reset();
					writeLog("New drone command by GUI: EMERGENCY");
				}
			}
		});
		plnDrone1_2.add(btnEmergency);
		btnEmergency.setForeground(Color.RED);
		btnEmergency.setFont(new Font("Tahoma", Font.BOLD, 18));
		
		JPanel plnDrone2 = new JPanel();
		pnlDrone.add(plnDrone2);
		GridBagLayout gbl_plnDrone2 = new GridBagLayout();
		gbl_plnDrone2.columnWidths = new int[] {100, 0};
		gbl_plnDrone2.rowHeights = new int[] {40, 40, 0};
		gbl_plnDrone2.columnWeights = new double[]{1.0, Double.MIN_VALUE};
		gbl_plnDrone2.rowWeights = new double[]{1.0, 1.0, Double.MIN_VALUE};
		plnDrone2.setLayout(gbl_plnDrone2);
		
		JPanel plnDrone2_1 = new JPanel();
		GridBagConstraints gbc_plnDrone2_1 = new GridBagConstraints();
		gbc_plnDrone2_1.insets = new Insets(0, 0, 5, 0);
		gbc_plnDrone2_1.fill = GridBagConstraints.BOTH;
		gbc_plnDrone2_1.gridx = 0;
		gbc_plnDrone2_1.gridy = 0;
		plnDrone2.add(plnDrone2_1, gbc_plnDrone2_1);
		plnDrone2_1.setLayout(new FlowLayout(FlowLayout.CENTER, 5, 5));
		
		JLabel lblBattery = new JLabel("Battery:");
		plnDrone2_1.add(lblBattery);
		
		JPanel plnDrone2_2 = new JPanel();
		GridBagConstraints gbc_plnDrone2_2 = new GridBagConstraints();
		gbc_plnDrone2_2.fill = GridBagConstraints.BOTH;
		gbc_plnDrone2_2.gridx = 0;
		gbc_plnDrone2_2.gridy = 1;
		plnDrone2.add(plnDrone2_2, gbc_plnDrone2_2);
		plnDrone2_2.setLayout(new FlowLayout(FlowLayout.CENTER, 5, 5));
		
		prgBattery = new JProgressBar();
		plnDrone2_2.add(prgBattery);
		prgBattery.setStringPainted(true);
		prgBattery.setPreferredSize( new Dimension (80, 30));
		
		
		JPanel pnlBCI = new JPanel();
		pnlBCI.setBorder(new TitledBorder(null, "BCI-Control", TitledBorder.LEADING, TitledBorder.TOP, null, null));
		GridBagConstraints gbc_pnlBCI = new GridBagConstraints();
		gbc_pnlBCI.fill = GridBagConstraints.BOTH;
		gbc_pnlBCI.insets = new Insets(0, 0, 5, 0);
		gbc_pnlBCI.gridx = 0;
		gbc_pnlBCI.gridy = 1;
		frmBciDroneControl.getContentPane().add(pnlBCI, gbc_pnlBCI);
		GridBagLayout gbl_pnlBCI = new GridBagLayout();
		gbl_pnlBCI.columnWidths = new int[] {120, 380};
		gbl_pnlBCI.rowHeights = new int[] {80};
		gbl_pnlBCI.columnWeights = new double[]{1.0, 1.0};
		gbl_pnlBCI.rowWeights = new double[]{1.0};
		pnlBCI.setLayout(gbl_pnlBCI);
		
		JPanel pnlBCI1 = new JPanel();
		GridBagConstraints gbc_pnlBCI1 = new GridBagConstraints();
		gbc_pnlBCI1.insets = new Insets(0, 0, 0, 5);
		gbc_pnlBCI1.fill = GridBagConstraints.BOTH;
		gbc_pnlBCI1.gridx = 0;
		gbc_pnlBCI1.gridy = 0;
		pnlBCI.add(pnlBCI1, gbc_pnlBCI1);
		GridBagLayout gbl_pnlBCI1 = new GridBagLayout();
		gbl_pnlBCI1.columnWidths = new int[] {120};
		gbl_pnlBCI1.rowHeights = new int[] {40, 40};
		gbl_pnlBCI1.columnWeights = new double[]{1.0};
		gbl_pnlBCI1.rowWeights = new double[]{1.0, 1.0};
		pnlBCI1.setLayout(gbl_pnlBCI1);
		
		JPanel pnlBCI1_1 = new JPanel();
		GridBagConstraints gbc_pnlBCI1_1 = new GridBagConstraints();
		gbc_pnlBCI1_1.insets = new Insets(0, 0, 5, 0);
		gbc_pnlBCI1_1.fill = GridBagConstraints.BOTH;
		gbc_pnlBCI1_1.gridx = 0;
		gbc_pnlBCI1_1.gridy = 0;
		pnlBCI1.add(pnlBCI1_1, gbc_pnlBCI1_1);
		pnlBCI1_1.setLayout(new GridLayout(1, 1, 0, 0));
		
		
		JPanel pnlBCI1_2 = new JPanel();
		GridBagConstraints gbc_pnlBCI1_2 = new GridBagConstraints();
		gbc_pnlBCI1_2.fill = GridBagConstraints.BOTH;
		gbc_pnlBCI1_2.gridx = 0;
		gbc_pnlBCI1_2.gridy = 1;
		pnlBCI1.add(pnlBCI1_2, gbc_pnlBCI1_2);
		pnlBCI1_2.setLayout(new GridLayout(1, 1, 0, 0));
		
		btnActiviateControl = new JButton("Activate Control");
		btnActiviateControl.setBackground(new Color(240, 240, 240));
		btnActiviateControl.setEnabled(false);
		//activate/deactivate BCI drone control when drone is connected
		btnActiviateControl.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				writeLog("Button pressed: BCI control activate/stop");
				if(drone != null && !acquisitionClient.getEnableControl()){
					//activate BCI drone control
					acquisitionClient.setDrone(drone);
					acquisitionClient.setEnableControl(true);
					//update GUI
					btnActiviateControl.setBackground(Color.green);
					btnActiviateControl.setText("Stop Control");
					writeLog("BCI control for drone activated");
				}else{
					//deactivate BCI drone control
					acquisitionClient.setDrone(null);
					acquisitionClient.setEnableControl(false);
					drone.hover();
					//update GUI
					btnActiviateControl.setBackground(Color.red);
					btnActiviateControl.setText("Activate Control");
					writeLog("BCI control for drone stopped");
				}
			}
		});
		pnlBCI1_2.add(btnActiviateControl);
		
		JPanel pnlBCI2 = new JPanel();
		pnlBCI2.setLayout(null);
		GridBagConstraints gbc_pnlBCI2 = new GridBagConstraints();
		gbc_pnlBCI2.fill = GridBagConstraints.BOTH;
		gbc_pnlBCI2.gridx = 1;
		gbc_pnlBCI2.gridy = 0;
		pnlBCI.add(pnlBCI2, gbc_pnlBCI2);
		
		//graphical visualization of BCI drone control commands
		lblLeft = new JLabel("");
		lblLeft.setEnabled(false);
		lblLeft.setBounds(73, 20, 88, 56);
		lblLeft.setIcon(new ImageIcon(DroneControlGUI.class.getResource("/images/left.png")));
		pnlBCI2.add(lblLeft);
		
		lblIdle = new JLabel("");
		lblIdle.setEnabled(false);
		lblIdle.setBounds(177, 35, 29, 29);
		lblIdle.setIcon(new ImageIcon(DroneControlGUI.class.getResource("/images/idle.png")));
		pnlBCI2.add(lblIdle);
		
		lblRight = new JLabel("");
		lblRight.setEnabled(false);
		lblRight.setBounds(222, 20, 88, 56);
		lblRight.setIcon(new ImageIcon(DroneControlGUI.class.getResource("/images/right.png")));
		pnlBCI2.add(lblRight);
		
		txtLeft = new JTextField();
		txtLeft.setEditable(false);
		txtLeft.setHorizontalAlignment(SwingConstants.RIGHT);
		txtLeft.setFont(new Font("Tahoma", Font.BOLD, 16));
		txtLeft.setBounds(12, 35, 49, 29);
		txtLeft.setText("0");
		pnlBCI2.add(txtLeft);
		txtLeft.setColumns(10);
		
		
		txtRight = new JTextField();
		txtRight.setEditable(false);
		txtRight.setHorizontalAlignment(SwingConstants.LEFT);
		txtRight.setText("0");
		txtRight.setFont(new Font("Tahoma", Font.BOLD, 16));
		txtRight.setColumns(10);
		txtRight.setBounds(322, 35, 49, 29);
		pnlBCI2.add(txtRight);
		
		JPanel pnlSettings = new JPanel();
		pnlSettings.setBorder(new TitledBorder(null, "Settings", TitledBorder.LEADING, TitledBorder.TOP, null, null));
		GridBagConstraints gbc_pnlSettings = new GridBagConstraints();
		gbc_pnlSettings.fill = GridBagConstraints.BOTH;
		gbc_pnlSettings.insets = new Insets(0, 0, 5, 0);
		gbc_pnlSettings.gridx = 0;
		gbc_pnlSettings.gridy = 2;
		frmBciDroneControl.getContentPane().add(pnlSettings, gbc_pnlSettings);
		pnlSettings.setLayout(new GridLayout(3, 2, 0, 0));
		
		//set drone speed
		JLabel lblSpeed = new JLabel("Speed (% of maximal speed):");
		pnlSettings.add(lblSpeed);
		
		spnSpeed = new JSpinner();
		//report any change of field
		JComponent comp = spnSpeed.getEditor();
		JFormattedTextField field = (JFormattedTextField) comp.getComponent(0);
		DefaultFormatter formatter = (DefaultFormatter) field.getFormatter();
		formatter.setCommitsOnValidEdit(true);
		
		//get new speed value on change, tell drone and acquisitionClient
		spnSpeed.addChangeListener(new ChangeListener() {
			@Override
			public void stateChanged(ChangeEvent e) {
				droneSpeed = (int)spnSpeed.getValue();
				if (drone != null)
					drone.setSpeed(droneSpeed);
				if (acquisitionClient != null)
					acquisitionClient.setDroneSpeed(droneSpeed);
				writeLog("Setting changed: Drone speed is now " + droneSpeed + "%");
			}
		});
		
		spnSpeed.setModel(new SpinnerNumberModel(10, 0, 100, 1));
		spnSpeed.setValue(droneSpeed);
		pnlSettings.add(spnSpeed);
		
		//set drone forward speed (on BCI control)
		JLabel lblForwardSpeed = new JLabel("Forward speed on BCI control (% of speed):");
		pnlSettings.add(lblForwardSpeed);
		
		spnForwardSpeed = new JSpinner();
		//report any change of field
		comp = spnForwardSpeed.getEditor();
		field = (JFormattedTextField) comp.getComponent(0);
		formatter = (DefaultFormatter) field.getFormatter();
		formatter.setCommitsOnValidEdit(true);
		
		//get new forward speed value on change, tell acquisitionClient
		spnForwardSpeed.addChangeListener(new ChangeListener() {
			@Override
			public void stateChanged(ChangeEvent e) {
				droneForwardSpeed = (int)spnForwardSpeed.getValue();
				if(acquisitionClient != null){
					acquisitionClient.setDroneForwardSpeed(-(droneSpeed * droneForwardSpeed)/100);
				}	
				writeLog("Setting changed: Drone forward speed is now " + droneForwardSpeed + "%");
			}
		});
				
		spnForwardSpeed.setModel(new SpinnerNumberModel(0, 0, 100, 5));
		pnlSettings.add(spnForwardSpeed);
		
		//set trigger threshold for direction control
		JLabel lblTriggerThreshold = new JLabel("Trigger Threshold:");
		pnlSettings.add(lblTriggerThreshold);
		
		spnTriggerThreshold = new JSpinner();
		//report any change of field
		comp = spnTriggerThreshold.getEditor();
		field = (JFormattedTextField) comp.getComponent(0);
		formatter = (DefaultFormatter) field.getFormatter();
		formatter.setCommitsOnValidEdit(true);
		
		//get new trigger threshold value on change, tell acquisitionClient
		spnTriggerThreshold.addChangeListener(new ChangeListener() {
			@Override
			public void stateChanged(ChangeEvent e) {
				triggerThreshold = (double)spnTriggerThreshold.getValue();
				if(acquisitionClient != null)
					acquisitionClient.setThreshold(triggerThreshold);
				writeLog("Setting changed: Trigger threshold is now " + triggerThreshold + "%");
			}
		});
		
		spnTriggerThreshold.setModel(new SpinnerNumberModel(80.0, 50.0, 100.0, 1.0));
		spnTriggerThreshold.setValue(triggerThreshold);
		pnlSettings.add(spnTriggerThreshold);
		
		//create/cancel acquisition client for getting current BCI values 
		btnConnect_1 = new JButton("Connect");
		btnConnect_1.setBackground(Color.red);
		btnConnect_1.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				writeLog("Button pressed: BCI control connect/disconnect");
				if(acquisitionClient == null || !acquisitionClient.isConnected()){
					//create, configure and start new acquisition client
					writeLog("Trying to connect to BCI acquisition client");
					acquisitionClient = new BCIAcquisitionClient(txtLeft, txtRight, lblLeft, lblIdle, lblRight, 5678, logWriter);
					acquisitionClient.setThreshold(triggerThreshold);
					acquisitionClient.setDroneSpeed(droneSpeed);
					acquisitionClient.setDroneForwardSpeed(droneForwardSpeed);
					acquisitionClient.execute();
					
					if (acquisitionClient.isConnected())
					{
						//update GUI
						btnActiviateControl.setBackground(Color.red);
						btnActiviateControl.setEnabled(true);			
						btnConnect_1.setText("Disconnect");
						btnConnect_1.setBackground(Color.green);
						writeLog("BCI acquisition client connection established");
					}
					else{
						//cancel acquisition client
						acquisitionClient.cancel(false);
						acquisitionClient = null;
						writeLog("BCI acquisition client connection failed");
						
						//update GUI
						btnActiviateControl.setBackground(null);
						btnActiviateControl.setText("Activate Control");
						btnActiviateControl.setEnabled(false);
						btnConnect_1.setText("Connect");
						btnConnect_1.setBackground(Color.red);
					}
				}
				else{
					//cancel acquisition client
					acquisitionClient.cancel(false);
					acquisitionClient = null;
					
					//update GUI
					btnActiviateControl.setBackground(null);
					btnActiviateControl.setText("Activate Control");
					btnActiviateControl.setEnabled(false);
					btnConnect_1.setText("Connect");
					btnConnect_1.setBackground(Color.red);
					writeLog("BCI acquisition client connection disabled");
				}
			}
		});
		pnlBCI1_1.add(btnConnect_1);
		
		writeLog("Finished building GUI");
	}

	//getting current battery values from drone, update ProgressBar on change
	private BatteryListener batteryListener = new BatteryListener() {
		public void voltageChanged(int vbat_raw){
			
		}
		public void batteryLevelChanged(int batteryLevel)		{
			if (batteryLevel != prgBattery.getValue())			{
				prgBattery.setValue(batteryLevel);
				writeLog("Drone battery level changed to " + batteryLevel + "%");
			}
		}
	};

	//grab keyboard input for manual drone control
	private class MyDispatcher implements KeyEventDispatcher {
		private ARDrone drone;
		 
		public MyDispatcher(ARDrone drone){
			this.drone = drone;
		}
		  
		@Override
			public boolean dispatchKeyEvent(KeyEvent e) {
				if (e.getID() == KeyEvent.KEY_PRESSED) {
					//generate command when key is pressed
					int key = e.getKeyCode();
					handleCommand(key, drone);
				}
				else if (e.getID() == KeyEvent.KEY_RELEASED) {
					//enter hover mode when key is released
					drone.hover();
					writeLog("New drone command by keyboard: hover");
				}
				else if (e.getID() == KeyEvent.KEY_TYPED) {
		    	  
				}
				return false;
		  }
	}

	//triggers drone commands based on keyboard inputs 
	private void handleCommand(int key, ARDrone drone){
		String direction = "";
		
		switch (key){
			case KeyEvent.VK_A:
				drone.goLeft();
				direction = "left";
				break;
			case KeyEvent.VK_D:
				drone.goRight();
				direction = "right";
				break;
			case KeyEvent.VK_W:
				drone.forward();
				direction = "forward";
				break;
			case KeyEvent.VK_S:
				drone.backward();
				direction = "backward";
				break;
			case KeyEvent.VK_RIGHT:
				drone.spinRight();
				direction = "spin right";
				break;
			case KeyEvent.VK_LEFT:
				drone.spinLeft();
				direction = "spin left";
				break;
			case KeyEvent.VK_UP:
				drone.up();
				direction = "up";
				break;
			case KeyEvent.VK_DOWN:
				drone.down();
				direction = "down";
				break;
			case KeyEvent.VK_SPACE:
				drone.reset();
				direction = "emergency";
				break;
			case KeyEvent.VK_E:
				drone.landing();
				direction = "landing";
				break;
		}
		writeLog("New drone command by keyboard: " + direction);
	}
	
	//add source to log
	private void writeLog(String t){
		logWriter.writeLog("DroneControlGUI", t);
	}
}
