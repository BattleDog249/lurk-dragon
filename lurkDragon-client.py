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
port = 5125

# Connect to server with assigned host & port
skt.connect((socket.gethostname(), port))
print('DEBUG: Connecting to server:', host)

buffer = ''
while len(buffer) < 4:
    buffer += skt.recv(8)
num = struct.unpack('!i', buffer[:4])[0]

# Recieve TCP message and print it
# Since the message is sent in bytes, we have to decode it before printing
print('DEBUG: Recieved server message:', num)

# Send TCP message to server in bytes form
#skt.send('Happy to connect with you!'.encode())

skt.close() # Close connection to server
print('DEBUG: Closed connection')