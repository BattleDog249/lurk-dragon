# Needs a rewrite with updated refactor!

#!/usr/bin/env python3

# Module required for network communications
import socket
# Module required for packing/unpacking structures
import struct
# Module required for multithreading & handling multiple clients
import threading
import dataclasses

from lurklib import *

MESSAGE = int(1)
CHANGEROOM = int(2)
FIGHT = int(3)
PVPFIGHT = int(4)
LOOT = int(5)
START = int(6)
ERROR = int(7)
ACCEPT = int(8)
ROOM = int(9)
CHARACTER = int(10)
GAME = int(11)
LEAVE = int(12)
CONNECTION = int(13)
VERSION = int(14)

@dataclasses.dataclass
class Client:
    """Class for tracking, finding, adding, and removing clients"""
    clients = {}
    def addClient(skt):
        Client.clients[skt] = skt.fileno()              # Add file descriptor to dictionary for tracking connections
        print('DEBUG: Added Client: ', Client.clients[skt])
    def removeClient(skt):
        print('DEBUG: Removing Client: ', Client.clients[skt])
        Client.clients.pop(skt)
        print('DEBUG: Connected Clients:', Client.clients)
    def getClients():                   # Pull list of all connected clients
        return Client.clients
    def getClient(skt):                 # Pull information on specified client
        return Client.clients[skt]

# Function for sending data in whole, unless a connection error presents itself
def lurkSend(skt, data):
    #print('DEBUG: Start - lurkSend()')
    try:                                                                # Try to send all data over socket
        skt.sendall(data)                                                   # Send all data
        print('LOG: Sent message!')                                         # Print log message
        return 0                                                            # Return status code 0
    except ConnectionError:                                             # Catch a ConnectionError if socket is closed
        print('WARN: Failed to send, ConnectionError!')                     # Print warning message
        if skt in Client.clients:                                           # If client is found in database tracking connected clients
            Client.removeClient(skt)                                            # Remove client from the list
            print('LOG: Removed client from dictionary!')                       # Print log message
            return 1                                                            # Return error code 1
        else:                                                               # If client is not found for whatever reason
            print('ERROR: Connection not found for removal?! Weird...')         # Print error message
            return 2                                                            # Return error code 2

class Message:
    """Class for handling Lurk MESSAGE messages and related functions."""
    msgType = int(1)
    
    def recvMessageConst(data):
        """"""
        messageDataConst = data[0:66]   # Probably needs adjusted, untested
        msgType, msgLen, recvName, sendName, narration = struct.unpack('<BH32s30sH', messageDataConst)
        print('DEBUG: Received MESSAGE message!')
        print('DEBUG: Type:', msgType)
        print('DEBUG: Message Length:', msgLen)
        print('DEBUG: Recipient Name:', recvName)
        print('DEBUG: Sender Name:', sendName)
        print('DEBUG: End of sender Name or narration marker:', narration)
        return msgType, msgLen, recvName, sendName, narration
    
    def recvMessageVar(data, dataLen):
        """"""
        messageDataVar = data[66:66+dataLen]    # 66 might be wrong, untested
        message = struct.unpack('<%ds' %dataLen, messageDataVar)
        print('DEBUG: Message:', message)
        return message
    
    def sendMessage(skt, sender, receiver, message):
        """Return 0 if successfully pack MESSAGE fields into a variable before sending to socket."""
        messagePacked = 0
        return lurkSend(skt, messagePacked)

class ChangeRoom:
    """Class for handling Lurk CHANGEROOM messages and related functions."""
    msgType = int(2)
    
    def recvChangeRoom(data):
        """Return CHANGEROOM message fields from socket after unpacking from buffer."""
        changeRoomData = data[0:3]
        msgType, roomNum = struct.unpack('<BH', changeRoomData)
        print('DEBUG: Received CHANGEROOM message!')
        print('DEBUG: CHANGEROOM bytes:', changeRoomData)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Requested Room:', roomNum)
        return msgType, roomNum
    
    def sendChangeRoom(skt, roomNum):
        """Return 0 if successfully pack CHANGEROOM fields into a variable before sending to socket."""
        changeRoomPacked = struct.pack('<BH', ChangeRoom.msgType, roomNum)
        print('DEBUG: Sending CHANGEROOM message!')
        return lurkSend(skt, changeRoomPacked)

