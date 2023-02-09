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

# Function for sending ACCEPT message to client
# action: Integer message type that was accepted
def sendAccept(action):
    type = int(8)
    action = int(action)
    acceptPacked = struct.pack('<2B', type, action)
    #print('DEBUG: Sending ACCEPT Message!')
    #print('DEBUG: ACCEPT Bytes:', acceptPacked)
    clientSkt.sendall(acceptPacked)

# Function to send an ERROR message to a client
# code: Integer of error code to send to client
def sendError(code):
    errorCodes = {
        0: 'ERROR: Other!',
        1: 'ERROR: Bad Room! Attempt to change to an inappropriate room.',
        2: 'ERROR: Player Exists. Attempt to create a player that already exists.',
        3: 'ERROR: Bad Monster. Attempt to loot a nonexistent or not present monster.',
        4: 'ERROR: Stat error. Caused by setting inappropriate player stats.',
        5: 'ERROR: Not Ready. Caused by attempting an action too early, for example changing rooms before sending START or CHARACTER.',
        6: 'ERROR: No target. Sent in response to attempts to loot nonexistent players, fight players in different rooms, etc.',
        7: 'ERROR: No fight. Sent if the requested fight cannot happen for other reasons (i.e. no live monsters in room)',
        8: 'ERROR: No player vs. player combat on the server. Servers do not have to support player-vs-player combat.'
    }
    type = int(7)
    errorCode = int(code)
    errMesLen = len(errorCodes[code])
    errMes = errorCodes[code]
    errorPacked = struct.pack('<2BH%ds' %errMesLen, type, errorCode, errMesLen, errMes)
    #print('DEBUG: Sending ERROR Message!')
    #print('DEBUG: ERROR Bytes:', errorPacked)
    clientSkt.sendall(errorPacked)

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
    gameDes = bytes(str("Logan's Lurk 2.3 server, full of surprises!"), 'utf-8')
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
        characterBuffer = clientSkt.recv(48)
        type, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', characterBuffer)
        charDes = clientSkt.recv(charDesLen)
        print('DEBUG: Received CHARACTER message!')
        print('DEBUG: CHARACTER Bytes:', characterBuffer)
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
        
        if (attack+defense+regen > Game.initPoints):
            print('Character\'s stats are higher than initPoints! Assigning valid values')
            attack = 45
            defense = 45
            regen = 5
        
        #Character.sendCharacter()
        sendAccept(10)
        return 0
            

    def sendCharacter(self):
        characterPacked = struct.pack('<B32sB7H%ds' %self.charDesLen, self.type, bytes(self.name, 'utf-8'), self.flags, self.attack, self.defense, self.regen, self.health, self.gold, self.room, len(self.charDes), bytes(self.charDes, 'utf-8'))
        #print('DEBUG: Packed version =', characterPacked)
        
        #characterUnpacked = struct.unpack('<B32sB7H%ds', characterPacked)
        #print('DEBUG: Unpacked version =', characterUnpacked)
        
        clientSkt.sendall(characterPacked)
        #print('DEBUG: CHARACTER sent!')
        
        return 0

def initConnect():
    """
    Executed when a client connects to the server, sends VERSION & GAME message to client, and receives CHARACTER message from client
    """
    version = Version()
    version = version.sendVersion()
    
    #Check that sendVersion() ran successfully
    if (version != 0):
        print('sendVersion() returned invalid code!')
        return 2
    
    game = Game()
    game = game.sendGame()
    
    # Check that sendGame() ran successfully
    if (game != 0):
        print('sendGame() returned invalid code!')
        return 2
    
    character = Character()
    character = character.recvCharacter()
    
    # Check that recvCharacter() ran successfully
    if (character != 0):
        print('ERROR: recvCharacter() returned invalid code!')
        return 2
    
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