import java.text.SimpleDateFormat;
import java.util.Date;

public class LogWriter {
	public LogWriter(){

	}
	
	public void writeLog(String s, String t){
		System.out.println(currentTimestamp() + " " + s + ": " + t);
	}
	
	private String currentTimestamp(){
		String timeStamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
		return timeStamp;
	}

}
