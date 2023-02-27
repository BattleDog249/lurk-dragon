#!/usr/bin/env python3

import socket
import threading

from serverlib import *

def handleClient(skt):
    while True:
        data = lurkRecv(skt)
        if (data == None):
            # Remove client from tracking database
            break
        message = lurkRead(data)
        if (message == None):
            continue
        print('DEBUG: Passing to lurkServ():', message)
        result = lurkServ(skt, message)
        if (result == -1):  # If we handled LEAVE, stop loop
            break

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
    
    # Handle incoming client messages until a START is received, then spin off in new thread? Trying to fix a thread spinning up for each lurkscan
    
    if (version == 0 and game == 0):
        Client.addClient(clientSkt)
        #Client.getClients()
        clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()    # Create thread for connected client and starts it
    else:
        print('ERROR: VERSION & GAME message failed somehow!')