# Import socket module, necessary for network communications
import socket
# Import struct module, required for packing/unpacking structures
import struct
# Import threading module, required for multithreading & handling multiple clients
import threading

# Function for sending ACCEPT message to client
# action: Integer message type that was accepted
def sendAccept(skt, action):
    type = int(8)
    action = int(action)
    acceptPacked = struct.pack('<2B', type, action)
    #print('DEBUG: Sending ACCEPT Message!')
    #print('DEBUG: ACCEPT Bytes:', acceptPacked)
    skt.sendall(acceptPacked)

def sendVersion(skt):
    type = int(14)
    major = int(2)
    minor = int(3)
    extSize = int(0)
    
    versionPacked = struct.pack('<3BH', type, major, minor, extSize)
    #print('DEBUG: Packed version =', versionPacked)
    
    #versionUnpacked = struct.unpack('<3BH', versionPacked)
    #print('DEBUG: Unpacked version =', versionUnpacked)
    
    skt.sendall(versionPacked)
    #print('DEBUG: VERSION sent!')
    
    return 0

#Function for sending GAME message to client
def sendGame(skt):
    type = int(11)
    initPoints = int(100)
    statLimit = int(65535)
    gameDes = bytes(str("Logan's Lurk 2.3 server, completely incomplete!"), 'utf-8')
    gameDesLen = int(len(gameDes))
    
    gamePacked = struct.pack('<B3H%ds' %gameDesLen, type, initPoints, statLimit, gameDesLen, gameDes)
    #print('DEBUG: Packed game =', gamePacked)
    
    #gameUnpacked = struct.unpack('<B3H%ds' %game['gameDesLen'], gamePacked)
    #print('DEBUG: Unpacked game =', gameUnpacked)
    
    skt.sendall(gamePacked)
    #print('DEBUG: GAME sent!')
    
    return 0

'''
def recvCharacter(skt, buffer, desBuffer):
        type, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', buffer)
        charDes = struct.unpack('<%ds' %charDesLen, desBuffer)
        
        #charDes = skt.recv(charDesLen)
        print('DEBUG: Received CHARACTER message!')
        print('DEBUG: CHARACTER Bytes:', buffer)
        print('DEBUG: Type:', type)
        print('DEBUG: Name:', name.decode('utf-8'))
        print('DEBUG: Flags:', flags)
        print('DEBUG: Attack', attack)
        print('DEBUG: Defense:', defense)
        print('DEBUG: Regen:', regen)
        print('DEBUG: Health:', health)
        print('DEBUG: Gold:', gold)
        print('DEBUG: Room', room)
        print('DEBUG: charDesLen:', charDesLen)
        print('DEBUG: charDes:', charDes.decode('utf-8'))

        if (attack+defense+regen > initPoints):
            print('Character\'s stats are higher than initPoints! Assigning valid values')
            attack = 45
            defense = 45
            regen = 5
        
        #Character.sendCharacter()
        sendAccept(10)
        return 0
'''

# Function for handling individual clients
# cSkt: Client socket to handle
def handleClient(cSkt):
    sendVersion(cSkt)   # Send VERSION to given client
    sendGame(cSkt)      # Send GAME to given client
    while True:         # While loop to listen for any potential messages received from client
        buffer = None
        buffer = cSkt.recv(1024)
        if (buffer != b''):
            if (buffer != None and buffer[0] == 1):
                # Handle MESSAGE
                pass
            elif (buffer[0] == 2):
                # Handle CHANGEROOM
                pass
            elif (buffer[0] == 3):
                # Handle FIGHT
                pass
            elif (buffer[0] == 4):
                # Handle PVPFIGHT
                pass
            elif (buffer[0] == 5):
                # Handle LOOT
                pass
            elif (buffer[0] == 6):
                # Handle START
                pass
            elif (buffer[0] == 7):
                # Handle ERROR
                pass
            elif (buffer[0] == 8):
                # Handle ACCEPT
                pass
            elif (buffer[0] == 9):
                # Handle ROOM
                pass
            elif (buffer[0] == 10):
                # Handle CHARACTER
                charBuffer = buffer[:48]
                type, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', charBuffer)
                print('DEBUG: Received CHARACTER message!')
                print('DEBUG: CHARACTER Bytes:', buffer)
                print('DEBUG: Type:', type)
                print('DEBUG: Name:', name.decode('utf-8'))
                print('DEBUG: Flags:', flags)
                print('DEBUG: Attack', attack)
                print('DEBUG: Defense:', defense)
                print('DEBUG: Regen:', regen)
                print('DEBUG: Health:', health)
                print('DEBUG: Gold:', gold)
                print('DEBUG: Room', room)
                print('DEBUG: charDesLen:', charDesLen)
                charDesBuffer = buffer[48:48+charDesLen]
                print('DEBUG: charDesBuffer:', charDesBuffer)
                charDes, = struct.unpack('<%ds' %charDesLen, charDesBuffer)
                charDes = charDes.decode('utf-8')
                print('DEBUG: charDes:', charDes)
                #print('DEBUG: charBuffer:', charBuffer)
                #charReturn = recvCharacter(cSkt, charBuffer, charDesBuffer)
                buffer = None
            elif (buffer[0] == 11):
                # Handle GAME
                pass
            elif (buffer[0] == 12):
                # Handle LEAVE
                cSkt.shutdown(2)    # Not necessary AFAIK, testing
                cSkt.close()        # Close connection to server
            elif (buffer[0] == 13):
                # Handle CONNECTION
                pass
            elif (buffer[0] == 14):
                # Handle VERSION
                pass
        else:
            continue

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if (serverSkt == 1):
    print('ERROR: Server socket could not be established!')
    

# Assign port number
# Logan's assigned range: 5010 - 5014
port = 5010

# Bind server to machine's hostname & assigned port number
serverSkt.bind((socket.gethostname(), port))

# Server listens and queue up to 5 connections before refusing more
serverSkt.listen(5)
print('Waiting for connection...')

while True:
    # Accepts connection from client & returns client socket (file descriptor) and address
    clientSkt, addr = serverSkt.accept()                                # Accept & assign client connection to clientSkt
    print('DEBUG: Client Socket:', clientSkt)
    print('DEBUG: Client Address:', addr)
    clientThread = threading.Thread(target = handleClient(clientSkt))   # Create thread for connected client
    clientThread.start()                                                # Start thread
    print("DEBUG: Client Thread:", clientThread)