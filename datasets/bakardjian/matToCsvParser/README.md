Script to parse the matlab files.

Run the main.py script with the path to the folder with the matlab data. This folder must have the subfoler 8Hz, 14Hz and 28Hz. Each subdirectory contains the matlabfiles with the correct frequncy.

Example script call:
python main.py <PathToDataDirectory>

Directory example:

data
 |
 |- test
 |   |
 |   |- 8Hz
 |   |   |-8HzMatlabfile
 |   |
 |   |- 14Hz
 |   |   |-14HzMatlabfile
 |   |
 |   |- 28Hz
 |       |-28HzMatlabfile
 |
 |- train
 |   |
 |   |- 8Hz
 |   |   |-8HzMatlabfile
 |   |
 |   |- 14Hz
 |   |   |-14HzMatlabfile
 |   |
 |   |- 28Hz
     |   |-28HzMatlabfile

The output will be written into the csv folder.


