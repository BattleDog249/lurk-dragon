import socket   # Import necessary module

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Establish socket
print('DEBUG: skt  = ', skt)

# Assign host IP/name and port number
host = 'localhost'  # Should use socket.gethostname()
port = 5125         # Testing port number
maxConnections = 2  # Assign number of connections server can handle
print('DEBUG: host = ', host)
print('DEBUG: port = ', port)
print('DEBUG: max  = ', maxConnections)

skt.bind((host, port))  # Bind to IP address of server and provided port number

skt.listen(maxConnections) # Listens and waits for 1 client

print('DEBUG: Listening...')

# Loop for each client that connects
while True:
    # Accepts connection from client & returns client name and address
    client_fd, addr = skt.accept()
    print('\nDEBUG: client_fd: \n', client_fd)
    print('\nDEBUG: addr: \n', addr)
    
    client_fd.send('Connected to server-test.py'.encode()) #sending a TCP message to the client in the form of bytes 
    print('DEBUG: Server message sent')


    #client_msg = skt.recv(1024).decode() #getting the TCP message from the client and decoding it 
    
    #print(f'The message from the client {client} is {client_msg}') #printing the message
    
    skt.close() #This stops the connection
    print('DEBUG: Closed connection')