import java.io.DataInputStream;
import java.io.EOFException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import javax.swing.JLabel;
import javax.swing.JTextField;
import javax.swing.SwingWorker;
import de.yadrone.base.ARDrone;
import java.net.*;

public class BCIAcquisitionClient extends
SwingWorker<Double ,Double>{

	//Variables for Drone control
	private ARDrone drone;
	private int droneSpeed;
	private int droneForwardSpeed;
	private boolean enableControl = false;
	private double threshold;
	private enum Command {
		left, right, idle
	}
	private Command CurrentCommand, LastCommand = Command.idle;
	
	//Variables for directions
	private double left;
	private double right;
	
	//Variables for GUI values
	private JTextField lefttxt;
	private JTextField righttxt;
	private JLabel leftlbl;
	private JLabel idlelbl;
	private JLabel rightlbl;
	
	//Variables for TCP connection to OpenVibe
	private int port;
	private Socket clientSocket;
	private DataInputStream inputStream;
	private boolean connected = false;
	
	//Variables for Logging
	private LogWriter logWriter;
	
	//GETTER
	public boolean getEnableControl(){
		return enableControl;
	}
	
	public boolean isConnected(){
		return connected;
	}
	
	//SETTER
	public void setThreshold(double threshold){
		this.threshold = threshold;
	}
	
	public void setEnableControl(boolean enableControl){
		this.enableControl = enableControl;
	}
	
	public void setDrone (ARDrone drone){
		this.drone = drone;
	}
	
	public void setDroneSpeed(int droneSpeed){
		this.droneSpeed = droneSpeed;
	}
	
	public void setDroneForwardSpeed(int droneForwardSpeed){
		this.droneForwardSpeed = droneForwardSpeed;
	}
	
	//Initialize, connect to TCP-server, read header and set connection status
	public BCIAcquisitionClient(JTextField lefttxt, JTextField righttxt, JLabel leftlbl, JLabel idlelbl, JLabel rightlbl, int port, LogWriter logWriter){
		this.lefttxt = lefttxt;
		this.righttxt = righttxt;
		this.leftlbl = leftlbl;
		this.idlelbl = idlelbl;
		this.rightlbl = rightlbl;
		this.port = port;
		this.logWriter = logWriter;
		
		writeLog("BCI Acquisition Client started");
		
		// try to connect to TCP-server
		writeLog("Trying to connect to TCP-Server");
		try {
		  clientSocket = new Socket("localhost", this.port);
		  inputStream = new DataInputStream(clientSocket.getInputStream());
  	  
		  // read header info
		  byte headerinfo[] = new byte[4];
		  writeLog("---Reading header information");
		  inputStream.readFully(headerinfo);
		  writeLog("Format: "+ (int)headerinfo[0]);
		  inputStream.readFully(headerinfo);
		  writeLog("Endianess: "+ (int)headerinfo[0]);
		  inputStream.readFully(headerinfo);
		  writeLog("Sampling frequency : "+ (int)headerinfo[0]);
		  inputStream.readFully(headerinfo);
		  writeLog("Number of channels: "+ (int)headerinfo[0]);
		  inputStream.readFully(headerinfo);
		  writeLog("Samples per chunk: "+ (int)headerinfo[0]);
		  headerinfo = new byte[12];
		  inputStream.readFully(headerinfo);
		  writeLog("Reserved: "+ (int)headerinfo[0]);
		  writeLog("---End of Header");
		} catch (UnknownHostException e) {
			e.printStackTrace();
			writeLog("TCP-Connection failed: Unknown host");
			return;
		} catch (IOException e) {
			e.printStackTrace();
			writeLog("TCP-Connection failed: IO Exception");
			return;
		}
		writeLog("TCP-Connection established");
		connected = true;
	}
	
	//Convert data from OpenVibe to Double
	private static double toDouble(byte[] bytes) {
		return ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).getDouble();
	}

	//Background-worker: collecting direction data, updating GUI, building command for Drone movement, sending command when control is activated and command has changed
	@Override
	protected Double doInBackground() throws Exception {
		byte data[] = new byte[8];
		int  speedX=0, speedZ=0, speedSpin=0;

		try {
			while(!isCancelled() && connected){
				//read value for first class
				inputStream.readFully(data);
				left = toDouble(data)*100;
				//read value for second class
				inputStream.readFully(data);
				right = toDouble(data)*100;
				
				//classify values, update GUI visuals, build commands
				if(left > threshold){
					idlelbl.setEnabled(false);
					leftlbl.setEnabled(true);
					rightlbl.setEnabled(false);
					speedSpin = -droneSpeed;
					CurrentCommand = Command.left;
					//writeLog("Left command");
				}else if(right > threshold){
					leftlbl.setEnabled(false);
					idlelbl.setEnabled(false);
					rightlbl.setEnabled(true);
					speedSpin = droneSpeed;
					CurrentCommand = Command.right;
					//writeLog("Right command");
				}else{
					leftlbl.setEnabled(false);
					idlelbl.setEnabled(true);
					rightlbl.setEnabled(false);
					speedSpin = 0;
					CurrentCommand = Command.idle;
					//writeLog("No command");
				}
				
				//update current value in GUI
				lefttxt.setText(String.format("%1$.1f", left));
				righttxt.setText(String.format("%1$.1f", right)); 			
	        	
				//send command when control is activated and command has changed
				if(enableControl && drone != null && CurrentCommand != LastCommand){
					if (!(speedX == 0 && droneForwardSpeed == 0 && speedZ == 0 && speedSpin == 0)){
						drone.move3D(speedX, droneForwardSpeed, speedZ, speedSpin);
						
						writeLog("New drone command by BCI control: move3D " + speedX + " " + droneForwardSpeed + " " + speedZ + " " + speedSpin);
					}
					else{
						drone.hover();
						writeLog("New drone command by BCI control: hover");
					}
					LastCommand = CurrentCommand;
				}
			}
		} catch (EOFException e){
			writeLog("TCP-Connection lost");
			e.printStackTrace();
			connected = false;
		} catch (IOException e) {
			writeLog("TCP-Connection terminated");
			e.printStackTrace();
			connected = false;
		} finally {
			//close socket
			clientSocket.close();
			writeLog("TCP-Connection closed");
			
			//reset GUI when finished
			idlelbl.setEnabled(false);
			leftlbl.setEnabled(false);
			rightlbl.setEnabled(false);
			lefttxt.setText("0");
			righttxt.setText("0");
			
			//exit
			writeLog("BCI Acquisition Client stopped");
		}
		return null;
	}
	
	//add source to log
	private void writeLog(String t){
		logWriter.writeLog("BCIAcquisitionClient", t);
	}
	

}