class Fight:
    """Class for handling LurK FIGHT messages and related functions."""
    msgType = int(3)
    
    def recvFight(data):
        """Return FIGHT message fields (not including TYPE) from socket after unpacking from buffer."""
        fightData = data[0:1]   # Untested
        msgType = struct.unpack('<B', fightData)
        print('DEBUG: Received FIGHT message!')
        print('DEBUG: FIGHT bytes:', fightData)
        print('DEBUG: Type:', msgType)
        return msgType
    
    def sendFight(skt):
        """Return 0 if successfully pack FIGHT fields into a variable before sending to socket."""
        fightPacked = struct.pack('<B', Fight.msgType)
        print('DEBUG: Sending FIGHT message!')
        return lurkSend(skt, fightPacked)

class PVPFight:
    """Class for handling Lurk PVPFIGHT messages and related functions."""
    msgType = int(4)
    def recvPVPFight(skt, buffer):
        """Return PVPFIGHT message fields (not including TYPE) from socket after unpacking from buffer."""
        pass
    def sendPVPFight(skt):
        """Return 0 if successfully pack PVPFIGHT fields into a variable before sending to socket."""
        PVPFightPacked = 0
        return lurkSend(skt, PVPFightPacked)

class Loot:
    """Class for handling Lurk LOOT messages and related functions."""
    msgType = int(5)
    def recvLoot(skt, buffer):
        """Return LOOT message fields (not including TYPE) from socket after unpacking from buffer."""
        pass
    def sendLoot(skt):
        """Return 0 if successfully pack LOOT fields into a variable before sending to socket."""
        lootPacked = 0
        return lurkSend(skt, lootPacked)

class Start:
    """Class for handling Lurk START messages and related functions."""
    msgType = int(6)
    def recvStart(skt, data):
        """Return START message field from socket after unpacking from buffer."""
        startData = data[0:1]
        msgType = struct.unpack('<B', data)
        print('DEBUG: Received START message!')
        print('DEBUG: START Bytes:', data)
        print('DEBUG: Type:', msgType)
        return msgType
    def sendStart(skt):
        """Return 0 if successfully pack START fields into a variable before sending to socket."""
        startPacked = struct.pack('<B', Start.msgType)
        #print('DEBUG: Sending START message!')
        #print('DEBUG: START Bytes:', startPacked)
        print('DEBUG: Sending START message!')
        return lurkSend(skt, startPacked)

class Error:
    """Class for handling Lurk ERROR messages and related functions."""
    msgType = int(7)
    errorCodes = {
        0: 'ERROR: This message type is not yet supported!',
        1: 'ERROR: Bad Room! Attempt to change to an inappropriate room.',
        2: 'ERROR: Player Exists. Attempt to create a player that already exists.',
        3: 'ERROR: Bad Monster. Attempt to loot a nonexistent or not present monster.',
        4: 'ERROR: Stat error. Caused by setting inappropriate player stats. Try again!',
        5: 'ERROR: Not Ready. Caused by attempting an action too early, for example changing rooms before sending START or CHARACTER.',
        6: 'ERROR: No target. Sent in response to attempts to loot nonexistent players, fight players in different rooms, etc.',
        7: 'ERROR: No fight. Sent if the requested fight cannot happen for other reasons (i.e. no live monsters in room)',
        8: 'ERROR: No player vs. player combat on the server. Servers do not have to support player-vs-player combat.'
        }

    def recvErrorConst(skt, data):
        """Return constant ERROR message fields from socket after unpacking from buffer."""
        msgType, errCode, errMsgLen = struct.unpack('<2BH', data)
        print('DEBUG: Received ERROR message!')
        print('DEBUG: Type:', msgType)
        print('DEBUG: Error Code:', errCode)
        print('DEBUG: Error Message Length:', errMsgLen)
        return msgType, errCode, errMsgLen
    
    def recvErrorVar(skt, data, dataLen):
        """Return variable ERROR message field from socket after unpacking from buffer."""
        errMsg, = struct.unpack('<%ds' %dataLen, data)
        errMsg = errMsg.decode('utf-8')
        print('DEBUG: Error Message:', errMsg)
        return errMsg
    
    #   skt: Socket to send message to
    #   code: Error code integer to send
    def sendError(skt, code):
        """Return 0 if successfully pack ERROR fields into a variable before sending to socket."""
        errCode = int(code)
        errMsgLen = len(Error.errorCodes[code])
        errMsg = Error.errorCodes[code].encode('utf-8')
        errorPacked = struct.pack('<2BH%ds' %errMsgLen, Error.msgType, errCode, errMsgLen, errMsg)
        #print('DEBUG: ERROR Bytes:', errorPacked)
        print('DEBUG: Sending ERROR message!')
        return lurkSend(skt, errorPacked)

