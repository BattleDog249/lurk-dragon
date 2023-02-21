#   CS435 LurkDragon: Module
#       Author: Logan Hunter Gray
#       Email: lhgray@lcmail.lcsc.edu
#       KNOWN ISSUES
#           ROOM: Room Description is appearing as bytes with b'<roomDes>', but Python is saying it's a string? Weird.

#!/usr/bin/env python3

# Module required for network communications
import socket
# Module required for packing/unpacking structures
import struct
# Module required for multithreading & handling multiple clients
import threading
import dataclasses

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

def lurkRecv(skt):
    try:
        buffer = skt.recv(4096)
        return buffer
    except ConnectionError:                                             # Catch a ConnectionError if socket is closed
        print('WARN: Failed to receive, ConnectionError!')                  # Print warning message
        if skt in Client.clients:                                           # If client is found in database tracking connected clients
            Client.removeClient(skt)                                            # Remove client from the list
            print('LOG: Removed client from dictionary!')                       # Print log message
            return 1                                                            # Return error code 1
        else:                                                               # If client is not found for whatever reason
            print('ERROR: Connection not found for removal?! Weird...')         # Print error message
            return 2                                                            # Return error code 2

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
    def recvMessage(skt, buffer):
        """Return MESSAGE message fields (not including TYPE) from socket after unpacking from buffer."""
        pass
    def sendMessage(skt):
        """Return 0 if successfully pack MESSAGE fields into a variable before sending to socket."""
        messagePacked = 0
        return lurkSend(skt, messagePacked)

class ChangeRoom:
    """Class for handling Lurk CHANGEROOM messages and related functions."""
    msgType = int(2)
    def recvChangeRoom(skt, buffer):
        """Return CHANGEROOM message fields (not including TYPE) from socket after unpacking from buffer."""
        pass
    def sendChangeRoom(skt):
        """Return 0 if successfully pack CHANGEROOM fields into a variable before sending to socket."""
        changeRoomPacked = 0
        return lurkSend(skt, changeRoomPacked)

class Fight:
    """Class for handling LurK FIGHT messages and related functions."""
    msgType = int(3)
    def recvFight(skt, buffer):
        """Return FIGHT message fields (not including TYPE) from socket after unpacking from buffer."""
        pass
    def sendFight(skt):
        """Return 0 if successfully pack FIGHT fields into a variable before sending to socket."""
        fightPacked = 0
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
        """Return START message fields (not including TYPE) from socket after unpacking from buffer."""
        msgType = struct.unpack('<B', data)
        print('DEBUG: Received START message!')
        print('DEBUG: START Bytes:', data)
        print('DEBUG: Type:', msgType)
        return 0
    def sendStart(skt):
        """Return 0 if successfully pack START fields into a variable before sending to socket."""
        startPacked = struct.pack('<B', Start.msgType)
        #print('DEBUG: Sending START message!')
        #print('DEBUG: START Bytes:', startPacked)
        
        #print('DEBUG: Sending START message!')
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
        return msgType, errCode, errMsgLen
    
    def recvErrorVar(skt, data, dataLen):
        """Return variable ERROR message field from socket after unpacking from buffer."""
        buffer = data[4:4+dataLen]
        errMsg, = struct.unpack('<%ds' %dataLen, data)
        errMsg = errMsg.decode('utf-8')
        return errMsg

    def recvError(skt, data):
        """Return all fields in ERROR message received"""
        msgType, errCode, errMsgLen = Error.recvErrorConst(skt, data)
        errMsg = Error.recvErrorVar(skt, data, errMsgLen)
        print('DEBUG: Received ERROR message!')
        print('DEBUG: ERROR Bytes:', data)
        print('DEBUG: Type:', msgType)
        print('DEBUG: ErrorCode:', errCode)
        print('DEBUG: ErrMesLen:', errMsgLen)
        print('DEBUG: ErrMsg:', errMsg)
        return msgType, errCode, errMsgLen, errMsg

    #   skt: Socket to send message to
    #   code: Error code integer to send
    def sendError(skt, code):
        """Return 0 if successfully pack ERROR fields into a variable before sending to socket."""
        errCode = int(code)
        errMsgLen = len(Error.errorCodes[code])
        errMsg = Error.errorCodes[code].encode('utf-8')
        errorPacked = struct.pack('<2BH%ds' %errMsgLen, Error.msgType, errCode, errMsgLen, errMsg)
        #print('DEBUG: Sending ERROR Message!')
        #print('DEBUG: ERROR Bytes:', errorPacked)
        
        #print('DEBUG: Sending ERROR message!')
        return lurkSend(skt, errorPacked)

class Accept:
    """Class for handling Lurk ACCEPT messages and related functions."""
    msgType = int(8)

    #   skt: Socket to receive message from
    #   buffer: Variable storing bytes to unpack from
    def recvAccept(skt, buffer):
        """Return ACCEPT message fields (not including TYPE) from socket after unpacking from buffer."""
        acceptBuffer = buffer[:2]
        msgType, message = struct.unpack('<2B', acceptBuffer)
        print('DEBUG: Received ACCEPT message!')
        print('DEBUG: ACCEPT Bytes:', buffer)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Message Type Accepted:', message)
        return 0

    #   skt: Socket to send message to
    #   message: Integer of message type that was accepted
    def sendAccept(skt, message):
        """Return 0 if successfully pack ACCEPT fields into a variable before sending to socket."""
        action = int(message)
        acceptPacked = struct.pack('<2B', Accept.msgType, action)
        
        return lurkSend(skt, acceptPacked)

