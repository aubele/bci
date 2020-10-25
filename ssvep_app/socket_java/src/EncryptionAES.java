import javax.crypto.Cipher;
import javax.crypto.Mac;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.MessageDigest;
import java.security.SecureRandom;
/**
 * Created by Florian Klein (Email: florian.klein1@hs-augsburg.de)
 * on behalf of University of Applied Sciences 
 * during BCI (Brain-Computing-Interface) project
 * 
 * @author Florian Klein
 *
 */

public class EncryptionAES {
		
       	/* static byte[] encryptionKey = {0x30, 0x31, 0x032, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f}; */
	
        static byte[] encryptionKey = new byte [] {'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'};
		static byte[] IV = encryptionKey;

		
        public static byte[] encrypt(byte[] plainData)
                throws Exception {
       
            Cipher cipher = Cipher.getInstance("AES/CBC/NoPadding");
            SecretKeySpec key = new SecretKeySpec(encryptionKey, "AES");
            cipher.init(Cipher.ENCRYPT_MODE, key, new IvParameterSpec(IV));
            return cipher.doFinal(plainData);
            
        }
        
}