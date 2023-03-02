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
    messages = []
    data = bytearray(b'')
    try:
        data = skt.recv(1024)
        if data == b'':     # If recv returns null, client disconnected. This fixes LurkScan!
            return None
    except socket.error or ConnectionError or OSError:
        return None
    
    print('DEBUG: Received binary data:', data)
    for i in data:                                                                               # This part is broken I believe
        print('DEBUG: i:', i)
        lurkMsgType = i
        '''
        try:                                                                                        # Check if byte could be a valid message type
            lurkMsgType = int.from_bytes(data[i], 'little')
            print('DEBUG: lurkMsgType:', lurkMsgType)
            if (lurkMsgType < 1 or lurkMsgType > 14):
                print('ERROR: data: {}({})'.format(type(data), data))
                continue
        except:
            # Value fails to convert into an integer, keep looking for potential lurk message types
            print('Value fails to convert into an integer, keep looking for potential lurk message types')
            continue
        '''
        if (lurkMsgType < 1 or lurkMsgType > 14):
                print('ERROR: Message not a valid lurk type')
                continue
        
        if (lurkMsgType == MESSAGE):
            print('DEBUG: Is it a MESSAGE message?')
            messageHeaderLen = i + 67
            messageHeader = data[i:messageHeaderLen]
            try:
                msgType, msgLen, recvName, sendName, narration = struct.unpack('<BH32s30sH', messageHeader)
            except struct.error:
                # If lurkMsgType is a valid int, but not a valid lurk message in its entirety, continue looking for next lurk msg type
                print('ERROR: Failed to unpack constant MESSAGE data!')
                continue
            print('DEBUG: Type:', msgType)
            print('DEBUG: Message Length:', msgLen)
            print('DEBUG: Recipient Name:', recvName)
            print('DEBUG: Sender Name:', sendName)
            print('DEBUG: End of sender Name or narration marker:', narration)
            messageData = data[messageHeaderLen:messageHeaderLen+msgLen]
            try:
                message = struct.unpack('<%ds' %msgLen, messageData)
            except struct.error:
                print('ERROR: Failed to unpack variable MESSAGE data!')
                continue
            print('DEBUG: Message:', message)
            
            # Pack values in a dictioanry with Key = Msg type, value = msg data as tuple
            # Now check if there is more data to unpack; if not, return dictionary containing single received message
            # If there is, add message to dictionary, and continue at end of message looking for another valid lurk msg type until at end of data buffer
            
            messages.append((msgType, msgLen, recvName, sendName, narration, message))
            
            if (len(data[messageHeaderLen+msgLen:]) != 0):           # If we are not at the end of the data buffer received, more potential messages to interpret, continue
                continue
            
            return messages
        
        elif (lurkMsgType == CHANGEROOM):
            print('DEBUG: Is it a CHANGEROOM message?')
            changeroomHeaderLen = i + 3
            changeroomHeader = data[i:changeroomHeaderLen]
            try:
                msgType, desiredRoomNum = struct.unpack('<BH', changeroomHeader)
            except struct.error:
                print('ERROR: Failed to unpack CHANGEROOM data!')
                continue
            print('DEBUG: Type:', msgType)
            print('DEBUG: desiredRoomNum:', desiredRoomNum)
            
            messages.append((msgType, desiredRoomNum))
            
            if (len(data[changeroomHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == FIGHT):
            print('DEBUG: Is it a FIGHT message?')
            fightHeaderLen = i + 1
            fightHeader = data[i:fightHeaderLen]
            try:
                msgType = struct.unpack('<B', fightHeader)
            except struct.error:
                print('ERROR: Failed to unpack FIGHT data!')
                continue
            
            messages.append((msgType,))
            
            if (len(data[fightHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == PVPFIGHT):
            print('DEBUG: Is it a PVPFIGHT message?')
            pvpfightHeaderLen = i + 33
            pvpfightHeader = data[i:pvpfightHeaderLen]
            try:
                msgType, targetName = struct.unpack('<B32s', pvpfightHeader)
            except struct.error:
                print('ERROR: Failed to unpack PVPFIGHT data!')
                continue
            
            messages.append((msgType, targetName))
            
            if (len(data[pvpfightHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == LOOT):
            print('DEBUG: Is it a LOOT message?')
            lootHeaderLen = i + 33
            lootHeader = data[i:lootHeaderLen]
            try:
                msgType, targetName = struct.unpack('<B32s', lootHeader)
            except struct.error:
                print('ERROR: Failed to unpack LOOT data!')
                continue
            
            messages.append((msgType, targetName))
            
            if (len(data[lootHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == START):
            print('DEBUG: Is it a START message?')
            startHeaderLen = i + 1
            startHeader = data[i:startHeaderLen]
            try:
                msgType = struct.unpack('<B', startHeader)
            except struct.error:
                print('ERROR: Failed to unpack START data!')
                continue
            
            messages.append((msgType,))
            
            if (len(data[startHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == ERROR):
            print('DEBUG: Is it an ERROR message?')
            errorHeaderLen = i + 4
            errorHeader = data[i:errorHeaderLen]
            try:
                msgType, errCode, errMsgLen = struct.unpack('<2BH', errorHeader)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack constant ERROR data!')
                continue
            errorData = data[errorHeaderLen:errorHeaderLen+errMsgLen]
            try:
                errMsg = struct.unpack('<%ds' %errMsgLen, errorData)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack variable ERROR data!')
                continue
            
            messages.append((msgType, errCode, errMsgLen))
            
            if (len(data[errorHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == ACCEPT):
            print('DEBUG: Is it an ACCEPT message?')
            acceptHeaderLen = i + 2
            acceptHeader = data[i:acceptHeaderLen]
            try:
                msgType, acceptedMsg = struct.unpack('<2B', acceptHeader)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack ACCEPT data!')
                continue
            
            messages.append((msgType, acceptedMsg))
            
            if (len(data[acceptHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == ROOM):
            print('DEBUG: Is it a ROOM message?')
            roomHeaderLen = i + 37
            roomHeader = data[i:roomHeaderLen]
            try:
                msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', roomHeader)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack constant ROOM data!')
                continue
            roomData = data[roomHeaderLen:roomHeaderLen+roomDesLen]
            try:
                roomDes = struct.unpack('<%ds' %roomDesLen, roomData)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack variable ROOM data!')
                continue
            
            messages.append((msgType, roomNum, roomName, roomDesLen, roomDes))
            
            if (len(data[roomHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == CHARACTER):
            print('DEBUG: Is it a CHARACTER message?')
            characterHeaderLen = i + 48
            print('DEBUG: characterHeaderLen:', characterHeaderLen)
            characterHeader = data[i:characterHeaderLen]
            print('DEBUG: characterHeader:', characterHeader)
            try:
                msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', characterHeader)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack constant CHARACTER data!')
                continue
            characterData = data[characterHeaderLen:characterHeaderLen+charDesLen]
            print('DEBUG: characterData:', characterData)
            try:
                charDes, = struct.unpack('<%ds' %charDesLen, characterData)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack variable CHARACTER data!')
                continue
            charDes = charDes.decode('utf-8')
            
            messages.append((msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes))
            
            if (len(data[characterHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == GAME):
            print('DEBUG: Is it a GAME message?')
            gameHeaderLen = i + 7
            gameHeader = data[i:gameHeaderLen]
            try:
                msgType, initPoints, statLimit, gameDesLen = struct.unpack('<B3H', gameHeader)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack constant GAME data!')
                continue
            gameData = data[gameHeaderLen:gameHeaderLen+gameDesLen]
            try:
                gameDes = struct.unpack('<%ds' %gameDesLen, gameData)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack variable GAME data!')
                continue
            
            messages.append((msgType, initPoints, statLimit, gameDesLen, gameDes))
            
            if (len(data[gameHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (lurkMsgType == LEAVE):
            print('DEBUG: Is it a LEAVE message?')
            leaveHeaderLen = i + 1
            leaveHeader = data[i:leaveHeaderLen]
            try:
                msgType = struct.unpack('<B', leaveHeader)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack LEAVE data!')
                continue
            
            messages.append((msgType,))

            return messages
        
        elif (data[0] == CONNECTION):
            print('DEBUG: Is it a CONNECTION message?')
            connectionHeaderLen = i + 37
            connectionHeader = data[i:connectionHeaderLen]
            try:
                msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', connectionHeader)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack constant CONNECTION data!')
                continue
            connectionDataVar = data[37:37+roomDesLen]
            try:
                roomDes = struct.unpack('<%ds' %roomDesLen, connectionDataVar)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack variable CONNECTION data!')
                continue
            
            messages.append((msgType, roomNum, roomName, roomDesLen, roomDes))
            
            if (len(data[connectionHeaderLen:]) != 0):
                continue
            
            return messages
        
        elif (data[0] == VERSION):
            print('DEBUG: Is it a VERSION message?')
            versionHeaderLen = i + 5
            versionHeader = data[i:versionHeaderLen]
            try:
                msgType, major, minor, extSize = struct.unpack('<3BH', versionHeader)
            except struct.error:
                print('ERROR: lurkRead() failed to unpack VERSION data!')
                continue
            messages.append((msgType, major, minor, extSize))
            if (len(data[versionHeaderLen:]) != 0):
                continue
            return messages
        
        else:
            print('ERROR: lurkRecv() was passed an invalid message type somehow, returning None!')
            return None