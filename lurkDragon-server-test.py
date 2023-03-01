# Testing server using many recv instead of calling recv once and putting the whole message into a buffer.

#!/usr/bin/env python3

from serverlibtest import *

def handleClient(skt):
    while True:
        msgType = skt.recv(1)
        lurkMsg = lurkRecv(msgType)

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if serverSkt == -1:
    print('ERROR: Server socket error!')
    exit

# Assigned range: 5010 - 5014
address = '0.0.0.0'
port = 5010

serverSkt.bind((address, port))

serverSkt.listen()
print('DEBUG: Listening on address:', address, 'port:', port)

while True:
    clientSkt, clientAddr = serverSkt.accept()
    
    version = Version.sendVersion(clientSkt)
    game = Game.sendGame(clientSkt)
    
    if (version == 0 and game == 0):
        Client.addClient(clientSkt)
        #Client.getClients()
        clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()    # Create thread for connected client and starts it
    else:
        print('ERROR: VERSION & GAME message failed somehow!')