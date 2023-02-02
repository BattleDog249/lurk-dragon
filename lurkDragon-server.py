'''
CS435 LurkDragon: Server
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

# Import socket module, necessary for network communications
import socket
import struct

gameDescription = "This is Logan's testing server description! Not very exciting, yet......"

# Function for sending VERSION message to client
def sendVersion(t = 14, major = 2, minor = 3, extSize = 0):
    '''
    Sent by the server upon initial connection along with GAME.
    '''
    versionBytes = struct.pack("<3BH", t, major, minor, extSize)
    #print(versionBytes)
    #versionMsg = struct.unpack("<bbbh", versionBytes)
    #print(versionMsg)
    clientSkt.sendall(versionBytes)
    print('DEBUG: VERSION sent!')
    return 0

# Function for sending GAME message to client
def sendGame(t = 11, initPoints = 100, statLimit = 65535):
    '''
    Used by the server to describe the game. The initial points is a combination of health, defense, and regen, and cannot be exceeded by the client when defining a new character.
    The stat limit is a hard limit for the combination for any player on the server regardless of experience.
    If unused, it should be set to 65535, the limit of the unsigned 16-bit integer.
    This message will be sent upon connecting to the server, and not re-sent.
    '''
    gameBytes = struct.pack("<B3H", t, initPoints, statLimit, len(gameDescription)) #gameDescription)  # Not yet sure what format to use for gameDescription
    desBytes = bytes(gameDescription, 'utf-8')
    #print(gameBytes)
    #print(desBytes)
    #gameMsg = struct.unpack("<B3H", gameBytes)
    #print(gameMsg)
    clientSkt.sendall(gameBytes)
    clientSkt.sendall(desBytes)
    print('DEBUG: GAME sent!')
    return 0

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign port number
port = 5126

# Bind server to machine's hostname & assigned port number
serverSkt.bind((socket.gethostname(), port))

# Server listens and queue up to 5 connections before refusing more
serverSkt.listen(5)
print('Waiting for connection...')

while True:
    # Accepts connection from client & returns client socket (file descriptor) and address
    clientSkt, addr = serverSkt.accept()            # Accept & assign client connection to clientSkt
    print('DEBUG: Client Socket:', clientSkt)
    print('DEBUG: Client Address:', addr)
    sendVersion()                                   # Send VERSION to client
    sendGame()                                      # Send GAME to client

#client_msg = skt.recv(1024).decode() # Get message from client and decode
#print('DEBUG: Client {client_fd} message is {client_msg}')