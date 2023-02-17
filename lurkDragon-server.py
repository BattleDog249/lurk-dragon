'''
CS435 LurkDragon: Server
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
    KNOWN ISSUES
        ...
'''

#!/usr/bin/env python3

# Import socket module, necessary for network communications
import socket
# Import threading module, required for multithreading & handling multiple clients
import threading

# Import custom lurk module
from lurk import *

# Function for handling individual clients
#   cSkt: Client socket to handle
def handleClient(cSkt):
    version = Version.sendVersion(cSkt)
    if (version != 0):
        print('WARN: sendVersion() returned unexpected code', version, 'for client', cSkt)
        return 2
    game = Game.sendGame(cSkt)
    if (game != 0):
        print('WARN: sendGame() returned unexpected code', game, 'for client', cSkt)
        return 2
    while True:
        buffer = b''                                        # I think this method breaks if recv receives more than one message into buffer
        try:
            buffer = cSkt.recv(4096)
        except ConnectionError:                                             # Catch a ConnectionError if socket is closed
            print('WARN: Failed to receive, ConnectionError!')                  # Print warning message
            if cSkt in Client.clients:                                          # If client is found in database tracking connected clients
                Client.removeClient(cSkt)                                           # Remove client from the list
                print('LOG: Removed client from dictionary!')                       # Print log message
                return 1                                                            # Return error code 1
            else:                                                               # If client is not found for whatever reason
                print('ERROR: Connection not found for removal?! Weird...')         # Print error message
                return 2                                                            # Return error code 2
        
        if (buffer != b'' and buffer[0] == 1):
            # Handle MESSAGE
            Error.sendError(cSkt, 0)
            continue
        elif (buffer != b'' and buffer[0] == 2):
            # Handle CHANGEROOM
            Error.sendError(cSkt, 0)
            continue
        elif (buffer != b'' and buffer[0] == 3):
            # Handle FIGHT
            Error.sendError(cSkt, 0)
            continue
        elif (buffer != b'' and buffer[0] == 4):
            # Handle PVPFIGHT
            Error.sendError(cSkt, 0)
            continue
        elif (buffer != b'' and buffer[0] == 5):
            # Handle LOOT
            Error.sendError(cSkt, 0)
            continue
        elif (buffer != b'' and buffer[0] == 6):
            # Handle START
            startBuffer = buffer
            msgType = Start.recvStart(cSkt, startBuffer)
        elif (buffer != b'' and buffer[0] == 7):
            # Handle ERROR
            errorBuffer = buffer
            error = Error.recvError(cSkt, errorBuffer)
            continue
        elif (buffer != b'' and buffer[0] == 8):
            # Handle ACCEPT
            acceptBuffer = buffer
            accept = Accept.recvAccept(cSkt, acceptBuffer)
            continue
        elif (buffer != b'' and buffer[0] == 9):
            # Handle ROOM
            Error.sendError(cSkt, 0)
            continue
        elif (buffer != b'' and buffer[0] == 10):
            # Handle CHARACTER
            characterBuffer = buffer
            name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes = Character.recvCharacter(cSkt, characterBuffer)
            
            # If stats and CHARACTER message is valid, send ACCEPT
            if (attack + defense + regen <= Game.initPoints):
                print('DEBUG: Detected valid stats, sending ACCEPT!')
                accept = Accept.sendAccept(cSkt, 10)
                room = Room.sendRoom(cSkt, 0)
            else:
                print('DEBUG: Detected invalid stats, sending ERROR type 4!')
                error = Error.sendError(cSkt, 4)
            continue
        
        elif (buffer != b'' and buffer[0] == 11):
            # Handle GAME
            Error.sendError(cSkt, 0)
            continue
        elif (buffer != b'' and buffer[0] == 12):
            # Handle LEAVE
            leave = Leave.recvLeave(cSkt)
            Client.removeClient(cSkt)
            break
        elif (buffer != b'' and buffer[0] == 13):
            # Handle CONNECTION
            Error.sendError(cSkt, 0)
            continue
        elif (buffer != b'' and buffer[0] == 14):
            # Handle VERSION
            Error.sendError(cSkt, 0)
            continue
        else:
            print('ERROR: Invalid message detected!')
            continue

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
    clientSkt, clientAddr = serverSkt.accept()                                                      # Accept & assign client socket & address
    #print('DEBUG: Client Socket:', clientSkt)
    #print('DEBUG: Client Address:', clientAddr)

    Client.addClient(clientSkt)
    Client.getClients()

    clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()    # Create thread for connected client and starts it
    #print("DEBUG: Client Thread:", clientThread)