package com.bci.smarthome;

import android.util.Log;

/**
 * Created by Fabio Paul Aubele (Email: fabioaubele95@hotmail.de)
 * on behalf of Hochschule Augsburg (BCI-Projekt SS 2017)
 */

/**
 * public log-class which is used in both activities to make it smoother to log something on the console
 */
public class ConsoleLog {

    public void logStatusMain(String log) {
        logStatus("MainActivity", log);
    }
    public void logStatusConfig(String log) {
        logStatus("ConfigActivity", log);
    }
    public void logStatus(String activity, String log) {
        Log.d(activity, log);
    }

    public void logErrorMain(String log) {
        logError("MainActivity", log);
    }
    public void logErrorConfig(String log) {
        logError("ConfigActivity", log);
    }
    public void logError(String activity, String log) {
        Log.e(activity, log);
    }

}