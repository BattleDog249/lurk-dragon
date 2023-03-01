#!/usr/bin/env python3

from serverlib import *

def handleClient(skt):
    while True:
        data = lurkRecv(skt)
        if (data == None):
            print('DEBUG: lurkRecv() passed None. Removing client from tracker and ending thread.')
            # Maybe also remove client connection with "active" (in use) character here as well
            Client.removeClient(skt)
            print('DEBUG: Connected Clients:', Client.getClients())
            break
        message = lurkRead(data)
        if (message == None):
            continue
        print('DEBUG: Passing to lurkServ():', message)
        result = lurkServ(skt, message)
        if (result == 1):
            print('WARN: Server does not support receiving this message, sending error 0!')
            print('INFO: This could also occur if lurkServ() was passed completely invalid data, but the first byte in the message happens to be a valid lurk message type.')
            error = Error.sendError(skt, 0)
            continue
        elif (result == 2):
            print('WARN: lurkServ() received a message type not supported by the LURK protocol, sending error 0!')
            error = Error.sendError(skt, 0)
            continue
        elif (result == -1):
            print('INFO: Client sent LEAVE, ending thread for {}'.format(skt))
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
    
    if (version == 0 and game == 0):
        Client.addClient(clientSkt)
        #Client.getClients()
        clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()    # Create thread for connected client and starts it
    else:
        print('ERROR: VERSION & GAME message failed somehow!')