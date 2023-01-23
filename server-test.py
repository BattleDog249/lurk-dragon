'''
    Python Testing Server
    Author: Logan Hunter Gray
'''

import socket

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket named skt

host = 'localhost'  # Should use socket.gethostname()
port = 5125         # Testing port number

skt.bind((host, port))  # Bind to IP address of server and provided port number

skt.listen(5) # Listens and waits for 1 client

print('Waiting for connection...')

while True:
    client, addr = skt.accept() #this function accepts the connection from client and returns the client name and its address

    client.send(bytes('DEBUG: Connected to the server-test.py', 'utf-8')) #sending a TCP message to the client in the form of bytes 

    client_msg = skt.recv(1024).decode() #getting the TCP message from the client and decoding it 
    
    print(f'The message from the client {client} is {client_msg}') #printing the message
    
    skt.close() #This stops the connection