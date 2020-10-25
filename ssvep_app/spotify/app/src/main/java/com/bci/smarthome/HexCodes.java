package com.bci.smarthome;

/**
 * Created by Florian Klein (Email: florian.klein1@hs-augsburg.de)
 * on behalf of University of Applied Sciences 
 * during BCI (Brain-Computing-Interface) project
 * 
 * @author Florian Klein
 *
 */

public class HexCodes {
	
	/*Customer Code of Aldi*/
	private String customerCode = "C2";
			
	/*Authentication-Code of Aldi */
	private String authenticationCode = "92DD";
	
	/* Main States of Device */
	private String MAIN_STATE_ON = "0000FFFF";
	private String MAIN_STATE_OFF = "000000FF";
	private String state = ""; // nothing before initialization
	
	
	public HexCodes(String customerCode, String authCode, String state){
		
	}
	
	public String getCompanyCode(){
		return this.customerCode;
	}
	
	public String getAuthCode() {
		return this.authenticationCode;
	}
	
	public String getMainState() {
		return this.state;
	}
	
	public void setSocketOn(){
		this.state = MAIN_STATE_ON;
	}
	
	public void setSocketOff(){
		this.state = MAIN_STATE_OFF;
	}
	
	
	public String getFinalHash() {
		return "00" + "FF" +"FF" + getCompanyCode() + "11" + getAuthCode() + "01" + getMainState() + "04040404";
	}
}
