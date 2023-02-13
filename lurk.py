'''
CS435 LurkDragon: Module
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
    KNOWN ISSUES
        ROOM: Room Description is appearing as bytes with b'<roomDes>', but Python is saying it's a string? Weird.
'''

# Import socket module, necessary for network communications
import socket
# Import struct module, required for packing/unpacking structures
import struct
# Import threading module, required for multithreading & handling multiple clients
import threading

# Class for handling MESSAGE messages
class Message:
    msgType = int(1)
    def recvMessage(skt, buffer):
        pass
    def sendMessage(skt):
        pass

# Class for handling CHANGEROOM messages
class ChangeRoom:
    msgType = int(2)
    def recvChangeRoom(skt, buffer):
        pass
    def sendChangeRoom(skt):
        pass

# Class for handling FIGHT messages
class Fight:
    msgType = int(3)
    def recvFight(skt, buffer):
        pass
    def sendFight(skt):
        pass

# Class for handling PVPFIGHT messages
class PVPFight:
    msgType = int(4)
    def recvPVPFight(skt, buffer):
        pass
    def sendPVPFight(skt):
        pass

# Class for handling LOOT messages
class Loot:
    msgType = int(5)
    def recvLoot(skt, buffer):
        pass
    def sendLoot(skt):
        pass

# Class for handling START messages
class Start:
    msgType = int(6)
    def recvStart(skt, buffer):
        pass
    def sendStart(skt):
        pass

# Class for handling ERROR messages
class Error:
    msgType = int(7)
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

    # Function for receiving an ERROR message
    def recvError(skt, buffer):
        constBuffer = buffer[:4]
        msgType, errorCode, errMesLen = struct.unpack('<2BH', constBuffer)
        print('DEBUG: Received ERROR message!')
        print('DEBUG: ERROR Bytes:', buffer)
        print('DEBUG: Type:', msgType)
        print('DEBUG: ErrorCode:', errorCode)
        print('DEBUG: ErrMesLen:', errMesLen)
        varBuffer = buffer[4:4+errMesLen]
        errMes, = struct.unpack('<%ds' %errMesLen, varBuffer)
        errMes = errMes.decode('utf-8')
        print('DEBUG: ErrMes:', errMes)

    # Function for sending an ERROR message
    #   skt: Socket to send message to
    #   code: Error code integer to send
    def sendError(skt, code):
        errorCode = int(code)
        errMesLen = len(Error.errorCodes[code])
        errMes = Error.errorCodes[code].encode('utf-8')
        errorPacked = struct.pack('<2BH%ds' %errMesLen, Error.msgType, errorCode, errMesLen, errMes)
        #print('DEBUG: Sending ERROR Message!')
        #print('DEBUG: ERROR Bytes:', errorPacked)
        skt.sendall(errorPacked)
        return 0

# Class for handling ACCEPT messages
class Accept:
    msgType = int(8)

    # Function for receiving an ACCEPT message
    #   skt: Socket to receive message from
    #   buffer: Variable storing bytes to unpack from
    def recvAccept(skt, buffer):
        msgType, message = struct.unpack('<2B', buffer)
        print('DEBUG: Received ACCEPT message!')
        print('DEBUG: ACCEPT Bytes:', buffer)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Message Type Accepted:', message)
        return 0

    # Function for sending an ACCEPT message
    #   skt: Socket to send message to
    #   message: Integer of message type that was accepted
    def sendAccept(skt, message):
        action = int(message)
        acceptPacked = struct.pack('<2B', Accept.msgType, action)
        #print('DEBUG: Sending ACCEPT Message!')
        skt.sendall(acceptPacked)
        #print('DEBUG: ACCEPT Sent:', acceptPacked)
        return 0

# Class for handling ROOM messages
class Room:
    msgType = int(9)
    
    # Dictionary of tuples containing room information
    rooms = {
        0: ('Starting Room', 'This is the starting room, not much to see here.'),
        1: ('Hallway', 'A hallway leading away from the starting room.')
    }

    # Function for receiving a ROOM message
    def recvRoom(skt, buffer):
        constBuffer = buffer[:37]
        msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', constBuffer)
        varBuffer = buffer[37:37+roomDesLen]
        roomDes = struct.unpack('<%ds' %roomDesLen, varBuffer)
        roomDes = ''.join(map(str, roomDes))                    # Convert tuple object to.. bytes? Should convert to string?
        print('DEBUG: Received ROOM message!')
        print('DEBUG: Total ROOM Bytes:', buffer)
        print('DEBUG: Constant ROOM Bytes:', constBuffer)
        print('DEBUG: Variable ROOM Bytes:', varBuffer)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Room Number:', roomNum)
        print('DEBUG: Room Name:', roomName.decode('utf-8'))
        print('DEBUG: Room Description Length:', roomDesLen)
        print('DEBUG: Room Description:', roomDes)              # roomDes is a string, according to type(), but appears to be a bytes object?
        #print('DEBUG: Room Description TYPE:', type(roomDes))
        return roomNum, roomName, roomDesLen, roomDes

    # Function for sending a ROOM message
    def sendRoom(skt, roomNum):
        roomNum = int(roomNum)
        print('DEBUG: Room Number:', roomNum)
        roomName = Room.rooms[roomNum][0]
        print('DEBUG: Room Name:', roomName)
        roomDes = Room.rooms[roomNum][1]
        print('DEBUG: Room Description:', roomDes)
        roomDesLen = len(roomDes)
        
        roomPacked = struct.pack('<BH32sH%ds' %roomDesLen, Room.msgType, roomNum, bytes(roomName, 'utf-8'), roomDesLen, bytes(roomDes, 'utf-8'))
        
        skt.sendall(roomPacked)
        return 0


