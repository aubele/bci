package com.bci.smarthome;

import android.animation.AnimatorSet;
import android.animation.ArgbEvaluator;
import android.animation.ValueAnimator;
import android.content.Context;
import android.os.AsyncTask;
import android.graphics.Color;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Collections;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;
import java.util.TreeMap;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

import com.spotify.sdk.android.player.Config;
import com.spotify.sdk.android.player.ConnectionStateCallback;
import com.spotify.sdk.android.player.Error;
import com.spotify.sdk.android.player.Player;
import com.spotify.sdk.android.player.PlayerEvent;
import com.spotify.sdk.android.player.Spotify;
import com.spotify.sdk.android.player.SpotifyPlayer;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

public class MainActivity extends AppCompatActivity implements
        SpotifyPlayer.NotificationCallback, ConnectionStateCallback, MqttCallback {

    //CONSTANTS

    /**
     * Instance for SocketControl class
     */
    private static final SocketControl startIt = new SocketControl();

    /**
     * Client ID, can be found under https://developer.spotify.com/my-applications/#!/
     */
    private static final String CLIENT_ID = "866a929469724a708d4cfe20a7d08656";

    /**
     * Example-Playlist
     */
    private static final String EXAMPLE_PLAYLIST = "spotify:user:spotify:playlist:37i9dQZF1DXcN1fAVSf7CR";

    /**
     * Dummy elements for now
     */
    private static final Action POWER_ON = new Action("Power on", 0);
    private static final Action POWER_OFF = new Action("Power off", 1);
    /**
     * Elements to control spotify
     */
    private static final Action PLAY_SONG = new Action("Play Song", 2);
    private static final Action NEXT_SONG = new Action("Next Song", 3);
    private static final Action PREVIOUS_SONG = new Action("Previous Song", 4);

    /**
     * UI controls which may only be enabled after the player has been initialized,
     * (or effectively, after the user has logged in).
     */
    private static final Map<Action, Method> REQUIRES_INITIALIZED_STATE;
    static {
        Map<Action, Method> result = new TreeMap<Action, Method>();
        try{
            result.put(PLAY_SONG, MainActivity.class.getDeclaredMethod("onPlayButton"));
            result.put(NEXT_SONG, MainActivity.class.getDeclaredMethod("onNextButtonClicked"));
            result.put(PREVIOUS_SONG, MainActivity.class.getDeclaredMethod("onPreviousButtonClicked"));
        } catch (Exception e) {
            e.printStackTrace();
        }
        REQUIRES_INITIALIZED_STATE = Collections.unmodifiableMap(result);
    }

    /**
     * UI controls which should only be enabled if the player is actively playing.
     */
    private static final Map<Action, Method> REQUIRES_PLAYING_STATE;
    static {
        Map<Action, Method> result = new TreeMap<Action, Method>();
        try{
            result.put(NEXT_SONG, MainActivity.class.getDeclaredMethod("onNextButtonClicked"));
            result.put(PREVIOUS_SONG, MainActivity.class.getDeclaredMethod("onPreviousButtonClicked"));
        } catch (Exception exc) {
            exc.printStackTrace();
        }
        REQUIRES_PLAYING_STATE = Collections.unmodifiableMap(result);
    }

    /**
     * Map element which holds all current active Actions
     */
    Map<Action, Method> allActions = new TreeMap<Action, Method>();

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    //FIELDS

    /**
     * Instance which is used for all log-calls
     */
    private final ConsoleLog log = new ConsoleLog();

    /**
     * Callback which is used by all spotifyPlayer actions
     */
    private final Player.OperationCallback mOperationCallback = new Player.OperationCallback() {
        @Override
        public void onSuccess() {
            log.logStatusMain("Callback says everything went well");
        }

        @Override
        public void onError(Error error) {
            log.logErrorMain("Callback says ERROR: " + error);
        }
    };

    /**
     * The player used by this activity. There is only ever one instance of the player,
     * which is owned by the {@link com.spotify.sdk.android.player.Spotify} class and refcounted.
     * This means that you may use the Player from as many Fragments as you want, and be
     * assured that state remains consistent between them.
     * <p/>
     * However, each fragment, activity, or helper class <b>must</b> call
     * {@link com.spotify.sdk.android.player.Spotify#destroyPlayer(Object)} when they are no longer
     * need that player. Failing to do so will result in leaked resources.
     */
    private SpotifyPlayer mPlayer;

    private enum PlayState {
        NOT_PLAYING, PLAYING, PAUSING
    }

    /**
     * Displays the playing state which allows to activate or deactivate some player interactions
     */
    private PlayState mCurrentPlayState = PlayState.NOT_PLAYING;

    /**
     * Index which shows the currently selected action (box in the middle)
     */
    private int currentIndex = 0;

    /**
     * Textviews which are displaying the label from the actions which are changing
     */
    private TextView previousText;
    private TextView currentText;
    private TextView nextText;

    // the third flashing box, which flashes with a frequenzy of 7.5 Hz and gets represented by
    // ImageView previousImage
    private ValueAnimator previousAnimation;
    private ImageView previousImage;
    final int freq1 = 5000/75;
    // the second flashing box, which flashes with a frequenzy of 10 Hz and gets represented by
    // ImageView currentImage
    private ValueAnimator currentAnimation;
    private ImageView currentImage;
    final int freq2 = 5000/100;
    // the first flashing box, which flashes with a frequenzy of 12.0 Hz and gets represented by
    // ImageView nextImage
    private ValueAnimator nextAnimation;
    private ImageView nextImage;
    final int freq3 = 5000/120;

    private AnimatorSet animatorSet = new AnimatorSet();


    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    //INIT

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        previousImage = (ImageView) findViewById(R.id.previousButton);
        currentImage = (ImageView) findViewById(R.id.currentButton);
        nextImage = (ImageView) findViewById(R.id.nextButton);

        // creates the flickering of the boxes
        initAllAnimator(Color.BLACK, Color.RED);
        // creates a mqtt connection
        establishMqtt();
        // init Player, which probably starts a new login callback
        initPlayer();
        // init the starting <action,method> map
        initMethodMap();
        // init TextViews for the update calls
        initTextViews();

        mCurrentPlayState = PlayState.NOT_PLAYING;
        // init all current Actions
        updateActionAvailability();
        updateActions();
    }

    private void initAllAnimator(Integer colorFrom, Integer colorTo) {
        previousAnimation = setOneAnimator(previousImage, freq1, colorFrom, colorTo);
        currentAnimation = setOneAnimator(currentImage, freq2, colorFrom, colorTo);
        nextAnimation = setOneAnimator(nextImage, freq3, colorFrom, colorTo);

        startAllAnimator();
    }

    private void establishMqtt() {
        String ip = getIntent().getStringExtra("IP");
        String port = getIntent().getStringExtra("PORT");
        String topic = getIntent().getStringExtra("TOPIC");

        mqttSSVEP(ip, port, topic);
    }

    private void initMethodMap(){
        try {
            allActions.put(POWER_ON, MainActivity.class.getDeclaredMethod("socketDeviceOn"));
            allActions.put(POWER_OFF, MainActivity.class.getDeclaredMethod("socketDeviceOff"));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void initTextViews(){
        previousText = (TextView)findViewById(R.id.previousText);
        currentText = (TextView)findViewById(R.id.currentText);
        nextText = (TextView)findViewById(R.id.nextText);
    }

    /**
     * Initializes the spotify player and returns if it was successful or not
     */
    private void initPlayer() {
        String accToken = getIntent().getStringExtra("ACCESS_TOKEN");

        Config playerConfig = new Config(this, accToken, CLIENT_ID);
        Spotify.getPlayer(playerConfig, this, new SpotifyPlayer.InitializationObserver() {
            @Override
            public void onInitialized(SpotifyPlayer spotifyPlayer) {
                mPlayer = spotifyPlayer;
                mPlayer.addConnectionStateCallback(MainActivity.this);
                mPlayer.addNotificationCallback(MainActivity.this);
                log.logStatusMain("Player successfully initialized");
            }

            @Override
            public void onError(Throwable throwable) {
                log.logErrorMain("Could not initialize player: " + throwable.getMessage());
            }
        });
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // UI-WHEEL


    private ValueAnimator setOneAnimator(final ImageView imageView, int freq, Integer colorFrom, Integer colorTo) {
        ValueAnimator animator = ValueAnimator.ofObject(new ArgbEvaluator(), colorFrom, colorTo);
        animator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
            @Override
            public void onAnimationUpdate(ValueAnimator animator) {
                imageView.setBackgroundColor((Integer) animator.getAnimatedValue());
            }
        });
        animator.setRepeatCount(ValueAnimator.INFINITE);
        animator.setRepeatMode(ValueAnimator.REVERSE);
        animator.setDuration(freq);
        return animator;
    }

    /**
     *
     */
    private void startAllAnimator() {
        // We put the three AnimatorSet together into a AnimatorSet to start them together
        animatorSet.playTogether(previousAnimation, currentAnimation,
                nextAnimation);
        animatorSet.start();
    }

    /**
     * Updates all the Action, so there is always the correct label displayed
     */
    private void updateActions() {
        if (allActions.size() > 0) {
            Action previousAction;
            Action currentAction ;
            Action nextAction;

            // get previous Action
            if (currentIndex > 0) {
                previousAction = (Action) allActions.keySet().toArray()[currentIndex - 1];
            } else {
                previousAction = (Action) allActions.keySet().toArray()[allActions.size() - 1];
            }
            // get next Action
            if (currentIndex < allActions.size() - 1) {
                nextAction = (Action) allActions.keySet().toArray()[currentIndex + 1];
            } else {
                nextAction = (Action) allActions.keySet().toArray()[0];
            }
            // get current Action
            currentAction = (Action) allActions.keySet().toArray()[currentIndex];

            // set the labels
            previousText.setText(previousAction.getLabel());
            currentText.setText(currentAction.getLabel());
            nextText.setText(nextAction.getLabel());
        }
    }

    /**
     * Triggers the 'previous Event', which allows to get to the previous action, gets called with
     * mqtt message 1
     * @param view parent view object
     */
    public void previousAction(View view) {
        log.logStatusMain("Previous Action triggered");
        currentIndex = (currentIndex > 0) ? currentIndex - 1 : allActions.size() - 1;
        updateActions();
    }

    /**
     * Triggers the 'next Event', which allows to get to the next action, gets called with mqtt
     * message 3
     * @param view parent view object
     */
    public void nextAction(View view) {
        log.logStatusMain("Next Action triggered");
        currentIndex = (currentIndex < (allActions.size() - 1)) ? currentIndex + 1 : 0;
        updateActions();
    }

    /**
     * Triggers the 'execute Event', which allows to execute the current action with reflection, gets
     * called with mqtt message 2
     * @param view parent view object
     */
    public void executeAction(View view) {
        log.logStatusMain("Execute Action triggered");
        if(allActions.size() > 0) {
            Context context = getApplicationContext();
            Action current = (Action) allActions.keySet().toArray()[currentIndex];
            CharSequence text = "Führe Aus: " + current.getLabel();
            int duration = Toast.LENGTH_SHORT;
            Toast toast = Toast.makeText(context, text, duration);
            toast.show();
            try {
                Method method = allActions.get(current);
                method.invoke(this);
            } catch (InvocationTargetException ITe) {
                ITe.printStackTrace();
            } catch (IllegalAccessException IAe) {
                IAe.printStackTrace();
            }
            updateActionAvailability();
            updateActions();
        }
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // UI EVENTS

    /**
     * Manages which action are displayed and active
     */
    private void updateActionAvailability(){
        // Set availability for the buttons who are reliant on the login
        boolean login = isLoggedIn();
        setActionAvailabilityForLogin(login);

        // Set availability for the buttons who are reliant on the playing state
        boolean playing = isPlaying();
        setActionAvailabilityForPlaying(playing);
    }

    private boolean isLoggedIn() {
        return mPlayer != null && mPlayer.isLoggedIn();
    }

    private boolean isPlaying() {
        return isLoggedIn() && mCurrentPlayState != null && mCurrentPlayState == PlayState.PLAYING;
    }

    /**
     * Decides if the action which are reliant on the login should be displayed or not
     * @param enable
     */
    private void setActionAvailabilityForLogin(boolean enable) {
        for (Map.Entry<Action, Method> entry : REQUIRES_INITIALIZED_STATE.entrySet()) {
            if (!allActions.containsKey(entry.getKey()) && enable) {
                allActions.put(entry.getKey(), entry.getValue());
            } else if (allActions.containsKey(entry.getKey()) && !enable) {
                allActions.remove(entry.getKey());
            }
        }
    }
    /**
     * Decides if the action which are reliant on the playing state should be displayed or not
     * @param enable
     */
    private void setActionAvailabilityForPlaying(boolean enable) {
        for (Map.Entry<Action, Method> entry : REQUIRES_PLAYING_STATE.entrySet()) {
            if (!allActions.containsKey(entry.getKey()) && enable) {
                allActions.put(entry.getKey(), entry.getValue());
            } else if (allActions.containsKey(entry.getKey()) && !enable) {
                allActions.remove(entry.getKey());
            }
        }
    }

    /**
     * Triggers the play events which a reliant on the current play state
     */
    private void onPlayButton(){
        switch (mCurrentPlayState) {
            case NOT_PLAYING:
                onStartPlaylist();
                mCurrentPlayState = PlayState.PLAYING;
                PLAY_SONG.setLabel("Pause Song");
                break;
            case PLAYING:
                onPausePlaylist();
                mCurrentPlayState = PlayState.PAUSING;
                PLAY_SONG.setLabel("Play Song");
                break;
            case PAUSING:
                onResumePlaylist();
                mCurrentPlayState = PlayState.PLAYING;
                PLAY_SONG.setLabel("Pause Song");
                break;
        }
    }

    /**
     * Starts the playlist and sets shuffle and repeat on true
     */
    private void onStartPlaylist() {
        log.logStatusMain("Now playing following URI: " + EXAMPLE_PLAYLIST);
        mPlayer.playUri(mOperationCallback, EXAMPLE_PLAYLIST, 0, 0);

        // set repeat a second later cause the player allActions does not seem to be que'd, so else it
        // won't work correctly in the current api version from spotify (current state: beta)
        Timer timer = new Timer();
        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                log.logStatusMain("Set repeat on " + true);
                mPlayer.setRepeat(mOperationCallback, true);
            }
        }, 1000);
        // same for shuffle
        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                log.logStatusMain("Set shuffle on " + true);
                mPlayer.setShuffle(mOperationCallback, true);
            }
        }, 2*1000);
    }

    private void onPausePlaylist(){
        log.logStatusMain("Pausing playlist");
        mPlayer.pause(mOperationCallback);
    }

    private void onResumePlaylist(){
        log.logStatusMain("Resuming playlist");
        mPlayer.resume(mOperationCallback);
    }

    private void onPreviousButtonClicked() {
        log.logStatusMain("Skip to previous song");
        mPlayer.skipToPrevious(mOperationCallback);
    }

    private void onNextButtonClicked() {
        log.logStatusMain("Skip to next song");
        mPlayer.skipToNext(mOperationCallback);
    }

    private void socketDeviceOn(){

        byte [] connectionInformation;
        // boolean connectionStatus = false; // needed when status works

        try{
            connectionInformation = startIt.turnSocketDeviceOn();
            new ClientSendHashTask().execute(connectionInformation);
            //connectionStatus = new ClientSendHashTask().doInBackground(); // modification necc.
            String label;
            /*
            if(connectionStatus == true){
                label = "Connection to the socket successfully established.";
            }else {
                label = "Connection to the socket could not be established!";
            }
            Toast connectionMessage = Toast.makeText(getApplicationContext(), label, Toast.LENGTH_SHORT);
            connectionMessage.show();
            */
        } catch (Throwable Tr) {
            Tr.printStackTrace();
        }
    }

    private void socketDeviceOff() {

        byte [] connectionInformation;
        //Boolean connectionStatus = false; // needed when status works

        try {
            connectionInformation = startIt.turnSocketDeviceOff();
            new ClientSendHashTask().execute(connectionInformation);
            //connectionStatus = new ClientSendHashTask().doInBackground();   //modification necc.
            String label;

            /*
            if(connectionStatus){
                label = "Successfully disconnected from the socket.";
            }else {
                label = "Disconnection from the socket wasn´t successfully";
            }
            Toast connectionMessage = Toast.makeText(getApplicationContext(), label, Toast.LENGTH_LONG);
            connectionMessage.show();
            */
        } catch (Throwable Tr) {
            Tr.printStackTrace();
        }
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // CALLBACK METHODS

    @Override
    public void onLoggedIn() {
        // can NOT happen in this activity, but still need to override it
        log.logStatusMain("User logged in");
    }

    @Override
    public void onLoggedOut() {
        // can NOT happen in this activity, but still need to override it
        log.logStatusMain("User logged out");
    }

    @Override
    public void onLoginFailed(Error i) {
        log.logErrorMain("Login failed");
    }

    @Override
    public void onTemporaryError() {
        log.logErrorMain("Temporary error occurred");
    }

    @Override
    public void onConnectionMessage(String message) {
        log.logStatusMain("Received connection message: " + message);
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // DESTRUCTION

    @Override
    protected void onDestroy() {
        Spotify.destroyPlayer(this);
        super.onDestroy();
    }

    @Override
    public void onPlaybackEvent(PlayerEvent playerEvent) {
        log.logStatusMain("Playback event received: " + playerEvent.name());
        switch (playerEvent) {
            // Handle event type as necessary
            default:
                break;
        }
    }

    @Override
    public void onPlaybackError(Error error) {
        log.logErrorMain("Playback error received: " + error.name());
        switch (error) {
            // Handle error type as necessary
            default:
                break;
        }
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // MQTT

    // Setting up the MQTT client
    MqttClient client;
    MemoryPersistence persistence = new MemoryPersistence();
    String clientId = "smartHome";

    // initialize the current_message as NULL state
    private String current_message = "0";


    /**
     * Constructor for the MQTT for SSVEP
     * Args:
     * String mqttIP: The IP of the Mosquitto Host
     * String mqttTopic: The Topic of MQTT to subscribe for
     */
    public void mqttSSVEP(String mqttIP, String port, String mqttTopic) {
        try {
            client = new MqttClient("tcp://" + mqttIP + ":" + port, clientId, persistence);
            client.connect();
            client.setCallback(this);
            client.subscribe(mqttTopic);
            log.logStatusMain("Connection established");
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void connectionLost(Throwable cause) {
        log.logErrorMain("Connection lost " + cause.toString());
    }

    private long currentTime;
    /**
     * This method handles the correct call for each mqtt message, mqtt messages should not be sent
     * to fast, else the thread management is not working correctly
     */
    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {
        // sets the message to the new message that arrives
        current_message = message.toString();
        log.logStatusMain("Message arrived: " + current_message);
        // wait for 5 seconds till the next message can be processed
        if(System.currentTimeMillis() - currentTime > 5000) {
            // without this method the views are not callable
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    switch (current_message) {
                        // previous
                        case "1":
                            // execute the correct event
                            previousAction(findViewById(R.id.previousButton));

                            // get a timestamp when executing an action
                            currentTime = System.currentTimeMillis();
                            // set the animator which to a green color for one second to signalize
                            // the correct processing
                            previousAnimation.cancel();
                            previousAnimation = setOneAnimator(previousImage, freq1, Color.BLACK, Color.GREEN);
                            previousAnimation.start();
                            // set color back to red after one second
                            new Handler().postDelayed(new Runnable() {
                                @Override
                                public void run() {
                                    previousAnimation.cancel();
                                    previousAnimation = setOneAnimator(previousImage, freq1, Color.BLACK, Color.RED);
                                    previousAnimation.start();
                                }
                            }, 1000);
                            break;
                        // execute
                        case "2":
                            executeAction(findViewById(R.id.currentButton));

                            currentTime = System.currentTimeMillis();
                            currentAnimation.cancel();
                            currentAnimation = setOneAnimator(currentImage, freq2, Color.BLACK, Color.GREEN);
                            currentAnimation.start();
                            new Handler().postDelayed(new Runnable() {
                                @Override
                                public void run() {
                                    currentAnimation.cancel();
                                    currentAnimation = setOneAnimator(currentImage, freq2, Color.BLACK, Color.RED);
                                    currentAnimation.start();
                                }
                            }, 1000);
                            break;
                        // next
                        case "3":
                            nextAction(findViewById(R.id.nextButton));

                            currentTime = System.currentTimeMillis();
                            nextAnimation.cancel();
                            nextAnimation = setOneAnimator(nextImage, freq3, Color.BLACK, Color.GREEN);
                            nextAnimation.start();
                            new Handler().postDelayed(new Runnable() {
                                @Override
                                public void run() {
                                    nextAnimation.cancel();
                                    nextAnimation = setOneAnimator(nextImage, freq3, Color.BLACK, Color.RED);
                                    nextAnimation.start();
                                }
                            }, 1000);
                            break;
                        default:
                            log.logStatusMain("Unknown MQTT-command!");
                    }
                }
            });
        }
    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {
        log.logStatusMain("Delivery Complete");
        log.logStatusMain(token.toString());
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    private class ClientSendHashTask extends AsyncTask<byte [], Void, Boolean> {

        @Override
        protected Boolean doInBackground(byte[]... endMessage) {

            /* boolean for the connection */
            boolean connectionStatus = false;

            DatagramSocket clientSocket = null;

            /* Ip-Address of the device to send the message to */
            InetAddress ipAddress;

			/*Encoding the incoming message to sequence of Bytes */
            byte [] yourMessage = endMessage[0];

			/*Trying to send the data */
            try{
                clientSocket = new DatagramSocket();
                ipAddress = InetAddress.getByName("192.168.43.13");
                DatagramPacket sendPacket = new DatagramPacket(yourMessage, yourMessage.length, ipAddress, 8530);

                for(int i = 0; i < 10; i++) {
                    clientSocket.send(sendPacket);
                }
                connectionStatus = true;

            } catch (IOException io) {
                io.printStackTrace();
            }

			/*End the connection to the socket */
            clientSocket.close();
            return connectionStatus;
        }

        @Override
        protected void onPostExecute(Boolean result) {
        }

    }


}




