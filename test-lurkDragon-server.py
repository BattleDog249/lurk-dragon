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
    
# Function to send an ERROR message to a client
# code: Integer of error code to send to client
def sendError(skt, code):
    errorCodes = {
        0: 'ERROR: Other!',
        1: 'ERROR: Bad Room! Attempt to change to an inappropriate room.',
        2: 'ERROR: Player Exists. Attempt to create a player that already exists.',
        3: 'ERROR: Bad Monster. Attempt to loot a nonexistent or not present monster.',
        4: 'ERROR: Stat error. Caused by setting inappropriate player stats. Try again!',
        5: 'ERROR: Not Ready. Caused by attempting an action too early, for example changing rooms before sending START or CHARACTER.',
        6: 'ERROR: No target. Sent in response to attempts to loot nonexistent players, fight players in different rooms, etc.',
        7: 'ERROR: No fight. Sent if the requested fight cannot happen for other reasons (i.e. no live monsters in room)',
        8: 'ERROR: No player vs. player combat on the server. Servers do not have to support player-vs-player combat.'
    }
    type = int(7)
    errorCode = int(code)
    errMesLen = len(errorCodes[code])
    errMes = errorCodes[code].encode('utf-8')
    errorPacked = struct.pack('<2BH%ds' %errMesLen, type, errorCode, errMesLen, errMes)
    #print('DEBUG: Sending ERROR Message!')
    #print('DEBUG: ERROR Bytes:', errorPacked)
    skt.sendall(errorPacked)

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

def sendRoom(skt, roomNum):
    type = int(9)
    roomNum = int(roomNum)
    roomName = str('Test Room')
    roomDes = str('This is a testing room, like floating in a white void...')
    
    roomPacked = struct.pack('<BH32s%ds', type, roomNum, bytes(roomName, 'utf-8'), len(roomDes), roomDes)
    
    skt.sendall(roomPacked)
    return 0

class Game:
    """
    Used by the server to describe the game. The initial points is a combination of health, defense, and regen, and cannot be exceeded by the client when defining a new character.
    The stat limit is a hard limit for the combination for any player on the server regardless of experience.
    If unused, it should be set to 65535, the limit of the unsigned 16-bit integer.
    This message will be sent upon connecting to the server, and not re-sent.
    """
    
    type = int(11)
    initPoints = int(100)
    statLimit = int(65535)
    gameDes = bytes(str("Logan's Lurk 2.3 server, completely incomplete!"), 'utf-8')
    gameDesLen = int(len(gameDes))
    
    # Function for sending GAME message to client
    def sendGame(self, skt):
        gamePacked = struct.pack('<B3H%ds' %self.gameDesLen, self.type, self.initPoints, self.statLimit, self.gameDesLen, self.gameDes)
        #print('DEBUG: Packed game =', gamePacked)
        
        #gameUnpacked = struct.unpack('<B3H%ds' %game['gameDesLen'], gamePacked)
        #print('DEBUG: Unpacked game =', gameUnpacked)
        
        skt.sendall(gamePacked)
        #print('DEBUG: GAME sent!')
        
        return 0

class Version:
    """
    Sent by the server upon initial connection along with GAME. If no VERSION is received, the server can be assumed to support only LURK 2.0 or 2.1. 
    """
    
    type = int(14)
    major = int(2)
    minor = int(3)
    extSize = int(0)
    
    # Function for receiving VERSION message from client
    def recvVersion():
        type, major, minor, extSize = struct.unpack('<3BH', clientSkt.recv(5))
        print('DEBUG: Received VERSION message!')
        print('DEBUG: Type: ', type)
        print('DEBUG: Major:', major)
        print('DEBUG: Minor', minor)
        print('DEBUG: Ext. Size: ', extSize)
        return 0
    
    # Function for sending VERSION message to client
    def sendVersion(self, skt):
        versionPacked = struct.pack('<3BH', self.type, self.major, self.minor, self.extSize)
        #print('DEBUG: Packed version =', versionPacked)
        
        #versionUnpacked = struct.unpack('<3BH', versionPacked)
        #print('DEBUG: Unpacked version =', versionUnpacked)
        
        skt.sendall(versionPacked)
        #print('DEBUG: VERSION sent!')
        
        return 0

# Function for handling individual clients
# cSkt: Client socket to handle
def handleClient(cSkt):
    version = Version.sendVersion(Version, cSkt)    # Send VERSION to given client
    if (version != 0):
        print('WARN: sendVersion() returned unexpected code', version, 'for client', cSkt)
        return 2
    game = Game.sendGame(Game, cSkt)                # Send GAME to given clien
    if (game != 0):      # Send GAME to given client
        print('WARN: sendGame() returned unexpected code', game, 'for client', cSkt)
        return 2
    buffer = cSkt.recv(1024)
    while buffer != None:         # While loop to listen for any potential messages received from client
        if (buffer[0] == 1):
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
            
            # If stats and CHARACTER message is valid, send ACCEPT
            if (attack+defense+regen <= Game.initPoints):
                sendAccept(cSkt, 10)
                buffer = None
            else:
                sendError(cSkt, 4)
                buffer = None
                
            buffer = None
        elif (buffer[0] == 11):
            # Handle GAME
            pass
        elif (buffer[0] == 12):
            # Handle LEAVE
            cSkt.shutdown(2)    # Not necessary AFAIK, testing
            cSkt.close(cSkt)        # Close connection to server
        elif (buffer[0] == 13):
            # Handle CONNECTION
            pass
        elif (buffer[0] == 14):
            # Handle VERSION
            pass
        else:
            buffer = None

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if (serverSkt == 1):
    print('ERROR: Server socket could not be established!')
    

# Assign port number
# Logan's assigned range: 5010 - 5014
# Testing 5195 for isoptera, connection refused on assigned ports... Debugging
port = 5195

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