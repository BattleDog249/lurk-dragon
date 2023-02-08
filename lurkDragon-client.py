'''
CS435 LurkDragon: Client
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

# Import socket module, required for network communications
import socket
# Import struct module, required for packing/unpacking structures
import struct

# Function for receiving VERSION message from server
def recvVersion():
    versionUnpacked = struct.unpack('<3BH', skt.recv(5))
    print('DEBUG: Received VERSION message:', versionUnpacked)
    return 0

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

def sendCharacter(t = 10, name = "Test Dummy: ID 1 - Cannot > 32By", flags = 0, attack = 50, defense = 25, regen = 5, health = 20, gold = 0, room = 0):
    """
    Function to send CHARACTER message to server
    """
    charDes = "This is a test dummy, don't feel bad for it. It is not sentient!"
    characterPacked = struct.pack('<B32sB7H%ds' %charDes, t, bytes(name, 'utf-8'), flags, attack, defense, regen, health, gold, room, len(charDes), bytes(charDes, 'utf-8'))
    #desBytes = bytes(characterDescription, 'utf-8')
    skt.sendall(characterPacked)
    return 0

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining host address & port of server to connect to
host = 'localhost'
port = 5010

# Connect to server with assigned host & port
skt.connect((socket.gethostname(), port))
print('DEBUG: Connecting to server:', host)

version = recvVersion()
game = recvGame()

if game == 0:
    characterDescription = "This is a test dummy, don't feel bad for it. It is not sentient!"
    character = Character("Test Dummy", 0, 50, 25, 5, 20, 0, 0, len(characterDescription), characterDescription)
    character.sendCharacter()
    print('DEBUG: Successfully received GAME message, sent CHARACTER message in response!')
else:
    print('ERROR: Failed to receive GAME message, not sending CHARACTER message!')

skt.shutdown(2) # Not necessary AFAIK
skt.close() # Close connection to server
#print('DEBUG: Closed connection')