'''
CS435 LurkDragon: Server
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

# Import socket module, necessary for network communications
import socket
# Import threading module, required for multithreading & handling multiple clients
import threading

# Import custom lurk module
from lurk import *

# Function for handling individual clients
#   cSkt: Client socket to handle
def handleClient(cSkt):
    version = Version.sendVersion(cSkt)    # Send VERSION to given client
    if (version != 0):
        print('WARN: sendVersion() returned unexpected code', version, 'for client', cSkt)
        return 2
    game = Game.sendGame(cSkt)                # Send GAME to given client
    if (game != 0):
        print('WARN: sendGame() returned unexpected code', game, 'for client', cSkt)
        return 2
    buffer = cSkt.recv(1024)
    while buffer != None:         # While loop to listen for any potential messages received from client
        if (buffer[0] == 1):
            # Handle MESSAGE
            pass
        elif (buffer[0] == 2):
            # Handle CHANGEROOM
            pass
        elif (buffer[0] == 3):
            # Handle FIGHT
            pass
        elif (buffer[0] == 4):
            # Handle PVPFIGHT
            pass
        elif (buffer[0] == 5):
            # Handle LOOT
            pass
        elif (buffer[0] == 6):
            # Handle START
            pass
        elif (buffer[0] == 7):
            # Handle ERROR
            pass
        elif (buffer[0] == 8):
            # Handle ACCEPT
            pass
        elif (buffer[0] == 9):
            # Handle ROOM
            pass
        elif (buffer[0] == 10):
            # Handle CHARACTER
            characterBuffer = buffer
            name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes = Character.recvCharacter(cSkt, characterBuffer)
            
            # If stats and CHARACTER message is valid, send ACCEPT
            if (attack + defense + regen <= Game.initPoints):
                print('DEBUG: Detected valid stats, sending ACCEPT!')
                accept = Accept.sendAccept(cSkt, 10)
                room = Room.sendRoom(cSkt, 0)
                buffer = None
            else:
                print('DEBUG: Detected invalid stats, sending ERROR type 4!')
                error = Error.sendError(cSkt, 4)
                characterBuffer = buffer
                name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes = Character.recvCharacter(cSkt, characterBuffer)
                accept = Accept.sendAccept(cSkt, 10)
                room = Room.sendRoom(cSkt, 0)
                buffer = None
                
            buffer = None
        elif (buffer[0] == 11):
            # Handle GAME
            pass
        elif (buffer[0] == 12):
            # Handle LEAVE
            cSkt.shutdown(2)    # Not necessary AFAIK, testing
            cSkt.close(cSkt)        # Close connection to server
            buffer = None
        elif (buffer[0] == 13):
            # Handle CONNECTION
            pass
        elif (buffer[0] == 14):
            # Handle VERSION
            pass
        else:
            buffer = None

# Create dictionary to track connected clients
clients = {}

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign address & port number
# Logan's assigned range: 5010 - 5014
# Testing 5195 for isoptera, connection refused on assigned ports...
address = 'localhost'
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

    clients[clientSkt] = clientSkt.fileno()                                                         # Add file descriptor to dictionary for tracking connections
    #print('DEBUG: Connected Clients: ', clients)

    clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()    # Create thread for connected client and starts it
    #print("DEBUG: Client Thread:", clientThread)