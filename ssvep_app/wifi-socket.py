import socket
from Crypto.Cipher import AES
import hashlib
import urllib.parse
import urllib.request, json
import binascii
import time
import codecs
import string
mac = '009569A692EA'

COMPANY_CODE_LIDL = 'C1'
COMPANY_CODE_ALDI = 'C2'

AUTH_CODE_ALDI = '92DD'
AUTH_CODE_LIDL = '7150'


on =        '0000D5C21192DD010000FFFF04040404'
off =       '0000D5C21192DD01000000FF04040404'

slaveon =   '00FFFFC21192DD0811743F6004040404'
slaveoff =   '00FFFFC21192DD0811743F7004040404'



class WifiSocket:
    AES_KEY = '0123456789abcdef'
    MAC = None
    IP = None

    COMPANY_CODE = COMPANY_CODE_ALDI
    AUTH_CODE = AUTH_CODE_ALDI

    MAIN_STATE_ON = '0000FFFF'
    MAIN_STATE_OFF = '000000FF'

    RF_STATE_ON = '6'
    RF_STATE_OFF = '7'

    finalHash = string.Template('01 40 $mac 10 $cmd')

    cmdMain = string.Template('00 FF FF $companyCode 11 $authCode 01 $mainState 04 04 04 04')
    cmdRf = string.Template('00 FF FF $companyCode 11 $authCode 08 $rfAddress $rfState 0 04 04 04 04')

    def __init__(self, mac, ip):
        self.MAC = mac
        self.IP = ip

    def sendToDevice(self, cmd):
        text = bytes.fromhex(cmd)
        cypher = AES.new(key=self.AES_KEY, mode=AES.MODE_CBC, IV=self.AES_KEY)
        enctext = cypher.encrypt(text)
        coded = codecs.encode(enctext, 'hex').decode("utf-8")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        s.connect((self.IP, 8530))
        s.send(bytearray.fromhex( self.finalHash.substitute(mac=self.MAC, cmd = coded) ))

    def turnOn(self, device=None):
        if (device == None):
            cmd = self.cmdMain.substitute(companyCode=self.COMPANY_CODE, authCode=self.AUTH_CODE, mainState=self.MAIN_STATE_ON)
        self.sendToDevice(cmd)

    @staticmethod
    def captureDevices(username, password):
        access_key = 'Q763W08JZ07V23FR99410B3PC945LT28'
        base_url = string.Template('http://smart2connect.yunext.com/$endPoint?accessKey=$accessKey&username=$username&password=$password')
        username = urllib.parse.quote_plus(username)
        password = hashlib.md5(password.encode('utf-8')).hexdigest().upper()

        print( base_url.substitute(endPoint='api/device/wifi/list', accessKey=access_key, username=username, password=password))

        with urllib.request.urlopen( base_url.substitute(endPoint='api/device/wifi/list', accessKey=access_key, username=username, password=password) ) as url:
            data = json.loads(url.read().decode())
            print(data)

        with urllib.request.urlopen(
                base_url.substitute(endPoint='api/scene/rf/list', accessKey=access_key, username=username,
                                    password=password)) as url:
            data = json.loads(url.read().decode())
            print(data)




WifiSocket.captureDevices('michael.hammerl@hs-augsburg.de', 'bci2016')

wif = WifiSocket(mac='009569A692EA', ip='192.168.0.21')

#wif.turnOn()
# => b'6eed72d95f2db03b82d5662e0a603424'