class Accept:
    """Class for handling Lurk ACCEPT messages and related functions."""
    msgType = int(8)

    #   skt: Socket to receive message from
    #   buffer: Variable storing bytes to unpack from
    def recvAccept(skt, data):
        """Return ACCEPT message fields (not including TYPE) from socket after unpacking from buffer."""
        msgType, accept = struct.unpack('<2B', data)
        print('DEBUG: Received ACCEPT message!')
        print('DEBUG: ACCEPT Bytes:', data)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Message Type Accepted:', accept)
        return msgType, accept

    #   skt: Socket to send message to
    #   message: Integer of message type that was accepted
    def sendAccept(skt, message):
        """Return 0 if successfully pack ACCEPT fields into a variable before sending to socket."""
        action = int(message)
        acceptPacked = struct.pack('<2B', Accept.msgType, action)
        print('DEBUG: Sending ACCEPT message!')
        return lurkSend(skt, acceptPacked)

class Room:
    """Class for handling Lurk ROOM messages and related functions."""
    msgType = int(9)
    
    # Dictionary of tuples containing room information
    rooms = {
        0: ('Pine Forest', 'Located deep in the forbidden mountain range, there is surprisingly little to see here beyond towering spruce trees and small game.'),
        1: ('Dark Grove', 'A hallway leading away from the starting room.'),
        2: ('Hidden Valley', 'Seems to be remnants of a ranch here...')
    }
    
    def recvRoomConst(skt, data):
        """"""
        msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', data)
        print('DEBUG: Received ROOM message!')
        print('DEBUG: Type:', msgType)
        print('DEBUG: Room Number:', roomNum)
        print('DEBUG: Room Name:', roomName.decode('utf-8'))
        print('DEBUG: Room Description Length:', roomDesLen)
        return msgType, roomNum, roomName, roomDesLen
    
    def recvRoomVar(skt, data, dataLen):
        """"""
        roomDes = struct.unpack('<%ds' %dataLen, data)
        roomDes = ''.join(map(str, roomDes))                    # Convert tuple object to.. bytes? Should convert to string?
        print('DEBUG: Room Description:', roomDes)              # Appears to still be bytes, rather than a string.. but type() says its a string?
        return roomDes

    def sendRoom(skt, roomNum):
        """Return 0 if successfully pack ROOM fields into a variable before sending to socket."""
        roomNum = int(roomNum)
        print('DEBUG: Room Number:', roomNum)
        roomName = Room.rooms[roomNum][0]
        print('DEBUG: Room Name:', roomName)
        roomDes = Room.rooms[roomNum][1]
        print('DEBUG: Room Description:', roomDes)
        roomDesLen = len(roomDes)
        
        roomPacked = struct.pack('<BH32sH%ds' %roomDesLen, Room.msgType, roomNum, bytes(roomName, 'utf-8'), roomDesLen, bytes(roomDes, 'utf-8'))
        
        print('DEBUG: Sending ROOM message!')
        return lurkSend(skt, roomPacked)

