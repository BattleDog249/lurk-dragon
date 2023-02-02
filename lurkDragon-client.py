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
    print('DEBUG: Received GAME message:', game_des)
    return 0

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining host address & port of server to connect to
host = 'localhost'
port = 5126

# Connect to server with assigned host & port
skt.connect((socket.gethostname(), port))
print('DEBUG: Connecting to server:', host)

recvVersion()
recvGame()

skt.close() # Close connection to server
print('DEBUG: Closed connection')