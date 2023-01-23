'''
    Python Testing Client
    Author: Logan Hunter Gray
'''

import socket   # Import necessary module

skt = socket.socket() # Establish socket

# Assign host IP/name and port number
host = 'localhost' # Should use socket.gethostname()
port = 5125

skt.connect((host, port))   # Connect to server

# Recieve TCP message and print it
# Since the message is sent in bytes, we have to decode it before printing
print('DEBUG: Recieved server message: ', skt.recv(1024).decode())

#skt.send(bytes('Happy to connect with you!','utf-8')) #sending the TCP message to the server in bytes form

skt.close() # Close connection to server