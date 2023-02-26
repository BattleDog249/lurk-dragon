# Potential Bug: Check on unpack descriptions, des, = vs des =
# In messages 1 byte big, like START, may have to use startData = bytes(data[0:1]) vs. startData = data[0:1]
    # May not need to unpack because its only 1 integer?

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
        return False

def lurkRecv(skt):
    data = bytearray(b'')
    while True:
            if (data == b''):
                try:
                    data = skt.recv(4096)
                except ConnectionError:
                    print('WARN: ConnectionError, lurkRecv() returning False!')
                    return False
            elif (data != b''):
                print('DEBUG: lurkRecv() received data!')
                return data
        
def lurkRead(data):
    """Returns whole lurk message entered as parameter"""
    print('DEBUG: Data passed to lurkRead():', data)
    if (data[0] == MESSAGE):
        print('DEBUG: Reading MESSAGE message!')
        messageDataConst = data[0:67]
        msgType, msgLen, recvName, sendName, narration = struct.unpack('<BH32s30sH', messageDataConst)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Message Length:', msgLen)
        print('DEBUG: Recipient Name:', recvName)
        print('DEBUG: Sender Name:', sendName)
        print('DEBUG: End of sender Name or narration marker:', narration)
        messageDataVar = data[67:67+msgLen]
        message = struct.unpack('<%ds' %msgLen, messageDataVar)
        print('DEBUG: Message:', message)
        return msgType, msgLen, recvName, sendName, narration, message
    
    elif (data[0] == CHANGEROOM):
        print('DEBUG: Reading CHANGEROOM message!')
        changeRoomData = data[0:3]
        msgType, desiredRoomNum = struct.unpack('<BH', changeRoomData)
        print('DEBUG: Type:', msgType)
        print('DEBUG: Requested Room:', desiredRoomNum)
        return msgType, desiredRoomNum
    
    elif (data[0] == FIGHT):
        print('DEBUG: Reading FIGHT message!')
        fightData = data[0:1]
        msgType = struct.unpack('<B', fightData)
        print('DEBUG: Type:', msgType)
        return msgType
    
    elif (data[0] == PVPFIGHT):
        print('DEBUG: Reading PVPFIGHT message!')
        pvpFightData = data[0:33]
        msgType, targetName = struct.unpack('<B32s', pvpFightData)
        return msgType, targetName
    
    elif (data[0] == LOOT):
        print('DEBUG: Reading LOOT message!')
        lootData = data[0:33]
        msgType, targetName = struct.unpack('<B32s', lootData)
        return msgType, targetName
    
    elif (data[0] == START):
        print('DEBUG: Reading START message!')
        startData = data[0:1]
        msgType = struct.unpack('<B', startData)
        return msgType
    
    elif (data[0] == ERROR):
        print('DEBUG: Reading ERROR message!')
        errorDataConst = data[0:4]
        msgType, errCode, errMsgLen = struct.unpack('<2BH', errorDataConst)
        errorDataVar = data[4:4+errMsgLen]
        errMsg = struct.unpack('<%ds' %errMsgLen, errorDataVar)
        return msgType, errCode, errMsgLen, errMsg
    
    elif (data[0] == ACCEPT):
        print('DEBUG: Reading ACCEPT message!')
        acceptData = data[0:2]
        msgType, acceptedMsg = struct.unpack('<2B', acceptData)
        return msgType, acceptedMsg
    
    elif (data[0] == ROOM):
        print('DEBUG: Reading ROOM message!')
        roomDataConst = data[0:37]
        msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', roomDataConst)
        roomDataVar = data[37:37+roomDesLen]
        roomDes = struct.unpack('<%ds' %roomDesLen, roomDataVar)
        return msgType, roomNum, roomName, roomDesLen, roomDes
    
    elif (data[0] == CHARACTER):
        print('DEBUG: Reading CHARACTER message!')
        characterDataConst = data[0:48]
        msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', characterDataConst)
        characterDataVar = data[48:48+charDesLen]
        charDes, = struct.unpack('<%ds' %charDesLen, characterDataVar)
        charDes = charDes.decode('utf-8')
        return msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes
    
    elif (data[0] == GAME):
        print('DEBUG: Reading GAME message!')
        gameDataConst = data[0:7]
        msgType, initPoints, statLimit, gameDesLen = struct.unpack('<B3H', gameDataConst)
        gameDataVar = data[7:7+gameDesLen]
        gameDes = struct.unpack('<%ds' %gameDesLen, gameDataVar)
        return msgType, initPoints, statLimit, gameDesLen, gameDes
    
    elif (data[0] == LEAVE):
        print('DEBUG: Reading LEAVE message!')
        leaveData = data[0:1]
        msgType = struct.unpack('<B', leaveData)
        return msgType
    
    elif (data[0] == CONNECTION):
        print('DEBUG: Reading CONNECTION message!')
        connectionDataConst = data[0:37]
        msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', connectionDataConst)
        connectionDataVar = data[37:37+roomDesLen]
        roomDes = struct.unpack('<%ds' %roomDesLen, connectionDataVar)
        return msgType, roomNum, roomName, roomDesLen, roomDes
    
    elif (data[0] == VERSION):
        print('DEBUG: Reading VERSION message!')
        versionData = data[0:5]
        msgType, major, minor, extSize = struct.unpack('<3BH', versionData)
        return msgType, major, minor, extSize
    
    else:
        print('ERROR: Invalid message type passed to lurkRead(), returning None!')
        return None