class Character:
    """Class for handling Lurk CHARACTER messages and related functions."""
    msgType = int(10)
    
    characters = {}

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
        
    def getCharacterName():
        pass
    
    # I think this works! Could use some error handling
    def getCharacterRoom(name):
        """Return room number character name resides in"""
        name = Character.characters.get(name)
        print('DEBUG: getting room for character:', name)
        for name in Character.characters:
            try:
                print('DEBUG: Character is in room:', Character.characters[name][7])
                return Character.characters[name][7]
            except:
                pass

    def recvCharacterConst(data):
        """Return constant CHARACTER message fields from socket after unpacking from buffer."""
        msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', data)
        print('DEBUG: Received CHARACTER message!')
        print('DEBUG: Type:', msgType)
        print('DEBUG: Name:', name)
        print('DEBUG: Flags:', flags)
        print('DEBUG: Attack:', attack)
        print('DEBUG: Defense:', defense)
        print('DEBUG: Regen:', regen)
        print('DEBUG: Health:', health)
        print('DEBUG: Gold:', gold)
        print('DEBUG: Current Room:', room)
        print('DEBUG: Description Length:', charDesLen)
        return msgType, name.decode('utf-8'), flags, attack, defense, regen, health, gold, room, charDesLen
    
    def recvCharacterVar(data, dataLen):
        """Return variable CHARACTER message field from socket after unpacking from buffer."""
        charDes, = struct.unpack('<%ds' %dataLen, data)
        charDes = charDes.decode('utf-8')
        print('DEBUG: Character Description:', charDes)
        return charDes

    def sendCharacter(self, skt):
        """Return 0 if successfully pack CHARACTER fields into a variable before sending to socket."""
        characterPacked = struct.pack('<B32sB7H%ds' %self.charDesLen, Character.msgType, bytes(self.name, 'utf-8'), self.flags, self.attack, self.defense, self.regen, self.health, self.gold, self.room, len(self.charDes), bytes(self.charDes, 'utf-8'))
        print('LOG: Sending CHARACTER message!')
        return lurkSend(skt, characterPacked)
class Game:
    """Class for handling Lurk GAME messages and related functions."""
    msgType = int(11)
    initPoints = int(100)
    statLimit = int(65535)
    gameDes = bytes(str("""Can you conquer the beast?
                        
 (                    (                                   
 )\ )               ) )\ )                                
(()/(   (   (    ( /((()/(   (       )  (  (              
 /(_)) ))\  )(   )\())/(_))  )(   ( /(  )\))(  (    (     
(_))  /((_)(()\ ((_)\(_))_  (()\  )(_))((_))\  )\   )\ )  
| |  (_))(  ((_)| |(_)|   \  ((_)((_)_  (()(_)((_) _(_/(  
| |__| || || '_|| / / | |) || '_|/ _` |/ _` |/ _ \| ' \)) 
|____|\_,_||_|  |_\_\ |___/ |_|  \__,_|\__, |\___/|_||_|  
                                       |___/              
"""), 'utf-8')
    gameDesLen = int(len(gameDes))
    
    def recvGameConst(data):
        """Return constant GAME message fields from socket after unpacking from buffer.

        Args:
            data (7 bytes): Bytes data buffer to unpack

        Returns:
            _type_: GAME constant fields
        """
        msgType, initPoints, statLimit, gameDesLen = struct.unpack('<B3H', data)
        print('DEBUG: Received GAME message!')
        print('DEBUG: Type:', msgType)
        print('DEBUG: Initial Points:', initPoints)
        print('DEBUG: Stat Limit:', statLimit)
        print('DEBUG: Game Description Length:', gameDesLen)
        return msgType, initPoints, statLimit, gameDesLen
    
    def recvGameVar(data, dataLen):
        """Return variable GAME message field from socket after unpacking from buffer."""
        gameDes, = struct.unpack('<%ds' %dataLen, data)
        gameDes = gameDes.decode('utf-8')
        print('DEBUG: Game Description:', gameDes)
        return gameDes
    
    def sendGame(skt):
        """Return 0 if successfully pack GAME fields into a variable before sending to socket."""
        gamePacked = struct.pack('<B3H%ds' %Game.gameDesLen, Game.msgType, Game.initPoints, Game.statLimit, Game.gameDesLen, Game.gameDes)
        #print('DEBUG: Packed game =', gamePacked)
        
        #gameUnpacked = struct.unpack('<B3H%ds' %Game.gameDesLen, gamePacked)
        #print('DEBUG: Unpacked game =', gameUnpacked)
        
        print('DEBUG: Sending GAME message!')
        return lurkSend(skt, gamePacked)

