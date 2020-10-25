package de.hs_augsburg.bci2017;

import android.content.Context;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;


public class MainActivity extends AppCompatActivity {


    private Action[] actions = new Action[]{
            new Action() {
                @Override
                public void execute() {

                }

                @Override
                public String getLabel() {
                    return "Licht An";
                }
            },
            new Action() {
                @Override
                public void execute() {

                }

                @Override
                public String getLabel() {
                    return "Licht Aus";
                }
            },
            new Action() {
                @Override
                public void execute() {

                }

                @Override
                public String getLabel() {
                    return "Musik Abspielen";
                }
            },
            new Action() {
                @Override
                public void execute() {

                }

                @Override
                public String getLabel() {
                    return "Musik Lauter";
                }
            },
            new Action() {
                @Override
                public void execute() {

                }

                @Override
                public String getLabel() {
                    return "Musik Leiser";
                }
            },

    };

    private int currentAction = 0;

    private TextView previousText;
    private TextView currentText;
    private TextView nextText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


        previousText = (TextView)findViewById(R.id.previousText);
        currentText = (TextView)findViewById(R.id.currentText);
        nextText = (TextView)findViewById(R.id.nextText);

        updateButtons();

    }

    public void updateButtons()
    {
        Action previousAction = actions[ (currentAction > 0) ? currentAction - 1 : actions.length - 1 ];
        previousText.setText( previousAction.getLabel() );
        currentText.setText( actions[currentAction].getLabel() );
        Action nextAction = actions[ (currentAction < (actions.length - 1)) ? currentAction + 1 : 0 ];
        nextText.setText( nextAction.getLabel() );
    }

    public void previousAction(View view) {

        currentAction = (currentAction > 0) ? currentAction - 1 : actions.length - 1;

        updateButtons();

    }

    public void nextAction(View view) {

        currentAction = (currentAction < (actions.length - 1)) ? currentAction + 1 : 0;

        updateButtons();

    }

    public void executeAction(View view) {

        Context context = getApplicationContext();
        CharSequence text = "Führe Aus: " + actions[currentAction].getLabel();
        int duration = Toast.LENGTH_SHORT;

        Toast toast = Toast.makeText(context, text, duration);
        toast.show();

    }
}
