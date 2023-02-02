'''
CS435 LurkDragon: Client
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

# Import socket module, required for network communications
import socket
# Import struct module, required for packing/unpacking structures
import struct

# Function for receiving VERSION message from server
def recvVersion():
    version_msg = struct.unpack("<3BH", skt.recv(5))
    print('DEBUG: Received VERSION message:', version_msg)
    return 0

# Function for receiving GAME message from server
def recvGame():
    game_msg = struct.unpack("<B3H", skt.recv(7))
    game_des = skt.recv(game_msg[3])                    # Read game description, recv only description length
    print('DEBUG: Received GAME message:', game_msg)
    print('DEBUG: Received GAME message:', game_des.decode())
    return 0

def sendCharacter(t = 10, name = "Test Dummy", flags = 0, attack = 50, defense = 25, regen = 5, health = 20, gold = 0, room = 0):
    """
    Function to send CHARACTER message to server
    NEEDS WORK
    """
    characterDescription = "This is a test dummy, don't feel bad for it."
    characterBytes = struct.pack('<B%dcB7H' %len(name), t, name, flags, attack, defense, regen, health, gold, room, len(characterDescription))
    desBytes = bytes(characterDescription, 'utf-8')
    skt.sendall(characterBytes)
    skt.sendall(desBytes)
    return 0

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining host address & port of server to connect to
host = 'localhost'
port = 5195

# Connect to server with assigned host & port
skt.connect((socket.gethostname(), port))
print('DEBUG: Connecting to server:', host)

version = recvVersion()
game = recvGame()

if game == 0:
    sendCharacter()
    print('DEBUG: Sent CHARACTER message')

#skt.shutdown(2) # Not necessary AFAIK
#skt.close() # Close connection to server
#print('DEBUG: Closed connection')