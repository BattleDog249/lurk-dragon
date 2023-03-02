#!/usr/bin/env python3

from clientlib import *

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining host address & port of server to connect to
host = 'localhost'
port = 5010

# Connect to server with assigned host & port
skt.connect((host, port))
print('DEBUG: Connecting to server:', host)

characterDescription = "This is a collision test dummy, it is not sentient!"
character1 = Character("Test Dummy #1", 0x4, 25, 25, 50, 20, 100, 40, len(characterDescription), characterDescription)
character1 = Character.sendCharacter(character1, skt)
character2 = Character("Test Dummy #2", 0x4, 25, 25, 100, 20, 100, 40, len(characterDescription), characterDescription)
character2 = Character.sendCharacter(character2, skt)

while True:
    data = lurkRecv(skt)
    if (data == None):
        print('DEBUG: lurkRecv() passed None, corresponding to a connection or OS error.')
        break
    message = lurkRead(data)
    if (message == None):
        continue
    print('DEBUG: Passing to lurkClient():', message)
    result = lurkClient(skt, message)
    if (result == 1):
        print('WARN: Client does not support receiving this message!')
        print('INFO: This could also occur if lurkClient() was passed completely invalid data, but the first byte in the message happens to be a valid lurk message type.')
        continue
    elif (result == 2):
        print('WARN: lurkClient() received a message type not supported by the LURK protocol!')
        continue

"""
#character2 = Character("Test Dummy #2", 0x4, 25, 25, 100, 20, 100, 40, len(characterDescription), characterDescription)
#character2 = Character.sendCharacter(character2, skt)

data = bytearray(b'')
while True:
    if data == b'':
        try:
            data = skt.recv(4096)
        except ConnectionError:
            print('WARN: Connection broken, stopping!')
            break
    elif data != b'':
        if (data[0] == MESSAGE):
            pass
        
        # Client should not receive CHANGEROOM messages!
        elif (data[0] == CHANGEROOM):
            changeRoomData = data[0:3]
            Error.sendError(skt, 0)
            data = data.replace(changeRoomData, b'')
        
        elif (data[0] == FIGHT):
            pass
        
        elif (data[0] == PVPFIGHT):
            pass
        
        elif (data[0] == LOOT):
            pass
        
        elif (data[0] == START):
            pass
        
        elif (data[0] == ERROR):
            errorDataConst = data[0:4]
            msgType, errCode, errMsgLen = Error.recvErrorConst(skt, errorDataConst)
            errorDataVar = data[4:4+errMsgLen]
            errMsg = Error.recvErrorVar(skt, errorDataVar)
            
            # If received ERROR is about invaid character stats
            if (errCode == 4):
                #character = Character("Test Dummy #3", 0x4, 25, 25, 50, 20, 100, 40, len(characterDescription), characterDescription)
                #character = Character.sendCharacter(character, skt)
                pass
            #leave = Leave.sendLeave(skt)
            continue
            
        elif (data[0] == ACCEPT):
            acceptData = data[0:2]
            msgType, accept = Accept.recvAccept(skt, acceptData)
            data = data.replace(acceptData, b'')
            continue
        
        elif (data[0] == ROOM):
            roomDataConst = data[0:37]
            msgType, roomNum, roomName, roomDesLen = Room.recvRoomConst(skt, roomDataConst)
            roomDataVar = data[37:37+roomDesLen]
            roomDes = Room.recvRoomVar(skt, roomDataVar, roomDesLen)
            roomData = roomDataConst + roomDataVar
            data = data.replace(roomData, b'')
            #ChangeRoom.sendChangeRoom(skt, 1)
            continue
        
        elif (data[0] == CHARACTER):
            characterDataConst = data[0:48]
            msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = Character.recvCharacterConst(characterDataConst)
            characterDataVar = data[48:48+charDesLen]
            charDes = Character.recvCharacterVar(characterDataVar, charDesLen)
            characterData = characterDataConst + characterDataVar
            data = data.replace(characterData, b'')
        
        elif (data[0] == GAME):
            gameDataConst = data[0:7]
            msgType, initPoints, statLimit, gameDesLen = Game.recvGameConst(gameDataConst)
            gameDataVar = data[7:7+gameDesLen]
            gameDes = Game.recvGameVar(gameDataVar, gameDesLen)
            gameData = gameDataConst + gameDataVar
            data = data.replace(gameData, b'')
            continue
        
        elif (data[0] == LEAVE):
            pass
        
        elif (data[0] == CONNECTION):
            pass
        
        elif (data[0] == VERSION):
            versionData = data[0:5]
            msgType, major, minor, extSize = Version.recvVersion(versionData)
            data = data.replace(versionData, b'')
            continue
        
        else:
            print('ERROR: Invalid message type detected, erasing buffer!')
            data = data.replace(data, b'')
            continue
"""