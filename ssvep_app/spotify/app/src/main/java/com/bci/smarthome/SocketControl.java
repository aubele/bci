package com.bci.smarthome;

import java.io.IOException;
import java.net.SocketException;

/**
 * Created by Florian Klein (Email: florian.klein1@hs-augsburg.de) on behalf of
 * University of Applied Sciences during BCI (Brain-Computing-Interface) project
 *
 * @author Florian Klein
 *
 */

public class SocketControl {

	/* Local variables and constants for Hash */

	/* Key for the AES-Cryptography-Algorithm */
	private final static String aesKey = "0123456789abcdef";

	/* MAC-Address of the Socket Device */
	private final static String macAddress = "009569A68C7A";



/* --------------------------------------------------------------------------------------------------------------
 * --------------------------------------------------------------------------------------------------------------
 * --------------------------------------------------------------------------------------------------------------
 */


	/* Turn Socket-Device On */
	public byte [] turnSocketDeviceOn() throws Throwable {
		HexCodes information = new HexCodes("C2,", "92DD", "0000FFFF");
		information.setSocketOn();
		String hexString = information.getFinalHash();
		HexToBytes converter = new HexToBytes();
		byte[] transferredBytes = HexToBytes.hexStringToByteArray(hexString);
		EncryptionAES crypto = new EncryptionAES();
		byte[] cipher = EncryptionAES.encrypt(transferredBytes);
		byte[] status = sendFinalHash(cipher);

		return status ;
	}

	/* Turn Socket-Device Off */
	public byte [] turnSocketDeviceOff() throws SocketException, IOException, Exception, Throwable {
		HexCodes information = new HexCodes("C2,", "92DD", "000000FF");
		information.setSocketOff();
		String hexString = information.getFinalHash();
		HexToBytes converter = new HexToBytes();
		byte[] transferredBytes = HexToBytes.hexStringToByteArray(hexString);
		EncryptionAES crypto = new EncryptionAES();
		byte[] cipher = EncryptionAES.encrypt(transferredBytes);
		byte [] status = sendFinalHash(cipher);

		return status;

	}


/* --------------------------------------------------------------------------------------------------------------
 * --------------------------------------------------------------------------------------------------------------
 * --------------------------------------------------------------------------------------------------------------
 */



	public byte [] sendFinalHash(byte [] cipher) throws SocketException, IOException, Exception, Throwable{

		/* Creating the Final-Hash; this one will be send to the Socket-Device via UDP-DatagramSocket */
		String finalHash = "01" + "40" + macAddress + "10";
		byte [] messageBytes = HexToBytes.hexStringToByteArray(finalHash);

		/* Putting together both generated parts the crypted one and the uncrypted part of the hash */
		byte [] endMessage = new byte[messageBytes.length + cipher.length];
		System.arraycopy(messageBytes, 0, endMessage, 0, messageBytes.length);
		System.arraycopy(cipher, 0, endMessage, messageBytes.length, cipher.length);

		/* Just another method to make sure everything is still correct */
		System.out.print("endMessage:  ");
		for (int i = 0; i < endMessage.length; i++) {
			// System.out.print(new Integer(cipher[i]) + " ");
			byte b = endMessage[i];
			System.out.print(String.format("%02x", b & 0xFF) + " ");
		}

        /*
		Send Hash to Device establishing a new UDP-Connection
		UDPClient.sentToSocketPlug(endMessage);
		*/

		return endMessage;
	}


}
