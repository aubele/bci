import java.io.IOException;

import java.net.*;
/**
 * Created by Florian Klein (Email: florian.klein1@hs-augsburg.de)
 * on behalf of University of Applied Sciences 
 * during BCI (Brain-Computing-Interface) project
 * 
 * @author Florian Klein
 *
 */

class UDPClient{
	
		public static void sentToSocketPlug(byte [] endMessage) throws SocketException, IOException, Exception, Throwable{
			
			/* Check wether our aimed-PC is reachable for connection or not? */
			System.out.println();
			System.out.println("Status . " + InetAddress.getByName("192.168.43.13").isReachable(2000));
			System.out.println();
			
			/* Create a new Socket */
			DatagramSocket clientSocket = new DatagramSocket();
			
			/* Ip-Address of the device to send the message to */
			InetAddress ipAddress = InetAddress.getByName("192.168.43.13");
			
			
			/*Encoding the message to sequence of Bytes */
			byte [] yourmessage = endMessage;
			
			/*Send the data */
			DatagramPacket sendPacket = new DatagramPacket(yourmessage, yourmessage.length, ipAddress, 8530);
			clientSocket.send(sendPacket);

			
			/*End the connection to the socket */
			clientSocket.close();
			
		}
}