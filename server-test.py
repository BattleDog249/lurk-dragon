'''
    Python Testing Server
    Author: Logan Hunter Gray
'''

import socket

sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket named sct

sct.bind((socket.gethostname(), 9999))  # Bind to IP address of server and provided port number

sct.listen(1) # Listens and waits for 1 client

print('Waiting for connection...')

