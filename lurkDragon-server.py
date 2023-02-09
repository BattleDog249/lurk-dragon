'''
CS435 LurkDragon: Server
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
    NOTES:
        Perhaps a more efficient approach would be using the pickle module to serialize & send dictionaries directly? Not sure...
        Maybe use a class instead of dictionaries to store VERSION and GAME information?
'''

# Import socket module, necessary for network communications
import socket
# Import struct module, required for packing/unpacking structures
import struct
# Import threading module, required for multithreading & handling multiple clients
import threading

# Description of the game, sent in GAME message to client
gameDescription = "This is Logan's testing server description! Fun stuff."

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
    gameDes = bytes(str("This is Logan's testing server description! Fun stuff."), 'utf-8')
    gameDesLen = int(len(gameDes))
    
    # Function for sending GAME message to client
    def sendGame(self):
        gamePacked = struct.pack('<B3H%ds' %self.gameDesLen, self.type, self.initPoints, self.statLimit, self.gameDesLen, self.gameDes)
        #print('DEBUG: Packed game =', gamePacked)
        
        #gameUnpacked = struct.unpack('<B3H%ds' %game['gameDesLen'], gamePacked)
        #print('DEBUG: Unpacked game =', gameUnpacked)
        
        clientSkt.sendall(gamePacked)
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
    def sendVersion(self):
        versionPacked = struct.pack('<3BH', self.type, self.major, self.minor, self.extSize)
        #print('DEBUG: Packed version =', versionPacked)
        
        #versionUnpacked = struct.unpack('<3BH', versionPacked)
        #print('DEBUG: Unpacked version =', versionUnpacked)
        
        clientSkt.sendall(versionPacked)
        #print('DEBUG: VERSION sent!')
        
        return 0

class Character:
    """
    Sent by both the client and the server. The server will send this message to show the client changes to their player's status, such as in health or gold.
    The server will also use this message to show other players or monsters in the room the player is in or elsewhere.
    The client should expect to receive character messages at any time, which may be updates to the player or others.
    If the player is in a room with another player, and the other player leaves, a CHARACTER message should be sent to indicate this.
    In many cases, the appropriate room for the outgoing player is the room they have gone to. If the player goes to an unknown room, the room number may be set to a room that the player will not encounter (does not have to be part of the map).
    This could be accompanied by a narrative message (for example, "Glorfindel vanishes into a puff of smoke"), but this is not required.
    The client will use this message to set the name, description, attack, defense, regen, and flags when the character is created. It can also be used to reprise an abandoned or deceased character.
    """
    
    type = int(10)
    '''
    def __init__(self, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes):
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
    '''

    def recvCharacter(self):
        """
        NEEDS WORK
        """
        characterBuffer = clientSkt.recv(1024)
        print('DEBUG: Received CHARACTER:', characterBuffer)
        type, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', characterBuffer[0:48])
        name = name.decode('utf-8')
        i = charDesLen + 48
        charDes = struct.unpack('<%ds' %charDesLen , characterBuffer[48:i])
        charDes = ''.join(map(str, charDes))    # Converts the character description from a tuple containing bytes to just bytes
        print('DEBUG: Type:', type)
        print('DEBUG: Name:', name)
        print('DEBUG: Flags:', flags)
        print('DEBUG: Attack', attack)
        print('DEBUG: Defense:', defense)
        print('DEBUG: Regen:', regen)
        print('DEBUG: Health:', health)
        print('DEBUG: Gold:', gold)
        print('DEBUG: Room', room)
        print('DEBUG: charDesLen:', charDesLen)
        print('DEBUG: i:', i)
        print('DEBUG: charDes:', charDes)
        
        if (attack+defense+regen > Game.initPoints):
            print('Character\'s stats are higher than initPoints!')
            return 1
        return 0
            

    def sendCharacter(self):
        pass    

def initConnect():
    """
    Executed when a client connects to the server, sends VERSION & GAME message to client, and receives CHARACTER message from client
    """
    version = Version()
    version.sendVersion()
    
    game = Game()
    game.sendGame()
    
    character = Character()
    character.recvCharacter()
    
    return 0

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
    clientSkt, addr = serverSkt.accept()                    # Accept & assign client connection to clientSkt
    print('DEBUG: Client Socket:', clientSkt)
    print('DEBUG: Client Address:', addr)
    clientThread = threading.Thread(target = initConnect)   # Create thread for connected client
    clientThread.start()                                    # Start thread
    print("DEBUG: Client Thread:", clientThread)