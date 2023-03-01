# Potential Bug: Check on unpack descriptions, des, = vs des =
# In messages 1 byte big, like START, may have to use startData = bytes(data[0:1]) vs. startData = data[0:1]
    # May not need to unpack because its only 1 integer?

#!/usr/bin/env python3

import socket
import struct

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

def lurkSend(skt, data):
    try:
        skt.sendall(data)
        print('DEBUG: lurkSend() sent data!')
        return 0
    except ConnectionError:
        print('WARN: ConnectionError, lurkSend() returning False!')
        return 1

def lurkRecv(skt):
    """Waits to receive binary data from socket, and handles potential ConnectionErrors.

    Args:
        skt (Socket): Socket file descriptor to receive from.

    Returns:
        Binary: Data read from socket.
    """
    data = bytearray(b'')
    while True:
            if (data == b''):
                try:
                    data = skt.recv(1024)
                except ConnectionError or OSError:
                    print('WARN: ConnectionError or OSError, lurkRecv() returning None!')
                    return None
            elif (data == None):
                print('DEBUG: Client disconnected, or just a lurkscan message.')
                return None
            elif (data != b''):
                print('DEBUG: lurkRecv() received data!')
                return data
        
def lurkRead(data):
    """Returns unpacked lurk messages

    Args:
        data (bytes): Binary data following the LURK protocol

    Returns:
        Any: All values of unpacked LURK message as integers, strings, etc.
        None: If passed an unsupported message type, or if nessage type is of unexpected size
    """
    print('DEBUG: Data passed to lurkRead():', data)
    if (data[0] == MESSAGE):
        print('DEBUG: Reading MESSAGE message!')
        messageDataConst = data[0:67]
        try:
            msgType, msgLen, recvName, sendName, narration = struct.unpack('<BH32s30sH', messageDataConst)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack constant MESSAGE data!')
            return None
        print('DEBUG: Type:', msgType)
        print('DEBUG: Message Length:', msgLen)
        print('DEBUG: Recipient Name:', recvName)
        print('DEBUG: Sender Name:', sendName)
        print('DEBUG: End of sender Name or narration marker:', narration)
        messageDataVar = data[67:67+msgLen]
        try:
            message = struct.unpack('<%ds' %msgLen, messageDataVar)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack variable MESSAGE data!')
            return None
        print('DEBUG: Message:', message)
        return msgType, msgLen, recvName, sendName, narration, message
    
    elif (data[0] == CHANGEROOM):
        print('DEBUG: Reading CHANGEROOM message!')
        changeRoomData = data[0:3]
        try:
            msgType, desiredRoomNum = struct.unpack('<BH', changeRoomData)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack CHANGEROOM data!')
            return None
        return msgType, desiredRoomNum
    
    elif (data[0] == FIGHT):
        print('DEBUG: Reading FIGHT message!')
        fightData = data[0:1]
        try:
            msgType = struct.unpack('<B', fightData)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack FIGHT data!')
            return None
        return msgType
    
    elif (data[0] == PVPFIGHT):
        print('DEBUG: Reading PVPFIGHT message!')
        pvpFightData = data[0:33]
        try:
            msgType, targetName = struct.unpack('<B32s', pvpFightData)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack PVPFIGHT data!')
            return None
        return msgType, targetName
    
    elif (data[0] == LOOT):
        print('DEBUG: Reading LOOT message!')
        lootData = data[0:33]
        try:
            msgType, targetName = struct.unpack('<B32s', lootData)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack LOOT data!')
            return None
        return msgType, targetName
    
    elif (data[0] == START):
        print('DEBUG: Reading START message!')
        startData = data[0:1]
        try:
            msgType = struct.unpack('<B', startData)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack START data!')
            return None
        return msgType
    
    elif (data[0] == ERROR):
        print('DEBUG: Reading ERROR message!')
        errorDataConst = data[0:4]
        try:
            msgType, errCode, errMsgLen = struct.unpack('<2BH', errorDataConst)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack constant ERROR data!')
            return None
        errorDataVar = data[4:4+errMsgLen]
        try:
            errMsg = struct.unpack('<%ds' %errMsgLen, errorDataVar)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack variable ERROR data!')
            return None
        return msgType, errCode, errMsgLen, errMsg
    
    elif (data[0] == ACCEPT):
        print('DEBUG: Reading ACCEPT message!')
        acceptData = data[0:2]
        try:
            msgType, acceptedMsg = struct.unpack('<2B', acceptData)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack ACCEPT data!')
            return None
        return msgType, acceptedMsg
    
    elif (data[0] == ROOM):
        print('DEBUG: Reading ROOM message!')
        roomDataConst = data[0:37]
        try:
            msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', roomDataConst)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack constant ROOM data!')
            return None
        roomDataVar = data[37:37+roomDesLen]
        try:
            roomDes = struct.unpack('<%ds' %roomDesLen, roomDataVar)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack variable ROOM data!')
            return None
        return msgType, roomNum, roomName, roomDesLen, roomDes
    
    elif (data[0] == CHARACTER):
        print('DEBUG: Reading CHARACTER message!')
        characterDataConst = data[0:48]
        try:
            msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', characterDataConst)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack constant CHARACTER data!')
            return None
        characterDataVar = data[48:48+charDesLen]
        try:
            charDes, = struct.unpack('<%ds' %charDesLen, characterDataVar)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack variable CHARACTER data!')
            return None
        charDes = charDes.decode('utf-8')
        return msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes
    
    elif (data[0] == GAME):
        print('DEBUG: Reading GAME message!')
        gameDataConst = data[0:7]
        try:
            msgType, initPoints, statLimit, gameDesLen = struct.unpack('<B3H', gameDataConst)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack constant GAME data!')
            return None
        gameDataVar = data[7:7+gameDesLen]
        try:
            gameDes = struct.unpack('<%ds' %gameDesLen, gameDataVar)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack variable GAME data!')
            return None
        return msgType, initPoints, statLimit, gameDesLen, gameDes
    
    elif (data[0] == LEAVE):
        print('DEBUG: Reading LEAVE message!')
        leaveData = data[0:1]
        try:
            msgType = struct.unpack('<B', leaveData)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack LEAVE data!')
            return None
        return msgType
    
    elif (data[0] == CONNECTION):
        print('DEBUG: Reading CONNECTION message!')
        connectionDataConst = data[0:37]
        try:
            msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', connectionDataConst)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack constant CONNECTION data!')
            return None
        connectionDataVar = data[37:37+roomDesLen]
        try:
            roomDes = struct.unpack('<%ds' %roomDesLen, connectionDataVar)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack variable CONNECTION data!')
            return None
        return msgType, roomNum, roomName, roomDesLen, roomDes
    
    elif (data[0] == VERSION):
        print('DEBUG: Reading VERSION message!')
        versionData = data[0:5]
        try:
            msgType, major, minor, extSize = struct.unpack('<3BH', versionData)
        except struct.error:
            print('ERROR: lurkRead() failed to unpack VERSION data!')
            return None
        return msgType, major, minor, extSize
    
    else:
        print('ERROR: lurkRead() was passed an invalid message type, returning None!')
        return None