'''
CS435 LurkDragon: Server
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
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

MESSAGE = int(1)
CHANGEROOM = int(2)
FIGHT = int(3)
PVPFIGHT = int(4)
LOOT = int(5)
START = int(6)
ERROR = int(7)
ACCEPT = int(8)
ROOM = int(9)
CHARACTER = int(10)
GAME = int(11)
LEAVE = int(12)
CONNECTION = int(13)
VERSION = int(14)

characters = {}

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
        
        # If socket buffer contains message(s); do something with message, delete message from buffer, continue acting on other messages until buffer is empty, then continue listening
        elif data != b'':
            
            if (data[0] == MESSAGE):
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                
            elif (data[0] == CHANGEROOM):
                changeRoomData = data[0:3]
                Error.sendError(cSkt, 0)
                data = data.replace(changeRoomData, b'')
                
            elif (data[0] == FIGHT):
                fightData = bytes(data[0:1])
                Error.sendError(cSkt, 0)
                data = data.replace(fightData, b'')
                
            elif (data[0] == PVPFIGHT):
                pvpFightData = data[0:32]       # Untested
                Error.sendError(cSkt, 8)
                data = data.replace(pvpFightData, b'')
                
            elif (data[0] == LOOT):
                lootData = data[0:32]           # Untested
                Error.sendError(cSkt, 0)
                data = data.replace(lootData, b'')
                
            elif (data[0] == START):
                startData = bytes(data[0:1])
                msgType = Start.recvStart(cSkt, startData)
                data = data.replace(startData, b'')
                
            elif (data[0] == ERROR):
                errorDataConst = data[0:4]
                msgType, errCode, errMsgLen = Error.recvErrorConst(cSkt, errorDataConst)
                errorDataVar = data[4:4+errMsgLen]
                errMsg = Error.recvErrorVar(cSkt, errorDataVar)
                errorData = errorDataConst + errorDataVar
                data = data.replace(errorData, b'')
                
            elif (data[0] == ACCEPT):
                acceptData = data[0:1]
                msgType, accept = Accept.recvAccept(cSkt, acceptData)
                data = data.replace(acceptData, b'')
                
            elif (data[0] == ROOM):
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                
            elif (data[0] == CHARACTER):
                characterDataConst = data[0:48]
                msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = Character.recvCharacterConst(cSkt, characterDataConst)
                #name = str(name)
                characterDataVar = data[48:48+charDesLen]
                charDes = Character.recvCharacterVar(cSkt, characterDataVar, charDesLen)
                characterData = characterDataConst + characterDataVar
                
                # If received character is new to the server
                if (name not in characters):
                    print('DEBUG: Character not found in database, adding!')
                    # If stats and CHARACTER message is valid, send ACCEPT
                    if (attack + defense + regen <= Game.initPoints):
                        print('DEBUG: Detected valid stats, sending ACCEPT!')
                        characters.update({name: [flags, attack, defense, regen, 100, 0, 0]})   # Health = 100, Gold = 0, Room = 0
                        print(characters)
                        accept = Accept.sendAccept(cSkt, 10)
                        room = Room.sendRoom(cSkt, 0)
                    else:
                        print('DEBUG: Detected invalid stats, sending ERROR type 4!')
                        error = Error.sendError(cSkt, 4)
                else:
                    print('DEBUG: Character found in database!')
                    if (attack + defense + regen <= Game.initPoints):
                        print('DEBUG: Detected valid stats, sending ACCEPT!')
                        characters.update({name: [flags, attack, defense, regen, 100, 0, 0]})   # Health = 100, Gold = 0, Room = 0
                        print(characters)
                        accept = Accept.sendAccept(cSkt, 10)
                        room = Room.sendRoom(cSkt, 0)
                    else:
                        print('DEBUG: Detected invalid stats, sending ERROR type 4!')
                        error = Error.sendError(cSkt, 4)
                data = data.replace(characterData, b'')        # This works now!!!
                
            elif (data[0] == GAME):
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                
            elif (data[0] == LEAVE):
                leaveData = bytes(data[0:1])
                leave = Leave.recvLeave(cSkt)
                Client.removeClient(cSkt)
                data = data.replace(leaveData, b'')
                break
            
            elif (data[0] == CONNECTION):
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                
            elif (data[0] == VERSION):
                Error.sendError(cSkt, 0)
                data = data.replace(data, b'')
                
            else:
                print('ERROR: Invalid message type detected!')
                data = data.replace(data, b'')
                
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