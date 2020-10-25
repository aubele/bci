sudo apt install build-essential \
libopenblas-dev \
python-pip \
mosquitto \
mosquitto-clients \
-y

pip install scipy \
Theano==0.8 \
-e git+https://github.com/Lasagne/Lasagne.git@8f4f9b2#egg=Lasagne==0.2.git \
joblib==0.9.3 \
scikit-learn \
tabulate==0.7.5 \
-e git+https://github.com/dnouri/nolearn.git@master#egg=nolearn==0.7.git \
imbalanced-learn \
paho-mqtt

echo "[global]
device = gpu  
floatX = float32

[blas]
ldflags = -L/usr/local/lib -lopenblas" > ~/.theanorc