import socket   # Import necessary module

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Establish socket
print('DEBUG: skt  =', skt)

# Assign host IP/name and port number
host = 'localhost' # Should use socket.gethostname()
port = 5125

print('DEBUG: host =', host)
print('DEBUG: port =', port)

skt.connect((host, port))   # Connect to server
print('DEBUG: Connecting to server:', host)

# Recieve TCP message and print it
# Since the message is sent in bytes, we have to decode it before printing
print('DEBUG: Recieved server message:', skt.recv(1024).decode())

# Send TCP message to server in bytes form
#skt.send(bytes('Happy to connect with you!','utf-8'))

skt.close() # Close connection to server
print('DEBUG: Closed connection')