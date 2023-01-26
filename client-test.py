import socket   # Import necessary module
import struct

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Establish socket
print('DEBUG: skt  =', skt)

# Assign host IP/name and port number
host = 'localhost' # Should use socket.gethostname()
port = 5125

print('DEBUG: host =', host)
print('DEBUG: port =', port)

skt.connect((host, port))   # Connect to server
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