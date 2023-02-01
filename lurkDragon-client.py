'''
CS435 LurkDragon: Client
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

# Import socket module, necessary for network communications
import socket
import struct

# Function for receiving VERSION message from server
def recvVersion():
    return 0

# Function for receiving GAME message from server
def recvGame():
    return 0

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining host address & port of server to connect to
host = 'localhost'
port = 5126

# Connect to server with assigned host & port
skt.connect((socket.gethostname(), port))
print('DEBUG: Connecting to server:', host)

# Recieve TCP message and print it
# Since the message is sent in bytes, we have to decode it before printing
version_msg = skt.recv(1024)#.decode() # Get message from server and decode
print('DEBUG: Received server message:', version_msg.decode())

# Send TCP message to server in bytes form
#skt.send('Happy to connect with you!'.encode())

skt.close() # Close connection to server
print('DEBUG: Closed connection')