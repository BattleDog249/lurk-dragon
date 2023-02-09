'''
CS435 LurkDragon: Client
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

# Import socket module, required for network communications
import socket
# Import struct module, required for packing/unpacking structures
import struct

# Function for receiving GAME message from server
def recvGame():
    gameUnpacked = struct.unpack("<B3H", skt.recv(7))
    game_des = skt.recv(gameUnpacked[3])                    # Read game description, recv only description length
    print('DEBUG: Received GAME:', gameUnpacked)
    print('DEBUG: Received GAME Description:', game_des.decode())
    return 0

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
        type, major, minor, extSize = struct.unpack('<3BH', skt.recv(5))
        print('DEBUG: Received VERSION message!')
        print('DEBUG: Type: ', type)
        print('DEBUG: Major:', major)
        print('DEBUG: Minor', minor)
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
    characterDescription = "This is a test dummy description tester!"
    character = Character("Test Dummy # 512", 0, 50, 25, 5, 20, 0, 0, len(characterDescription), characterDescription)
    character.sendCharacter()
    print('DEBUG: Successfully received GAME message, sent CHARACTER message in response!')
else:
    print('ERROR: Failed to receive GAME message, not sending CHARACTER message!')

skt.shutdown(2) # Not necessary AFAIK
skt.close() # Close connection to server
#print('DEBUG: Closed connection')