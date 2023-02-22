'''
CS435 LurkDragon: Client
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

#!/usr/bin/env python3

# Import socket module, required for network communications
import socket
# Import custom lurk module
from lurk import *

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
#character2 = Character("Test Dummy #2", 0x4, 25, 25, 100, 20, 100, 40, len(characterDescription), characterDescription)
#character2 = Character.sendCharacter(character2, skt)

def userInput(skt):
    while True:
        inputType = input('Type: ')
        if (inputType == MESSAGE):
            msgType = inputType
            msgLen = input('Message Length: ')
            recipientName = input('Recipient Name: ')
            senderName = input('Sender Name: ')
            
        elif (inputType == CHANGEROOM):
            msgType = inputType
            roomNum = input('Room Number to enter: ')
            
        elif (inputType == FIGHT):
            msgType = inputType
            
        elif (inputType == PVPFIGHT):
            msgType = inputType
            targetPlayer = input('Enter Name of player to fight: ')
            
        elif (inputType == LOOT):
            msgType = inputType
            pass
        elif (inputType == START):
            msgType = inputType
            pass
        elif (inputType == ERROR):
            msgType = inputType
            pass
        elif (inputType == ACCEPT):
            msgType = inputType
            pass
        elif (inputType == ROOM):
            msgType = inputType
            pass
        elif (inputType == CHARACTER):
            msgType = inputType
            pass
        elif (inputType == GAME):
            msgType = inputType
            pass
        elif (inputType == LEAVE):
            msgType = inputType
            pass
        elif (inputType == CONNECTION):
            msgType = inputType
            pass
        elif (inputType == VERSION):
            msgType = inputType
            pass
        else:
            # Handle client sending invalid types
            print('ERROR: Message type {} is not supported!'.format(inputType))

data = bytearray(b'')
while True:
    if data == b'':
        try:
            data = skt.recv(4096)
        except ConnectionError:
            print('WARN: Connection broken, stopping!')
            break
    elif data != b'':
        if (data[0] == 1):
            # Handle MESSAGE
            pass
        
        elif (data[0] == 2):
            # Handle CHANGEROOM
            pass
        
        elif (data[0] == 3):
            # Handle FIGHT
            pass
        
        elif (data[0] == 4):
            # Handle PVPFIGHT
            pass
        
        elif (data[0] == 5):
            # Handle LOOT
            pass
        
        elif (data[0] == 6):
            # Handle START
            pass
        
        elif (data[0] == 7):
            # Handle ERROR
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
            
        elif (data[0] == 8):
            # Handle ACCEPT
            acceptData = data[0:2]
            msgType, accept = Accept.recvAccept(skt, acceptData)
            data = data.replace(acceptData, b'')
            continue
        
        elif (data[0] == 9):
            # Handle ROOM
            roomDataConst = data[0:37]
            msgType, roomNum, roomName, roomDesLen = Room.recvRoomConst(skt, roomDataConst)
            roomDataVar = data[37:37+roomDesLen]
            roomDes = Room.recvRoomVar(skt, roomDataVar, roomDesLen)
            roomData = roomDataConst + roomDataVar
            data = data.replace(roomData, b'')
            continue
        
        elif (data[0] == 10):
            # Handle CHARACTER
            pass
        
        elif (data[0] == 11):
            # Handle GAME
            gameDataConst = data[0:7]
            msgType, initPoints, statLimit, gameDesLen = Game.recvGameConst(skt, gameDataConst)
            gameDataVar = data[7:7+gameDesLen]
            gameDes = Game.recvGameVar(skt, gameDataVar, gameDesLen)
            gameData = gameDataConst + gameDataVar
            data = data.replace(gameData, b'')
            continue
        
        elif (data[0] == 12):
            # Handle LEAVE
            pass
        
        elif (data[0] == 13):
            # Handle CONNECTION
            pass
        
        elif (data[0] == 14):
            # Handle VERSION
            versionData = data[0:5]
            msgType, major, minor, extSize = Version.recvVersion(skt, versionData)
            data = data.replace(versionData, b'')
            continue
        
        else:
            print('ERROR: Invalid message type detected, erasing buffer!')
            data = data.replace(data, b'')
            continue