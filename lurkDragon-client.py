'''
CS435 LurkDragon: Client
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

# Import socket module, required for network communications
import socket
# Import struct module, required for packing/unpacking structures
import struct

def recvAccept(buffer):
    type, message = struct.unpack('<2B', buffer)
    print('DEBUG: Received ACCEPT message!')
    print('DEBUG: ACCEPT Bytes:', buffer)
    print('DEBUG: Type:', type)
    print('DEBUG: Message Type accepted:', message)
    return 0

# Function for receiving GAME message from server
def recvGame():
    gameBuffer = skt.recv(7)
    type, initPoints, statLimit, gameDesLen = struct.unpack("<B3H", gameBuffer[0:7])
    game_des = skt.recv(gameDesLen)                    # Read game description, recv only description length
    print('DEBUG: Received GAME message!')
    print('DEBUG: GAME Bytes:', gameBuffer)
    print('DEBUG: Type:', type)
    print('DEBUG: Initial Points:', initPoints)
    print('DEBUG: Stat Limit:', statLimit)
    print('DEBUG: Game Description Length:', gameDesLen)
    print('DEBUG: GAME Description:', game_des.decode())
    return 0


# Function to receive an ERROR message from server
# buffer: Buffer to read from
def recvError(buffer):
    errorBuffer = buffer[:4]
    type, errorCode, errMesLen = struct.unpack('<2BH', errorBuffer)
    print('DEBUG: Received ERROR message!')
    print('DEBUG: ERROR Bytes:', buffer)
    print('DEBUG: Type:', type)
    print('DEBUG: ErrorCode:', errorCode)
    print('DEBUG: ErrMesLen:', errMesLen)
    errMesBuffer = buffer[4:4+errMesLen]
    errMes, = struct.unpack('<%ds' %errMesLen, errMesBuffer)
    errMes = errMes.decode('utf-8')
    print('DEBUG: ErrMes:', errMes)
class Character:
    def __init__(self, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes):
        self.type = 10
        self.name = name
        self.flags = flags
        self.attack = attack
        self.defense = defense
        self.regen = regen
        self.health = health
        self.gold = gold
        self.room = room
        self.charDesLen = charDesLen
        self.charDes = charDes
    
    def recvCharacter(self):
        pass
    
    def sendCharacter(self):
        characterPacked = struct.pack('<B32sB7H%ds' %self.charDesLen, self.type, bytes(self.name, 'utf-8'), self.flags, self.attack, self.defense, self.regen, self.health, self.gold, self.room, len(self.charDes), bytes(self.charDes, 'utf-8'))
        #print('DEBUG: Packed version =', characterPacked)
        
        #characterUnpacked = struct.unpack('<B32sB7H%ds', characterPacked)
        #print('DEBUG: Unpacked version =', characterUnpacked)
        
        skt.sendall(characterPacked)
        #print('DEBUG: CHARACTER sent!')
        
        return 0

class Version:
    """
    Sent by the server upon initial connection along with GAME. If no VERSION is received, the server can be assumed to support only LURK 2.0 or 2.1. 
    """
    
    type = int(14)
    major = int(2)
    minor = int(3)
    extSize = int(0)
    
    #Function for receiving VERSION message from server
    def recvVersion():
        versionBuffer = skt.recv(5)
        type, major, minor, extSize = struct.unpack('<3BH', versionBuffer)
        print('DEBUG: Received VERSION message!')
        print('DEBUG: VERSION Bytes:', versionBuffer)
        print('DEBUG: Type: ', type)
        print('DEBUG: Major:', major)
        print('DEBUG: Minor:', minor)
        print('DEBUG: Ext. Size: ', extSize)
        return 0
    
    # Function for sending VERSION message to server
    def sendVersion(self):
        versionPacked = struct.pack('<3BH', self.type, self.major, self.minor, self.extSize)
        #print('DEBUG: Packed version =', versionPacked)
        
        #versionUnpacked = struct.unpack('<3BH', versionPacked)
        #print('DEBUG: Unpacked version =', versionUnpacked)
        
        skt.sendall(versionPacked)
        #print('DEBUG: VERSION sent!')
        
        return 0

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining host address & port of server to connect to
host = 'localhost'
port = 5010

# Connect to server with assigned host & port
skt.connect((socket.gethostname(), port))
print('DEBUG: Connecting to server:', host)

version = Version.recvVersion()
game = recvGame()

if game == 0:
    characterDescription = "This is a test dummy description tester! Testing, testing! Ag"
    character = Character("Test Dummy # 512", 0x4, 25, 25, 100, 20, 100, 40, len(characterDescription), characterDescription)
    character.sendCharacter()
    print('DEBUG: Successfully received VERSION & GAME message, sent CHARACTER message in response!')

    buffer = skt.recv(128)
    if (buffer[0] == 8):
        accept = recvAccept(buffer[:2])
        if (accept != 0):
            print('WARN: recvAccept() returned unexpected code', accept)
            exit
    elif (buffer[0] == 7):
        error = recvError(buffer)
        character = Character("Test Dummy # 512", 0x4, 25, 25, 50, 20, 100, 40, len(characterDescription), characterDescription)
        character.sendCharacter()
        

else:
    print('ERROR: Failed to receive GAME message, not sending CHARACTER message!')

skt.shutdown(2) # Not necessary AFAIK
skt.close() # Close connection to server
#print('DEBUG: Closed connection')