class Leave:
    """Class for handling Lurk LEAVE messages and related functions."""
    msgType = int(12)
    
    def recvLeave(skt):
        """Return LEAVE message fields (not including TYPE) from socket after unpacking from buffer."""
        print('DEBUG: Received LEAVE message!')
        print('DEBUG: Closing socket:', skt)
        skt.shutdown(2)
        skt.close()
        return 0
    
    def sendLeave(skt):
        """Return 0 if successfully pack LEAVE fields into a variable before sending to socket."""
        leavePacked = struct.pack('<B', Leave.msgType)
        
        print('DEBUG: Sending LEAVE message!')
        return lurkSend(skt, leavePacked)

class Connection:
    """Class for handling Lurk CONNECTION messages and related functions."""
    msgType = int(13)
    
    connections = {
        Room.rooms[0]: (Room.rooms[1], Room.rooms[2]),
        Room.rooms[1]: (Room.rooms[2]),
        Room.rooms[2]: (Room.rooms[1])
    }
    
    def getConnections(roomNum):
        """Return available connections for room"""
        
        pass
    
    def recvConnection(skt, buffer):
        """Return CONNECTION message fields (not including TYPE) from socket after unpacking from buffer."""
        pass
    
    def sendConnection(skt, roomNum):
        """Return 0 if successfully pack CONNECTION fields into a variable before sending to socket."""
        if (roomNum in Connection.connections):
            #for (roomNum in Connection.connections[])
            connectionPacked = struct.pack('<BH32sH%ds' %Room.rooms[roomNum][1], Connection.msgType, Room.rooms[roomNum], Room.rooms[roomNum][0], len(Room.rooms[roomNum][1]), Room.rooms[roomNum][1])
            print('DEBUG: Sending CONNECTION message!')
            return lurkSend(skt, connectionPacked)

class Version:
    """Class for handling Lurk VERSION messages and related functions."""
    msgType = int(14)
    major = int(2)
    minor = int(3)
    extSize = int(0)
    
    # Does not currently support receiving list of extensions, so extSize should always = 0
    #   data: Buffer of data to unpack
    def recvVersion(data):
        """Return VERSION message fields (not including TYPE) from socket after unpacking from buffer."""
        versionData = data[0:5]                                                 # Ensure data is correct size
        msgType, major, minor, extSize = struct.unpack('<3BH', versionData)
        print('DEBUG: Received VERSION message!')
        print('DEBUG: VERSION bytes: ', versionData)
        print('DEBUG: Type: ', msgType)
        print('DEBUG: Major:', major)
        print('DEBUG: Minor', minor)
        print('DEBUG: Ext. Size: ', extSize)
        return msgType, major, minor, extSize
    
    # Does not currently support sending list of extensions, so extSize should always = 0
    #   skt: Socket to send data to
    def sendVersion(skt):
        """Return 0 if successfully pack VERSION fields into a variable before sending to socket."""
        versionPacked = struct.pack('<3BH', Version.msgType, Version.major, Version.minor, Version.extSize)
        
        print('DEBUG: Sending VERSION message!')
        return lurkSend(skt, versionPacked)