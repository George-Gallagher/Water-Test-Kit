import socket, pickle
import json, subprocess
from sorter4 import Sorter
 
username        = 'ProjectCInterns'                                                                     # Your ClickSend username
api_key         = '488EEB10-B030-070D-FC8A-1B8A813170A4'        # Your Secure Unique API key
msg_to          = '+17034737129'                                                # Recipient Mobile Number in international format ($
msg_from        = ''                                                            # Custom sender ID (leave blank to accept replies).
msg_body        = 'This is a test message'                                      # The message to be sent.
HOST = '192.168.1.4'
PORT = 3999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
try:
        n=0
        p=0
        while True:
                conn, addr = s.accept()
                print 'Connected by', addr
                while 1:
                    p=0
                    data = conn.recv(4096)
                    if not data: print('no data')
                    if not data: break
                    conn.send(data)
                    dataPrint = pickle.loads(data)
                    print("raw")
                    print(data)
                    print("loads")
                    print(dataPrint)
                    sorter = Sorter(dataPrint)
                    ret = sorter.sort()
                    if ret=='':
                        p=1
                    if n%100==0 or p==0:
                        msg_body='DO: ' + str(dataPrint[0]) + ' ORP: ' + str(dataPrint[1]) + ' pH: ' + str(dataPrint[2]) + ' Conductivity: ' + str(dataPrint[3]) + 'Temp: ' + str(dataPrint[4]) + ' Flow ' + str(dataPrint[5]) + ' Nitrate ' + str(dataPrint[6]) + ' Turbidity: ' + str(dataPrint[7]) + ret 
                        request = { "messages" : [ { "source":"python", "from":msg_from, "to":msg_to, "body":msg_body } ] }
                        request = json.dumps(request)
                        cmd = "curl https://rest.clicksend.com/v3/sms/send -u " + username + ":" + api_key + " -H \"Content-Type: application/json\" -X POST --data-raw '" + request + "'"
                        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
                        (output,err) = p.communicate()
                        print output
                    n+=1
except KeyboardInterrupt:
        pass

