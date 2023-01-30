'''
    Author: Logan Gray
    Email: lhgray@lcmail.lcsc.edu
    Instructions:
        Due Wednesday, February 1, 2023
        Connect to port 5071 on isoptera.
        There is a server running on that port that will send you 5 32-bit (20 bytes total) integers in big endian order.
        Upload a text file with your name, the integers isoptera sent you, and explain how you received them (include source code if you wrote it).
        You are welcome to start with the simple_client.c program from class, but you can just start your own program if you prefer.
'''

# Import socket module, necessary for network communications
import socket

# Length in bytes of message being received
expectedBytes = 5

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining IP address & port of server to connect to
address = 'isoptera.lcsc.edu'
port = 5071

# Connect to server defined with above variables
skt.connect((socket.gethostbyname(address), port))

# Receive bytes from server, store in 32 byte buffer
# For this assignment, server always sends 20 bytes, which fits inside 32 byte buffer
bytes = skt.recv(32)
print('Full Raw Message: ', bytes)

# Variables used to determine amount of bytes to read for each loop
start = 1
end = 4

# Loop through whole message, reading 4 bytes each loop
for i in range(1, expectedBytes + 1):
    value = int.from_bytes(bytes[start:end], 'big', signed = False)
    print('Converting bytes', bytes[start:end])
    print('Integer value', i,':', value)
    start += 4
    end += 4