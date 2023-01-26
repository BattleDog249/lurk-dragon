'''
    Due Wednesday, February 1
    Connect to port 5071 on isoptera.
    There is a server running on that port that will send you 5 32-bit integers in big endian order.
    Upload a text file with your name, the integers isoptera sent you, and explain how you received them (include source code if you wrote it).
    You are welcome to start with the simple_client.c program from class, but you can just start your own program if you prefer. 
'''

import socket
import struct

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

skt.connect(('74.118.22.194', 5071))

message = skt.recv(2048)

print(message)

value = int.from_bytes(message, 'big', signed = False)

print(value)