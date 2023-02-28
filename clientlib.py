#!/usr/bin/env python3

from lurklib import *

class Message:
    """Class for handling Lurk MESSAGE messages and related functions."""
    msgType = int(1)
    
    def sendMessage(skt, sender, receiver, message):
        """Return 0 if successfully pack MESSAGE fields into a variable before sending to socket."""
        messagePacked = 0
        return lurkSend(skt, messagePacked)

class ChangeRoom:
    """Class for handling Lurk CHANGEROOM messages and related functions."""
    msgType = int(2)
    
    def sendChangeRoom(skt, roomNum):
        """Return 0 if successfully pack CHANGEROOM fields into a variable before sending to socket."""
        changeRoomPacked = struct.pack('<BH', ChangeRoom.msgType, roomNum)
        print('DEBUG: Sending CHANGEROOM message!')
        return lurkSend(skt, changeRoomPacked)

class Fight:
    """Class for handling LurK FIGHT messages and related functions."""
    msgType = int(3)
    
    def sendFight(skt):
        """Return 0 if successfully pack FIGHT fields into a variable before sending to socket."""
        fightPacked = struct.pack('<B', Fight.msgType)
        print('DEBUG: Sending FIGHT message!')
        return lurkSend(skt, fightPacked)

class PVPFight:
    """Class for handling Lurk PVPFIGHT messages and related functions."""
    msgType = int(4)
    
    def sendPVPFight(skt):
        """Return 0 if successfully pack PVPFIGHT fields into a variable before sending to socket."""
        PVPFightPacked = 0
        return lurkSend(skt, PVPFightPacked)

class Loot:
    """Class for handling Lurk LOOT messages and related functions."""
    msgType = int(5)
    
    def sendLoot(skt):
        """Return 0 if successfully pack LOOT fields into a variable before sending to socket."""
        lootPacked = 0
        return lurkSend(skt, lootPacked)

class Start:
    """Class for handling Lurk START messages and related functions."""
    msgType = int(6)
    
    def sendStart(skt):
        """Return 0 if successfully pack START fields into a variable before sending to socket."""
        startPacked = struct.pack('<B', Start.msgType)
        #print('DEBUG: Sending START message!')
        #print('DEBUG: START Bytes:', startPacked)
        print('DEBUG: Sending START message!')
        return lurkSend(skt, startPacked)

class Error:
    """Client should not send ERROR messages"""
    msgType = int(7)

class Accept:
    """Client should not send ACCEPT messages"""
    msgType = int(8)

class Room:
    """Client should not send ROOM messages"""
    msgType = int(9)

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
    
    def sendCharacter(self, skt):
        """Return 0 if successfully pack CHARACTER fields into a variable before sending to socket."""
        characterPacked = struct.pack('<B32sB7H%ds' %self.charDesLen, Character.msgType, bytes(self.name, 'utf-8'), self.flags, self.attack, self.defense, self.regen, self.health, self.gold, self.room, len(self.charDes), bytes(self.charDes, 'utf-8'))
        print('LOG: Sending CHARACTER message!')
        return lurkSend(skt, characterPacked)

class Game:
    """Client should not send GAME messages"""
    msgType = int(11)

class Leave:
    """Class for handling Lurk LEAVE messages and related functions."""
    msgType = int(12)
    
    def sendLeave(skt):
        """Return 0 if successfully pack LEAVE fields into a variable before sending to socket."""
        leavePacked = struct.pack('<B', Leave.msgType)
        print('DEBUG: Sending LEAVE message!')
        return lurkSend(skt, leavePacked)

class Connection:
    """Client should not send CONNECTION messages"""
    msgType = int(13)

class Version:
    """Client should not send VERSION messages"""
    msgType = int(14)

def lurkClient(skt, message):
    if (message[0] == MESSAGE):
        print('DEBUG: Client handling MESSAGE message!')
        msgType, msgLen, recvName, sendName, narration, message = message
        return 0
    elif (message[0] == CHANGEROOM):
        print('WARN: Client handling CHANGEROOM message, going against protocol!')
        return 1
    elif (message[0] == FIGHT):
        print('WARN: Client handling FIGHT message, going against protocol!')
        return 1
    elif (message[0] == PVPFIGHT):
        print('WARN: Client handling PVPFIGHT message, going against protocol!')
        return 1
    elif (message[0] == LOOT):
        print('WARN: Client handling LOOT message, going against protocol!')
        return 1
    elif (message[0] == START):
        print('WARN: Client handling START message, going against protocol!')
        return 1
    elif (message[0] == ERROR):
        print('DEBUG: Client handling ERROR message!')
        msgType, errCode, errMsgLen, errMsg = message
        return 0
    elif (message[0] == ACCEPT):
        print('DEBUG: Client handling ACCEPT message!')
        msgType, accept = message
        return 0
    elif (message[0] == ROOM):
        print('DEBUG: Client handling ROOM message!')
        msgType, roomNum, roomName, roomDesLen, roomDes = message
        return 0
    elif (message[0] == CHARACTER):
        print('DEBUG: Client handling CHARACTER message!')
        msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes = message
        return 0
    elif (message[0] == GAME):
        print('DEBUG: Client handling GAME message!')
        msgType, initPoints, statLimit, gameDesLen, gameDes = message
        return 0
    elif (message[0] == LEAVE):
        print('WARN: Client handling LEAVE message, going against protocol!')
        return 1
    elif (message[0] == CONNECTION):
        print('DEBUG: Client handling CONNECTION message!')
        msgType, roomNum, roomName, roomDesLen, roomDes = message
        return 0
    elif (message[0] == VERSION):
        print('DEBUG: Client handling VERSION message!')
        msgType, major, minor, extSize = message
        return 0
    else:
        print('WARN: Invalid message type passed to lurkServ()')
        return 2

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