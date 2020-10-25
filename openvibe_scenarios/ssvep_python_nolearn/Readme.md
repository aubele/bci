 - place the electrodes according to ./datasets/own/openbci_ssvep_electrodes.cfg
 - use OpenBCI app (sudo on linux) to check the connection quality: all channels <10 uVrms
    - Tipp: if the connection fails, shut down the board, unplug the usb device
      plug it back in and start the board
 - start aquisition server (sudo on linux), select correct channels in driver properties
 - start openvibe, 0_test_acquisition
 - run 1_configure_acquisition
 - run 2_data_acquisition, test person should look at the boxes propted in the console
 - run 3_convert_ov_to_csv
 - run 4_configure_traing
 - run 5_train_raw_classifier
 - optional: review data quality with heatmap.py
 - optional: run 6_test_raw_classifier
 - run mqtt-broker (should be running in backgroud once installed
 - run 7_live_prediction
    - run `mosquitto_sub -h localhost -t SSVEP` to test if the messages are being sent

Good Luck ;-)
