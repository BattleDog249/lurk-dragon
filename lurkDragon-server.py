'''
CS435 LurkDragon: Server
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

# Import socket module, necessary for network communications
import socket

# Function for sending VERSION message to client
def sendVersion(type = 14, major = 2, minor = 3, extensionSize = 0, extensionList = 0):
    '''
    Sent by the server upon initial connection along with GAME.
    '''
    client_fd.send(int.to_bytes(type, 'little', signed=False))
    client_fd.send(int.to_bytes(major, 'little', signed=False))
    client_fd.send(int.to_bytes(minor, 'little', signed=False))
    client_fd.send(int.to_bytes(extensionSize, 'little', signed=False))
    client_fd.send(int.to_bytes(extensionList, 'little', signed=False))
    return 0

# Function for sending GAME message to client
def sendGame(type = 11, initPoints = 100, statLimit = 65535, desLen = 19, description = 'Description default'):
    '''
    Used by the server to describe the game. The initial points is a combination of health, defense, and regen, and cannot be exceeded by the client when defining a new character.
    The stat limit is a hard limit for the combination for any player on the server regardless of experience.
    If unused, it should be set to 65535, the limit of the unsigned 16-bit integer.
    This message will be sent upon connecting to the server, and not re-sent.
    '''
    client_fd.send(int.to_bytes(type, 'little', signed=False))
    return 0

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign port number
port = 5126

# Bind server to machine's hostname & assigned port number
skt.bind((socket.gethostname(), port))

# Server listens and waits for 1 client connection
skt.listen(1)
print('Waiting for connection...')

# Accepts connection from client & returns client file descriptor and address
client_fd, addr = skt.accept()
print('\nDEBUG: client_fd: \n', client_fd)
print('\nDEBUG: addr: \n', addr)
    
#sendVersion()
skt.sendall(b'Testing message!')
print('DEBUG: Server message sent!')

#client_msg = skt.recv(1024).decode() # Get message from client and decode
#print('DEBUG: Client {client_fd} message is {client_msg}')
   
# Close connection to client
skt.close()