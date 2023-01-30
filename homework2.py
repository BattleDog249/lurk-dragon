'''
    Due Wednesday, February 1
    Connect to port 5071 on isoptera.
    There is a server running on that port that will send you 5 32-bit (20 bytes total) integers in big endian order.
    Upload a text file with your name, the integers isoptera sent you, and explain how you received them (include source code if you wrote it).
    You are welcome to start with the simple_client.c program from class, but you can just start your own program if you prefer. 
'''

import socket

address = 'isoptera.lcsc.edu'
port = 5071

# Length in bytes of message being received
expectedBytes = 5

# Establish socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to Isoptera
skt.connect((socket.gethostbyname(address), port))

# Receive 20 bytes, store in 32 byte buffer
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