'''
    Python Testing Client
    Author: Logan Hunter Gray
'''

import socket

skt=socket.socket() #creating the socket

host = 'localhost' # Should use socket.gethostname()
port = 5125

skt.connect((host, port)) #connecting to the server

print("The message from the server is ", skt.recv(1024).decode())
#receiving the TCP message and printing it. Since the message is sent in bytes, we have to decode it before printing

skt.send(bytes('Happy to connect with you!','utf-8')) #sending the TCP message to the server in bytes form

skt.close() #This stops the connection