#!/usr/bin/env python3

import lurk
import socket

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining host address & port of server to connect to
host = 'localhost'
port = 5010

# Connect to server with assigned host & port
skt.connect((host, port))
print('DEBUG: Connecting to server:', host)

characterDescription = "This is a collision test dummy, it is not sentient!"
#character1 = (10, "Big Stupid Guy", 0x4, 25, 25, 100, 20, 100, 40, len(characterDescription), characterDescription)
#status = Lurk.sendCharacter(skt, character1)
character2 = (10, "Legan", 0x4, 25, 25, 50, 1, 2, 3, len(characterDescription), characterDescription)
status = lurk.sendCharacter(skt, character2)
#character3 = Character(10, "Test Dummy #3", 0x4, 25, 25, 100, 20, 100, 40, len(characterDescription), characterDescription)
#status = Lurk.sendCharacter(skt, character3)

while True:
    try:
        messages = lurk.recv(skt)
        if (messages == None):
            print('WARN: Server must have disconnected!')
            break
    except ConnectionError:
        print('WARN: Lurk.lurkRecv() ConnectionError, breaking!')
        break
    print('DEBUG: List of Messages:', messages)
    for message in messages:
        
        if (message[0] == lurk.MESSAGE):
            msgType, msgLen, recvName, sendName, narration, message = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: Message Length:', msgLen)
            print('DEBUG: Recipient Name:', recvName)
            print('DEBUG: Sender Name:', sendName)
            print('DEBUG: End of sender Name or narration marker:', narration)
            print('DEBUG: Message:', message)
            continue
        
        elif (message[0] == lurk.CHANGEROOM):
            msgType, desiredRoomNum = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: desiredRoomNum:', desiredRoomNum)
            continue
        
        elif (message[0] == lurk.FIGHT):
            msgType = message
            print('DEBUG: Type:', msgType)
            continue
        
        elif (message[0] == lurk.PVPFIGHT):
            msgType, targetName = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: targetName:', targetName)
            continue
        
        elif (message[0] == lurk.LOOT):
            msgType, targetName = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: targetName:', targetName)
            continue
        
        elif (message[0] == lurk.START):
            msgType = message
            print('DEBUG: Type:', msgType)
            continue
        
        elif (message[0] == lurk.ERROR):
            msgType, errCode, errMsgLen, errMsg = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: errCode:', errCode)
            print('DEBUG: errMsgLen:', errMsgLen)
            print('DEBUG: errMsg:', errMsg)
            continue
        
        elif (message[0] == lurk.ACCEPT):
            msgType, acceptedMsg = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: acceptedMsg:', acceptedMsg)
            continue
        
        elif (message[0] == lurk.ROOM):
            msgType, roomNum, roomName, roomDesLen, roomDes = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: roomNum:', roomNum)
            print('DEBUG: roomName:', roomName)
            print('DEBUG: roomDesLen:', roomDesLen)
            print('DEBUG: roomDes:', roomDes)
            continue
        
        elif (message[0] == lurk.CHARACTER):
            msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: Name:', name)
            print('DEBUG: Flags:', flags)
            print('DEBUG: Attack:', attack)
            print('DEBUG: Defense:', defense)
            print('DEBUG: Regen:', regen)
            print('DEBUG: Health:', health)
            print('DEBUG: Gold:', gold)
            print('DEBUG: Room:', room)
            print('DEBUG: charDesLen:', charDesLen)
            print('DEBUG: charDes:', charDes)
            
            continue
        
        elif (message[0] == lurk.GAME):
            msgType, initPoints, statLimit, gameDesLen, gameDes = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: initPoints:', initPoints)
            print('DEBUG: statLimit:', statLimit)
            print('DEBUG: gameDesLen:', gameDesLen)
            print('DEBUG: gameDes:', gameDes)
            continue
        
        elif (message[0] == lurk.LEAVE):
            msgType = message
            print('DEBUG: Type:', msgType)
            continue
        
        elif (message[0] == lurk.CONNECTION):
            msgType, roomNum, roomName, roomDesLen, roomDes = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: roomNum:', roomNum)
            print('DEBUG: roomName:', roomName)
            print('DEBUG: roomDesLen:', roomDesLen)
            print('DEBUG: roomDes:', roomDes)
            continue
        
        elif (message[0] == lurk.VERSION):
            msgType, major, minor, extSize = message
            print('DEBUG: Type:', msgType)
            print('DEBUG: major:', major)
            print('DEBUG: minor:', minor)
            print('DEBUG: extSize:', extSize)
            continue
        
lurk.sendStart(skt, 6)