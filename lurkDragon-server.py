'''
CS435 LurkDragon: Server
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
    KNOWN ISSUES
        ...
'''

#!/usr/bin/env python3

import logging
# Import socket module, necessary for network communications
import socket
# Import threading module, required for multithreading & handling multiple clients
import threading
import time

# Import custom lurk module
from lurk import *

# Function for handling individual clients
#   cSkt: Client socket to handle
def handleClient(cSkt):
    data = bytearray(b'')
    while True:
        # If socket buffer is empty, try receiving data from client
        if data == b'':
            try:
                data = cSkt.recv(4096)
            except ConnectionError:                                             # Catch a ConnectionError if socket is closed
                print('WARN: Failed to receive, ConnectionError!')                  # Print warning message
                if cSkt in Client.clients:                                          # If client is found in database tracking connected clients
                    Client.removeClient(cSkt)                                           # Remove client from the list
                    print('LOG: Removed client from dictionary!')                       # Print log message
                    return 1                                                            # Return error code 1
                else:                                                               # If client is not found for whatever reason
                    print('ERROR: Connection not found for removal?! Weird...')         # Print error message
                    return 2                                                            # Return error code 2
        
        # If socket buffer contains message(s), take action
        elif data != b'':
            if (data[0] == 1):
                # Handle MESSAGE
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                continue
            elif (data[0] == 2):
                # Handle CHANGEROOM
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                continue
            elif (data[0] == 3):
                # Handle FIGHT
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                continue
            elif (data[0] == 4):
                # Handle PVPFIGHT
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                continue
            elif (data[0] == 5):
                # Handle LOOT
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                continue
            elif (data[0] == 6):
                # Handle START
                startData = bytes(data[0])
                msgType = Start.recvStart(cSkt, startData)
                data = data.replace(startData, b'')
                continue
            elif (data[0] == 7):
                # Handle ERROR
                errorDataConst = data[0:4]
                msgType, errCode, errMsgLen = Error.recvErrorConst(cSkt, errorDataConst)
                errorDataVar = data[4:4+errMsgLen]
                errMsg = Error.recvErrorVar(cSkt, errorDataVar)
                errorData = errorDataConst + errorDataVar
                data = data.replace(errorData, b'')
                continue
            elif (data[0] == 8):
                # Handle ACCEPT
                acceptData = data[0:1]
                msgType, accept = Accept.recvAccept(cSkt, data)
                data = data.replace(acceptData, b'')
                continue
            elif (data[0] == 9):
                # Handle ROOM
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                continue
            elif (data[0] == 10):
                # Handle CHARACTER
                characterDataConst = data[0:48]
                msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = Character.recvCharacterConst(cSkt, characterDataConst)
                characterDataVar = data[48:48+charDesLen]
                charDes = Character.recvCharacterVar(cSkt, characterDataVar, charDesLen)
                characterData = characterDataConst + characterDataVar
                
                # If stats and CHARACTER message is valid, send ACCEPT
                if (attack + defense + regen <= Game.initPoints):
                    print('DEBUG: Detected valid stats, sending ACCEPT!')
                    accept = Accept.sendAccept(cSkt, 10)
                    room = Room.sendRoom(cSkt, 0)
                else:
                    print('DEBUG: Detected invalid stats, sending ERROR type 4!')
                    error = Error.sendError(cSkt, 4)
                data = data.replace(characterData, b'')        # This works now!!!
                continue                                                                # Continue while loop
            
            elif (data[0] == 11):
                # Handle GAME
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                continue
            elif (data[0] == 12):
                # Handle LEAVE
                leaveData = data[0]
                leave = Leave.recvLeave(cSkt)
                Client.removeClient(cSkt)
                data = data.replace(data, b'')
                break
            elif (data[0] == 13):
                # Handle CONNECTION
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                continue
            elif (data[0] == 14):
                # Handle VERSION
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                continue
            else:
                print('ERROR: Invalid message detected!')
                data = data.replace(data, b'')
                continue
        else:
            print('ERROR: Something weird happened! Stopping.')

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign address & port number
# Assigned range: 5010 - 5014
address = '0.0.0.0'
port = 5010

# Bind server to machine's assigned address & port number
serverSkt.bind((address, port))

# Server listens and queues up connections
serverSkt.listen()
print('DEBUG: Listening on address:', address, 'port:', port)

while True:
    clientSkt, clientAddr = serverSkt.accept()
    
    version = Version.sendVersion(clientSkt)
    game = Game.sendGame(clientSkt)
    
    #time.sleep(1)
    
    if clientSkt.fileno() == -1:
        print('Invalid socket, perhaps it was lurkscan?')
    
    if (version == 0 and game == 0):
        Client.addClient(clientSkt)
        #Client.getClients()
        clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()    # Create thread for connected client and starts it
    else:
        print('ERROR: VERSION & GAME message failed somehow!')