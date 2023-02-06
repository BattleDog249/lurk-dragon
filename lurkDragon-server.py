'''
CS435 LurkDragon: Server
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
    NOTES:
        Perhaps a more efficient approach would be using the pickle module to serialize & send dictionaries directly? Not sure...
'''

# Import socket module, necessary for network communications
import socket
# Import struct module, required for packing/unpacking structures
import struct
# Import threading module, required for multithreading & handling multiple clients
import threading

# Description of the game, sent in GAME message to client
gameDescription = "This is Logan's testing server description! Not very exciting, thus far...."

# VERSION dictionary
version = {
        'type': 14,
        'major': 2,
        'minor': 3,
        'extSize': 0
    }

# GAME dictionary
game = {
    'type': 11,
    'initPoints': 100,
    'statLimit': 65535,
    'gameDesLen': len(gameDescription),
    'gameDes': bytes(gameDescription, 'utf-8')
}

# Function for sending VERSION message to client
def sendVersion():
    """
    Sent by the server upon initial connection along with GAME.
    """
    versionPacked = struct.pack('<3BH', version['type'], version['major'], version['minor'], version['extSize'])
    #print('DEBUG: Packed version =', versionPacked)
    
    #versionUnpacked = struct.unpack('<3BH', versionPacked)
    #print('DEBUG: Unpacked version =', versionUnpacked)
    
    clientSkt.sendall(versionPacked)
    #print('DEBUG: VERSION sent!')
    
    return 0

# Function for sending GAME message to client
def sendGame():
    """
    Used by the server to describe the game. The initial points is a combination of health, defense, and regen, and cannot be exceeded by the client when defining a new character.
    The stat limit is a hard limit for the combination for any player on the server regardless of experience.
    If unused, it should be set to 65535, the limit of the unsigned 16-bit integer.
    This message will be sent upon connecting to the server, and not re-sent.
    """
    gamePacked = struct.pack('<B3H%ds' %game['gameDesLen'], game['type'], game['initPoints'], game['statLimit'], game['gameDesLen'], game['gameDes'])
    #print('DEBUG: Packed game =', gamePacked)
    
    #gameUnpacked = struct.unpack('<B3H%ds' %game['gameDesLen'], gamePacked)
    #print('DEBUG: Unpacked game =', gameUnpacked)
    
    clientSkt.sendall(gamePacked)
    #print('DEBUG: GAME sent!')
    
    return 0

def recvCharacter():
    """
    NEEDS WORK
    """
    characterMsg = struct.unpack('<B32sB7H', clientSkt.recv(48))
    characterDes = clientSkt.recv(characterMsg[9])
    print('DEBUG: Received CHARACTER message:', characterMsg)
    print('DEBUG: Received CHARACTER Description:', characterDes.decode())
    return 0
    

def initConnect():
    """
    Executed when a client connects to the server, sends VERSION & GAME message to client
    """
    version = sendVersion()
    game = sendGame()
    character = recvCharacter()
    return 0

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign port number
port = 5195

# Bind server to machine's hostname & assigned port number
serverSkt.bind((socket.gethostname(), port))

# Server listens and queue up to 5 connections before refusing more
serverSkt.listen(5)
print('Waiting for connection...')

while True:
    # Accepts connection from client & returns client socket (file descriptor) and address
    clientSkt, addr = serverSkt.accept()                    # Accept & assign client connection to clientSkt
    print('DEBUG: Client Socket:', clientSkt)
    print('DEBUG: Client Address:', addr)
    clientThread = threading.Thread(target = initConnect)   # Create thread for connected client
    clientThread.start()                                    # Start thread
    print("DEBUG: Client Thread:", clientThread)