import socket   # Import necessary module
import struct
import sys
import threading

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Establish socket
if (skt == -1):
    print('ERROR: skt not what is expected!')
print('DEBUG: skt  = ', skt)

# Assign host IP/name and port number
host = 'localhost'  # Should use socket.gethostname()
port = 5125         # Testing port number
print('DEBUG: host = ', host)
print('DEBUG: port = ', port)

skt.bind((host, port))  # Bind to IP address of server and provided port number

skt.listen() # Listens and waits for 1 client

print('DEBUG: Listening...')

# Loop for each client that connects
while 1:
    # Accepts connection from client & returns client name and address
    client_fd, addr = skt.accept()
    print('\nDEBUG: client_fd: \n', client_fd)
    print('\nDEBUG: addr: \n', addr)
    
    type = 14
    majorVersion = int(2)
    minorVersion = int(3)
    
    val = struct.pack('!i', majorVersion)
    
    client_fd.send(val) # Send message to client 
    print('DEBUG: Server message sent!')

    #client_msg = skt.recv(1024).decode() # Get message from client and decode
    #print('DEBUG: Client {client_fd} message is {client_msg}')
    
    skt.close() # Close connection to client
    #print('DEBUG: Closed connection')