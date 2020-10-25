package com.bci.smarthome;

/**
 * Created by Florian Klein (Email: florian.klein1@hs-augsburg.de)
 * on behalf of University of Applied Sciences 
 * during BCI (Brain-Computing-Interface) project
 * 
 * @author Florian Klein
 *
 */

public class HexToBytes {
	
	/* Method to transfer the current String into Hex-Bytes*/
	public static byte[] hexStringToByteArray(String hexString) {
		
        int len = hexString.length();
        byte[] data = new byte[len/2];

        for(int i = 0; i < len; i+=2){
            data[i/2] = (byte) ((Character.digit(hexString.charAt(i), 16) << 4) + Character.digit(hexString.charAt(i+1), 16));
        }

        return data;
	}	

}
