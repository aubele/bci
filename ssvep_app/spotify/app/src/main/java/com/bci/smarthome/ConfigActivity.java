package com.bci.smarthome;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.v7.app.AppCompatActivity;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.support.design.widget.Snackbar;

import com.spotify.sdk.android.authentication.AuthenticationClient;
import com.spotify.sdk.android.authentication.AuthenticationRequest;
import com.spotify.sdk.android.authentication.AuthenticationResponse;
import com.spotify.sdk.android.player.Config;
import com.spotify.sdk.android.player.Error;
import com.spotify.sdk.android.player.PlayerEvent;
import com.spotify.sdk.android.player.Spotify;
import com.spotify.sdk.android.player.SpotifyPlayer;
import com.spotify.sdk.android.player.ConnectionStateCallback;

/**
 * Created by Fabio Paul Aubele (Email: fabioaubele95@hotmail.de)
 * on behalf of Hochschule Augsburg (BCI-Projekt SS 2017)
 */

public class ConfigActivity extends AppCompatActivity implements
        SpotifyPlayer.NotificationCallback, ConnectionStateCallback {

    // CONSTANTS

    /**
     * Client ID, can be found under https://developer.spotify.com/my-applications/#!/
     */
    private static final String CLIENT_ID = "866a929469724a708d4cfe20a7d08656";
    /**
     * Redirect URI, can be found under https://developer.spotify.com/my-applications/#!/
     */
    private static final String REDIRECT_URI = "spotify-bci://callback";
    /** Request code that will be used to verify if the result comes from correct activity
     * Can be any integer
     */
    private static final int REQUEST_CODE = 1337;

    private static final String IP_PREFERENCE = "IP";
    private static final String TOPIC_PREFERENCE = "TOPIC";
    private static final String PORT_PREFERENCE = "PORT";

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // FIELDS

    /**
     * Instance which is used for all log-calls
     */
    private final ConsoleLog log = new ConsoleLog();

    /**
     * Button which is reliant on the login
     */
    private static final int[] REQUIRES_INITIALIZED_STATE = {
            R.id.logoutButton,
    };

    private String accessToken = null;

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

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // INIT

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_config);

        initView();
        updateButton();
    }

    private void initView(){
        initButton();
        initTextEdit();
    }

    private void initButton(){
        final Button nextButton = (Button) findViewById(R.id.nextButton);
        nextButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                onNext();
            }
        });
        final Button loginButton = (Button) findViewById(R.id.loginButton);
        loginButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                onLogin();
            }
        });
        final Button logoutButton = (Button) findViewById(R.id.logoutButton);
        logoutButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                onLogout();
            }
        });
    }

    /**
     * Initialize all text edits with listener
     */
    private void initTextEdit(){
        final EditText ipEdit = (EditText) findViewById(R.id.ipEdit);
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(this);
        String ipText = preferences.getString(IP_PREFERENCE, "");
        if(!ipText.equalsIgnoreCase(""))
        {
            log.logStatusConfig("Got string " + ipText + " for ipEdit");
            ipEdit.setText(ipText);
        }
        ipEdit.addTextChangedListener(new TextWatcher() {

            public void afterTextChanged(Editable s) {
                updateIPEditText(s.toString());
            }

            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {
            }

            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {

            }
        });
        final EditText portEdit = (EditText) findViewById(R.id.portEdit);
        SharedPreferences preferences2 = PreferenceManager.getDefaultSharedPreferences(this);
        String portText = preferences2.getString(PORT_PREFERENCE, "");
        if(!portText.equalsIgnoreCase(""))
        {
            log.logStatusConfig("Got string " + portText + " for portEdit");
            portEdit.setText(portText);
        }
        portEdit.addTextChangedListener(new TextWatcher() {

            public void afterTextChanged(Editable s) {
                updatePortEditText(s.toString());
            }

            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {
            }

            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {

            }
        });
        final EditText topicEdit = (EditText) findViewById(R.id.topicEdit);
        SharedPreferences preferences3 = PreferenceManager.getDefaultSharedPreferences(this);
        String topicText = preferences3.getString(TOPIC_PREFERENCE, "");
        if(!topicText.equalsIgnoreCase(""))
        {
            log.logStatusConfig("Got string " + topicText + " for topicEdit");
            topicEdit.setText(topicText);
        }
        topicEdit.addTextChangedListener(new TextWatcher() {

            public void afterTextChanged(Editable s) {
                updateTopicEditText(s.toString());
            }

            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {
            }

            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {

            }
        });
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // UI

    private void updateButton() {
        boolean login = isLoggedIn();
        setButtonAvailabilityForLogin(login);
    }

    /**
     * Saves the given string for the ip adress
     * @param text string that got entered by the user and gets saved with sharedpreferences
     */
    private void updateIPEditText(String text) {
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(this);
        SharedPreferences.Editor editor = preferences.edit();
        editor.putString(IP_PREFERENCE, text);
        editor.apply();
    }

    /**
     * Saves the given string for the port
     * @param text string that got entered by the user and gets saved with sharedpreferences
     */
    private void updatePortEditText(String text) {
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(this);
        SharedPreferences.Editor editor = preferences.edit();
        editor.putString(PORT_PREFERENCE, text);
        editor.apply();
    }
    /**
     * Saves the given string for the mqtt topic
     * @param text string that got entered by the user and gets saved with sharedpreferences
     */
    private void updateTopicEditText(String text) {
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(this);
        SharedPreferences.Editor editor = preferences.edit();
        editor.putString(TOPIC_PREFERENCE, text);
        editor.apply();
    }

    private void setButtonAvailabilityForLogin(boolean enable) {
        for (int id : REQUIRES_INITIALIZED_STATE) {
            findViewById(id).setEnabled(enable);
        }
    }

    private boolean isLoggedIn() {
        return mPlayer != null && mPlayer.isLoggedIn();
    }

    /**
     * gets triggered when the next-button gets clicked, makes a new intent with all needed information
     * as extras
     */
    private void onNext() {
        Intent intent = new Intent(ConfigActivity.this, MainActivity.class);
        intent.putExtra("ACCESS_TOKEN", accessToken);
        final EditText topicEdit = (EditText) findViewById(R.id.topicEdit);
        intent.putExtra(TOPIC_PREFERENCE, topicEdit.getText().toString());
        final EditText ipEdit = (EditText) findViewById(R.id.ipEdit);
        intent.putExtra(IP_PREFERENCE, ipEdit.getText().toString());
        final EditText portEdit = (EditText) findViewById(R.id.portEdit);
        intent.putExtra(PORT_PREFERENCE, portEdit.getText().toString());
        this.finish();
        ConfigActivity.this.startActivity(intent);
    }

    /**
     * gets triggered when the login-button gets clicked
     */
    private void onLogin() {
        log.logStatusConfig("Login was clicked");
        openLoginWindow();
    }

    /**
     * gets triggered when the logout-button gets clicked
     */
    private void onLogout() {
        log.logStatusConfig("Logout was clicked");
        mPlayer.logout();
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // AUTHENTICATION

    /**
     * opens the login activity provided from the spotify api
     */
    protected void openLoginWindow() {
        // authentication stuff..
        AuthenticationRequest.Builder builder = new AuthenticationRequest.Builder(CLIENT_ID,
                AuthenticationResponse.Type.TOKEN,
                REDIRECT_URI);
        builder.setScopes(new String[]{"user-read-private", "playlist-read", "playlist-read-private", "streaming"});
        AuthenticationRequest request = builder.build();

        AuthenticationClient.openLoginActivity(this, REQUEST_CODE, request);
    }

    /**
     * gets called after the authorization from the login activity is finished
     * @param requestCode number which identifies the calling activity
     * @param resultCode number which indentifies the result
     * @param intent given intent
     */
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent intent) {
        super.onActivityResult(requestCode, resultCode, intent);

        // Check if result comes from the correct activity
        if (requestCode == REQUEST_CODE) {
            AuthenticationResponse response = AuthenticationClient.getResponse(resultCode, intent);

            switch (response.getType()) {
                // Response was successful and contains auth token
                case TOKEN:
                    log.logStatusConfig("Auth successful");
                    onAuthenticationComplete(response);
                    break;

                // Auth flow returned an error
                case ERROR:
                    log.logErrorConfig("Auth error: " + response.getError());
                    Snackbar mySnackbarError = Snackbar.make(findViewById(R.id.coordinatorLayout),
                            "An error occured, please check your connection or your account details!",
                            Snackbar.LENGTH_LONG);
                    mySnackbarError.show();
                    break;

                // Most likely auth flow was cancelled
                default:
                    log.logStatusConfig("Auth result: " + response.getType());
                    Snackbar mySnackbarCancel = Snackbar.make(findViewById(R.id.coordinatorLayout),
                            "An error occured, you probably canceled the login!", Snackbar.LENGTH_LONG);
                    mySnackbarCancel.show();
            }
        }
    }

    /**
     * Creates the spotify player after the login was successful
     * @param response given result from the login activity
     */
    private void onAuthenticationComplete(AuthenticationResponse response) {
        // Once we have obtained an authorization token, we can proceed with creating a Player.
        log.logStatusConfig("Got authentication token");
        if (mPlayer == null) {
            Config playerConfig = new Config(this, response.getAccessToken(), CLIENT_ID);
            Spotify.getPlayer(playerConfig, this, new SpotifyPlayer.InitializationObserver() {
                @Override
                public void onInitialized(SpotifyPlayer spotifyPlayer) {
                    mPlayer = spotifyPlayer;
                    mPlayer.addConnectionStateCallback(ConfigActivity.this);
                    mPlayer.addNotificationCallback(ConfigActivity.this);
                    log.logStatusConfig("Player successfully initialized");
                    // trigger UI refresh, has probably no effect
                    updateButton();
                }

                @Override
                public void onError(Throwable throwable) {
                    log.logErrorConfig("Could not initialize player: " + throwable.getMessage());
                }
            });
        } else {
            mPlayer.login(response.getAccessToken());
        }
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    //CALLBACK METHODS

    @Override
    public void onLoggedIn() {
        log.logStatusConfig("User logged in");
        Snackbar mySnackbar = Snackbar.make(findViewById(R.id.coordinatorLayout),
                "Successfully logged in your Spotify-Account", Snackbar.LENGTH_LONG);
        mySnackbar.show();

        updateButton();
    }

    @Override
    public void onLoggedOut() {
        log.logStatusConfig("User logged out");
        Snackbar mySnackbar = Snackbar.make(findViewById(R.id.coordinatorLayout),
                "Successfully logged out your Spotify-Account", Snackbar.LENGTH_LONG);
        mySnackbar.show();

        updateButton();
    }

    @Override
    public void onLoginFailed(Error i) {
        log.logErrorConfig("Login failed" + i.toString());
    }

    @Override
    public void onTemporaryError() {
        log.logErrorConfig("Temporary error occurred");
    }

    @Override
    public void onConnectionMessage(String message) {
        log.logStatusConfig("Received connection message: " + message);
    }

    //**********************************************************************************************
    //**********************************************************************************************
    //**********************************************************************************************

    // DESTRUCTION

    @Override
    protected void onDestroy() {
        Spotify.destroyPlayer(mPlayer);
        log.logStatusConfig("Player got destroyed");
        super.onDestroy();
    }

    @Override
    public void onPlaybackEvent(PlayerEvent playerEvent) {
        log.logStatusConfig("Playback event received: " + playerEvent.name());
        switch (playerEvent) {
            // Handle event type as necessary
            default:
                break;
        }
    }

    @Override
    public void onPlaybackError(Error error) {
        log.logErrorConfig("Playback error received: " + error.name());
        switch (error) {
            // Handle error type as necessary
            default:
                break;
        }
    }

}