# Class for handling CHARACTER messages
class Character:
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

    def recvCharacter(skt, buffer):
        constBuffer = buffer[:48]
        msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', constBuffer)
        print('DEBUG: Received CHARACTER message!')
        print('DEBUG: CHARACTER Bytes:', buffer)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Name:', name.decode('utf-8'))
        print('DEBUG: Flags:', flags)
        print('DEBUG: Attack', attack)
        print('DEBUG: Defense:', defense)
        print('DEBUG: Regen:', regen)
        print('DEBUG: Health:', health)
        print('DEBUG: Gold:', gold)
        print('DEBUG: Room', room)
        print('DEBUG: charDesLen:', charDesLen)
        varBuffer = buffer[48:48+charDesLen]
        charDes, = struct.unpack('<%ds' %charDesLen, varBuffer)
        print('DEBUG: charDes:', charDes.decode('utf-8'))
        return name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes

    def sendCharacter(self, skt):
        characterPacked = struct.pack('<B32sB7H%ds' %self.charDesLen, Character.msgType, bytes(self.name, 'utf-8'), self.flags, self.attack, self.defense, self.regen, self.health, self.gold, self.room, len(self.charDes), bytes(self.charDes, 'utf-8'))
        #print('DEBUG: Packed version =', characterPacked)
        
        #characterUnpacked = struct.unpack('<B32sB7H%ds', characterPacked)
        #print('DEBUG: Unpacked version =', characterUnpacked)
        
        skt.sendall(characterPacked)
        #print('DEBUG: CHARACTER sent!')
        
        return 0

# Class for handling GAME messages
class Game:
    msgType = int(11)
    initPoints = int(100)
    statLimit = int(65535)
    gameDes = bytes(str("Logan's Lurk 2.3 server, completely incomplete!"), 'utf-8')
    gameDesLen = int(len(gameDes))

    # Function for receiving a GAME message
    def recvGame(skt, buffer):
        constBuffer = buffer[:7]
        msgType, initPoints, statLimit, gameDesLen = struct.unpack("<B3H", constBuffer)
        varBuffer = buffer[7:7+gameDesLen]
        print('DEBUG: Received GAME message!')
        print('DEBUG: Total GAME Bytes:', buffer)
        print('DEBUG: Constant GAME Bytes:', constBuffer)
        print('DEBUG: Variable GAME Bytes:', varBuffer)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Initial Points:', initPoints)
        print('DEBUG: Stat Limit:', statLimit)
        print('DEBUG: Game Description Length:', gameDesLen)
        print('DEBUG: GAME Description:', varBuffer.decode())
        return 0
    
    # Function for sending a GAME message
    def sendGame(skt):
        gamePacked = struct.pack('<B3H%ds' %Game.gameDesLen, Game.msgType, Game.initPoints, Game.statLimit, Game.gameDesLen, Game.gameDes)
        #print('DEBUG: Packed game =', gamePacked)
        
        #gameUnpacked = struct.unpack('<B3H%ds' %Game.gameDesLen, gamePacked)
        #print('DEBUG: Unpacked game =', gameUnpacked)
        
        skt.sendall(gamePacked)
        #print('DEBUG: GAME sent!')
        
        return 0

# Class for handling LEAVE messages
class Leave:
    msgType = int(12)
    def recvLeave(skt, buffer):
        pass
    def sendLeave(skt):
        pass

# Class for handling CONNECTION messages
class Connection:
    msgType = int(13)
    def recvConnection(skt, buffer):
        pass
    def sendConnection(skt):
        pass

# Class for handling VERSION messages
class Version:
    msgType = int(14)
    major = int(2)
    minor = int(3)
    extSize = int(0)
    
    # Function for receiving a VERSION message
    # Does not currently support receiving list of extensions, so extSize should always = 0
    #   skt: Socket to receive data from
    def recvVersion(skt, buffer):
        msgType, major, minor, extSize = struct.unpack('<3BH', buffer)
        print('DEBUG: Received VERSION message!')
        print('DEBUG: VERSION bytes: ', buffer)
        print('DEBUG: Type: ', msgType)
        print('DEBUG: Major:', major)
        print('DEBUG: Minor', minor)
        print('DEBUG: Ext. Size: ', extSize)
        return 0
    
    # Function for sending a VERSION message
    # Does not currently support sending list of extensions, so extSize should always = 0
    #   skt: Socket to send data to
    def sendVersion(skt):
        # <:    Little endian
        # 3B:   Type, Major, & Minor as uchar (1 byte)
        # H:    extSize as ushort (2 bytes)
        versionPacked = struct.pack('<3BH', Version.msgType, Version.major, Version.minor, Version.extSize)    # Pack VERSION data into variable
        #print('DEBUG: Packed version =', versionPacked)
        
        #versionUnpacked = struct.unpack('<3BH', versionPacked)
        #print('DEBUG: Unpacked version =', versionUnpacked)
        
        skt.sendall(versionPacked)                                                              # Send all packed data to assigned socket
        #print('DEBUG: VERSION sent!')
        
        return 0