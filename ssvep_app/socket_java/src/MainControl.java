/**
 * Created by Florian Klein (Email: florian.klein1@hs-augsburg.de)
 * on behalf of University of Applied Sciences 
 * during BCI (Brain-Computing-Interface) project
 * 
 * @author Florian Klein
 *
 */

public class MainControl {
	public static void main(String []args) throws Throwable{
		
		/* Key for the AES-Cryptography-Algorithm */
		String aesKey = "0123456789abcdef";
		
		/* MAC-Address of the Socket Device */
		String macAddress = "009569A68C7A";
		
		/* Establishing the data for the connection regarding  informations 
		 * of producerCode, authenticationCode and stateOfDevice */
		HexCodes information = new HexCodes("C2", "92DD", "000000FF");
		
		information.setSocketOn(); /*--> still changes needed to switch Socket on / off */
		String hexString = information.getFinalHash();
		System.out.println("String mit StandardInformationen :" + hexString);
	
		/* Routine to transfer the String with Hex-signs into a byte-ordered array */
		HexToBytes converter = new HexToBytes();
		byte [] transferredBytes = HexToBytes.hexStringToByteArray(hexString);
		
		/* Encrypting the bytes using AES 128 with CBC-mode and Padding */
		EncryptionAES crypto = new EncryptionAES();
        byte[] cipher = EncryptionAES.encrypt(transferredBytes);

        
        /* just a method to try if it is the correct hash until then */
        System.out.print("cipher:  ");
        for (int i = 0; i < cipher.length; i++) {
            // System.out.print(new Integer(cipher[i]) + " ");
            byte b = cipher[i];
            System.out.print(String.format("%02x", b & 0xFF) + " ");

        }
        System.out.println();

	
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
			
		/*Send Hash to Device establishing a new UDP-Connection */
		UDPClient.sentToSocketPlug(endMessage);
					
	}
	
}