class Room:
    """Class for handling Lurk ROOM messages and related functions."""
    msgType = int(9)
    
    # Dictionary of tuples containing room information
    rooms = {
        0: ('Pine Forest', 'Located deep in the forbidden mountain range, there is surprisingly little to see here beyond towering spruce trees and small game.'),
        1: ('Dark Grove', 'A hallway leading away from the starting room.'),
        3: ('Hidden Valley', 'Seems to be remnants of a ranch here...')
    }

    def recvRoomConst(skt, data):
        """"""
        buffer = data[:37]
        msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', buffer)
        return msgType, roomNum, roomName, roomDesLen
    
    def recvRoomVar(skt, data, dataLen):
        """"""
        buffer = data[37:37+dataLen]
        roomDes = struct.unpack('<%ds' %dataLen, buffer)
        roomDes = ''.join(map(str, roomDes))                    # Convert tuple object to.. bytes? Should convert to string?
        return roomDes
    
    def recvRoom(skt, buffer):
        """Return all ROOM message fields received."""
        msgType, roomNum, roomName, roomDesLen = Room.recvRoomConst(skt, buffer)
        roomDes = Room.recvRoomVar(skt, buffer, roomDesLen)
        print('DEBUG: Received ROOM message!')
        print('DEBUG: ROOM Bytes:', buffer)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Room Number:', roomNum)
        print('DEBUG: Room Name:', roomName.decode('utf-8'))
        print('DEBUG: Room Description Length:', roomDesLen)
        print('DEBUG: Room Description:', roomDes)              # roomDes is a string, according to type(), but appears to be a bytes object?
        return roomNum, roomName, roomDesLen, roomDes

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
        
        #print('DEBUG: Sending ROOM message!')
        return lurkSend(skt, roomPacked)

class Character:
    """Class for handling Lurk CHARACTER messages and related functions."""
    msgType = int(10)

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

    def recvCharacterConst(skt, data):
        """Return constant CHARACTER message fields from socket after unpacking from buffer."""
        msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', data)
        return msgType, name.decode('utf-8'), flags, attack, defense, regen, health, gold, room, charDesLen
    
    def recvCharacterVar(skt, data, dataLen):
        """Return variable CHARACTER message field from socket after unpacking from buffer."""
        charDes, = struct.unpack('<%ds' %dataLen, data)
        charDes = charDes.decode('utf-8')
        return charDes
    
    def recvCharacter(skt, data):
        """Return all fields in CHARACTER message received."""
        msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = Character.recvCharacterConst(skt, data)
        charDes = Character.recvCharacterVar(skt, data, charDesLen)
        print('DEBUG: Received CHARACTER message!')
        print('DEBUG: CHARACTER Bytes:', data)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Name:', name)
        print('DEBUG: Flags:', flags)
        print('DEBUG: Attack', attack)
        print('DEBUG: Defense:', defense)
        print('DEBUG: Regen:', regen)
        print('DEBUG: Health:', health)
        print('DEBUG: Gold:', gold)
        print('DEBUG: Room', room)
        print('DEBUG: charDesLen:', charDesLen)
        print('DEBUG: charDes:', charDes)
        return msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes

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
    
    def recvGameConst(skt, data):
        """Return constant GAME message fields from socket after unpacking from buffer."""
        buffer = data[:7]
        msgType, initPoints, statLimit, gameDesLen = struct.unpack('<B3H', buffer)
        return msgType, initPoints, statLimit, gameDesLen
    
    def recvGameVar(skt, data, dataLen):
        """Return variable GAME message field from socket after unpacking from buffer."""
        buffer = data[7:7+dataLen]
        gameDes, = struct.unpack('<%ds' %dataLen, buffer)
        gameDes = gameDes.decode('utf-8')
        return gameDes
    
    def recvGame(skt, data):
        """Return all fields in GAME message received."""
        msgType, initPoints, statLimit, gameDesLen = Game.recvGameConst(skt, data)
        gameDes = Game.recvGameVar(skt, data, gameDesLen)
        print('DEBUG: Received GAME message!')
        print('DEBUG: GAME Bytes:', data)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Initial Points:', initPoints)
        print('DEBUG: Stat Limit:', statLimit)
        print('DEBUG: Game Description Length:', gameDesLen)
        print('DEBUG: GAME Description:', gameDes)
        return msgType, initPoints, statLimit, gameDesLen, gameDes

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
    def recvConnection(skt, buffer):
        """Return CONNECTION message fields (not including TYPE) from socket after unpacking from buffer."""
        pass
    def sendConnection(skt):
        """Return 0 if successfully pack CONNECTION fields into a variable before sending to socket."""
        connectionPacked = 0
        
        print('DEBUG: Sending CONNECTION message!')
        return lurkSend(skt, connectionPacked)

class Version:
    """Class for handling Lurk VERSION messages and related functions."""
    msgType = int(14)
    major = int(2)
    minor = int(3)
    extSize = int(0)
    
    # Does not currently support receiving list of extensions, so extSize should always = 0
    #   skt: Socket to receive data from
    def recvVersion(skt, buffer):
        """Return VERSION message fields (not including TYPE) from socket after unpacking from buffer."""
        msgType, major, minor, extSize = struct.unpack('<3BH', buffer)
        print('DEBUG: Received VERSION message!')
        print('DEBUG: VERSION bytes: ', buffer)
        print('DEBUG: Type: ', msgType)
        print('DEBUG: Major:', major)
        print('DEBUG: Minor', minor)
        print('DEBUG: Ext. Size: ', extSize)
        return major, minor, extSize
    
    # Does not currently support sending list of extensions, so extSize should always = 0
    #   skt: Socket to send data to
    def sendVersion(skt):
        """Return 0 if successfully pack VERSION fields into a variable before sending to socket."""
        versionPacked = struct.pack('<3BH', Version.msgType, Version.major, Version.minor, Version.extSize)
        
        print('DEBUG: Sending VERSION message!')
        return lurkSend(skt, versionPacked)