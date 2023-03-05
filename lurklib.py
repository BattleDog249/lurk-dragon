#!/usr/bin/env python3

import socket
import struct

from colorama import Fore

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

class Lurk:
    def lurkSend(skt, message):
        try:
            skt.sendall(message)
            print(Fore.WHITE+'DEBUG: lurkSend: Sent message!')
            return 0
        except socket.error:
            print(Fore.RED+'ERROR: lurkSend: Caught socket.error, raising socket.error!')
            raise socket.error
    
    def lurkRecv(skt):
        messages = []
        data = bytearray(b'')
        try:
            data = skt.recv(1024)
            if data == b'':
                print(Fore.RED+'ERROR: lurkRecv: Received {}, signaling a client disconnect, returning None!'.format(data))
                return None
        except socket.error:
            print(Fore.RED+'ERROR: lurkRecv: Caught socket.error, raising socket.error!')
            return None
        
        print(Fore.WHITE+'DEBUG: lurkRecv: Data:', data)
        i = 0
        while i < len(data):
            print(Fore.WHITE+'DEBUG: lurkRecv: Data at index {}: {}'.format(i, data[i]))
            
            if (data[i] < 1 or data[i] > 14):
                    print(Fore.RED+'ERROR: lurkRecv: {} not a valid lurk message type!'.format(data[i]))
                    i += 1
                    continue
            
            if (data[i] == MESSAGE):
                print('DEBUG: lurkRecv: Handling potential MESSAGE type {}'.format(data[i]))
                messageHeaderLen = i + 67
                messageHeader = data[i:messageHeaderLen]
                print('DEBUG: lurkRecv: Potential MESSAGE header: {}'.format(messageHeader))
                try:
                    msgType, msgLen, recvName, sendName = struct.unpack('<BH32s32s', messageHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack MESSAGE header!')
                    i += messageHeaderLen
                    continue
                messageData = data[messageHeaderLen:messageHeaderLen+msgLen]
                print('DEBUG: lurkRecv: Potential MESSAGE data: {}'.format(messageData))
                try:
                    message, = struct.unpack('<%ds' %msgLen, messageData)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack MESSAGE data!')
                    i += msgLen
                    continue
                messages.append((msgType, msgLen, recvName.decode('utf-8'), sendName.decode('utf-8'), message.decode('utf-8')))
                i += messageHeaderLen + msgLen
                continue
            
            elif (data[i] == CHANGEROOM):
                print('DEBUG: lurkRecv: Handling potential CHANGEROOM type {}'.format(data[i]))
                changeroomHeaderLen = i + 3
                changeroomHeader = data[i:changeroomHeaderLen]
                print('DEBUG: lurkRecv: Potential CHANGEROOM header: {}'.format(changeroomHeader))
                try:
                    msgType, desiredRoomNum = struct.unpack('<BH', changeroomHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv(): Failed to unpack CHANGEROOM header!')
                    i += changeroomHeaderLen
                    continue
                messages.append((msgType, desiredRoomNum))
                i += changeroomHeaderLen
                continue
            
            elif (data[i] == FIGHT):
                print('DEBUG: lurkRecv: Handling potential FIGHT type {}'.format(data[i]))
                fightHeaderLen = i + 1
                fightHeader = data[i:fightHeaderLen]
                print('DEBUG: lurkRecv: Potential FIGHT header: {}'.format(fightHeader))
                try:
                    msgType = struct.unpack('<B', fightHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack FIGHT header!')
                    i += fightHeaderLen
                    continue
                messages.append((msgType,))
                i += fightHeaderLen
                continue
            
            elif (data[i] == PVPFIGHT):
                print('DEBUG: lurkRecv: Handling potential PVPFIGHT type {}'.format(data[i]))
                pvpfightHeaderLen = i + 33
                pvpfightHeader = data[i:pvpfightHeaderLen]
                print('DEBUG: lurkRecv: Potential PVPFIGHT header: {}'.format(pvpfightHeader))
                try:
                    msgType, targetName = struct.unpack('<B32s', pvpfightHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack PVPFIGHT header!')
                    i += pvpfightHeaderLen
                    continue
                messages.append((msgType, targetName.decode('utf-8')))
                i += pvpfightHeaderLen
                continue
            
            elif (data[i] == LOOT):
                print('DEBUG: lurkRecv: Handling potential LOOT type {}'.format(data[i]))
                lootHeaderLen = i + 33
                lootHeader = data[i:lootHeaderLen]
                print('DEBUG: lurkRecv: Potential LOOT header: {}'.format(lootHeader))
                try:
                    msgType, targetName = struct.unpack('<B32s', lootHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack LOOT header!')
                    i += lootHeaderLen
                    continue
                messages.append((msgType, targetName.decode('utf-8')))
                i += lootHeaderLen
                continue
            
            elif (data[i] == START):
                print('DEBUG: lurkRecv: Handling potential START type {}'.format(data[i]))
                startHeaderLen = i + 1
                startHeader = data[i:startHeaderLen]
                print('DEBUG: lurkRecv: Potential START header: {}'.format(startHeader))
                try:
                    msgType = struct.unpack('<B', startHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack START header!')
                    i += startHeaderLen
                    continue
                messages.append((msgType))
                i += startHeaderLen
                continue
            
            elif (data[i] == ERROR):
                print('DEBUG: lurkRecv: Handling potential ERROR type {}'.format(data[i]))
                errorHeaderLen = i + 4
                errorHeader = data[i:errorHeaderLen]
                print('DEBUG: lurkRecv: Potential ERROR header: {}'.format(errorHeader))
                try:
                    msgType, errCode, errMsgLen = struct.unpack('<2BH', errorHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack ERROR header!')
                    i += errorHeaderLen
                    continue
                errorData = data[errorHeaderLen:errorHeaderLen+errMsgLen]
                print('DEBUG: lurkRecv: Potential ERROR data: {}'.format(errorData))
                try:
                    errMsg, = struct.unpack('<%ds' %errMsgLen, errorData)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack ERROR data!')
                    i += errMsgLen
                    continue
                messages.append((msgType, errCode, errMsgLen, errMsg.decode('utf-8')))
                i += errorHeaderLen + errMsgLen
                continue
            
            elif (data[i] == ACCEPT):
                print('DEBUG: lurkRecv: Handling potential ACCEPT type {}'.format(data[i]))
                acceptHeaderLen = i + 2
                acceptHeader = data[i:acceptHeaderLen]
                print('DEBUG: lurkRecv: Potential ACCEPT header: {}'.format(acceptHeader))
                try:
                    msgType, acceptedMsg = struct.unpack('<2B', acceptHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack ACCEPT data!')
                    i += acceptHeaderLen
                    continue
                messages.append((msgType, acceptedMsg))
                i += acceptHeaderLen
                continue
            
            elif (data[i] == ROOM):
                print('DEBUG: lurkRecv: Handling potential ROOM type {}'.format(data[i]))
                roomHeaderLen = i + 37
                roomHeader = data[i:roomHeaderLen]
                print('DEBUG: lurkRecv: Potential ROOM header: {}'.format(roomHeader))
                try:
                    msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', roomHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack ROOM header!')
                    i += roomHeaderLen
                    continue
                roomData = data[roomHeaderLen:roomHeaderLen+roomDesLen]
                print('DEBUG: lurkRecv: Potential ROOM data: {}'.format(roomData))
                try:
                    roomDes, = struct.unpack('<%ds' %roomDesLen, roomData)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack ROOM data!')
                    i += roomDesLen
                    continue
                messages.append((msgType, roomNum, roomName, roomDesLen, roomDes.decode('utf-8')))
                i += roomHeaderLen + roomDesLen
                continue
            
            elif (data[i] == CHARACTER):
                print('DEBUG: lurkRecv: Handling potential CHARACTER type {}'.format(data[i]))
                characterHeaderLen = i + 48
                characterHeader = data[i:characterHeaderLen]
                print('DEBUG: lurkRecv: Potential CHARACTER header: {}'.format(characterHeader))
                try:
                    msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', characterHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack CHARACTER header!')
                    i += characterHeaderLen
                    continue
                characterData = data[characterHeaderLen:characterHeaderLen+charDesLen]
                print('DEBUG: lurkRecv: Potential CHARACTER data: {}'.format(characterData))
                try:
                    charDes, = struct.unpack('<%ds' %charDesLen, characterData)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack CHARACTER data!')
                    i += characterHeaderLen + charDesLen
                    continue
                messages.append((msgType, name.decode('utf-8'), hex(flags), attack, defense, regen, health, gold, room, charDesLen, charDes.decode('utf-8')))
                i += characterHeaderLen + charDesLen
                continue
            
            elif (data[i] == GAME):
                print('DEBUG: lurkRecv: Handling potential GAME type {}'.format(data[i]))
                gameHeaderLen = i + 7
                gameHeader = data[i:gameHeaderLen]
                print('DEBUG: lurkRecv: Potential GAME header: {}'.format(gameHeader))
                try:
                    msgType, initPoints, statLimit, gameDesLen = struct.unpack('<B3H', gameHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack GAME header!')
                    i += gameHeaderLen
                    continue
                gameData = data[gameHeaderLen:gameHeaderLen+gameDesLen]
                print('DEBUG: lurkRecv: Potential GAME data: {}'.format(gameData))
                try:
                    gameDes, = struct.unpack('<%ds' %gameDesLen, gameData)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack GAME data!')
                    i += gameDesLen
                    continue
                messages.append((msgType, initPoints, statLimit, gameDesLen, gameDes.decode('utf-8')))
                i += gameHeaderLen + gameDesLen
                continue
            
            elif (data[i] == LEAVE):
                print('DEBUG: lurkRecv: Handling potential LEAVE type {}'.format(data[i]))
                leaveHeaderLen = i + 1
                leaveHeader = data[i:leaveHeaderLen]
                print('DEBUG: lurkRecv: Potential LEAVE header: {}'.format(leaveHeader))
                try:
                    msgType = struct.unpack('<B', leaveHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack LEAVE header!')
                    i += leaveHeaderLen
                    continue
                messages.append((msgType))
                i += leaveHeaderLen
                continue
            
            elif (data[0] == CONNECTION):
                print('DEBUG: lurkRecv: Handling potential CONNECTION type {}'.format(data[i]))
                connectionHeaderLen = i + 37
                connectionHeader = data[i:connectionHeaderLen]
                print('DEBUG: lurkRecv: Potential CONNECTION header: {}'.format(connectionHeader))
                try:
                    msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', connectionHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack CONNECTION header!')
                    i += connectionHeaderLen
                    continue
                connectionData = data[37:37+roomDesLen]
                print('DEBUG: lurkRecv: Potential CONNECTION data: {}'.format(connectionData))
                try:
                    roomDes = struct.unpack('<%ds' %roomDesLen, connectionData)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack CONNECTION data!')
                    i += roomDesLen
                    continue
                messages.append((msgType, roomNum, roomName, roomDesLen, roomDes.decode('utf-8')))
                i += connectionHeaderLen + roomDesLen
                continue
            
            elif (data[0] == VERSION):
                print('DEBUG: lurkRecv: Handling potential VERSION type {}'.format(data[i]))
                versionHeaderLen = i + 5
                versionHeader = data[i:versionHeaderLen]
                print('DEBUG: lurkRecv: Potential VERSION header: {}'.format(versionHeader))
                try:
                    msgType, major, minor, extSize = struct.unpack('<3BH', versionHeader)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack VERSION header!')
                    i += versionHeaderLen
                    continue
                messages.append((msgType, major, minor, extSize))
                i += versionHeaderLen
                continue
            
            else:
                print(Fore.RED+'ERROR: lurkRecv: Invalid message type {}, continuing!'.format(data[i]))
                i += 1
                continue
        print(Fore.GREEN+'INFO: lurkRecv: Returning messages:', messages)
        return messages
    
    def sendMessage(skt, message):
        try:
            messagePacked = struct.pack('<BH32s30sH%ds' %message[1], message[0], message[1], message[2], message[3], message[4], message[5])
            print('DEBUG: Sending MESSAGE message!')
            Lurk.lurkSend(skt, messagePacked)
        except struct.error:
            print('ERROR: Failed to pack MESSAGE structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendChangeroom(skt, changeRoom):
        try:
            changeroomPacked = struct.pack('<BH', changeRoom[0], changeRoom[1])
            print('DEBUG: Sending CHANGEROOM message!')
            Lurk.lurkSend(skt, changeroomPacked)
        except struct.error:
            print('ERROR: Failed to pack CHANGEROOM structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendFight(skt):
        try:
            fightPacked = struct.pack('<B', FIGHT)
            print('DEBUG: Sending FIGHT message!')
            Lurk.lurkSend(skt, fightPacked)
        except struct.error:
            print('ERROR: Failed to pack FIGHT structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendPvpfight(skt, pvpFight):
        try:
            pvpfightPacked = struct.pack('<B32s', pvpFight[0], pvpFight[1])
            print('DEBUG: Sending PVPFIGHT message!')
            Lurk.lurkSend(skt, pvpfightPacked)
        except struct.error:
            print('ERROR: Failed to pack PVPFIGHT structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendLoot(skt, loot):
        try:
            lootPacked = struct.pack('<B32s', loot[0], loot[1])
            print('DEBUG: Sending LOOT message!')
            Lurk.lurkSend(skt, lootPacked)
        except struct.error:
            print('ERROR: Failed to pack LOOT structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendStart(skt, start):
        try:
            startPacked = struct.pack('<B', START)
            print('DEBUG: Sending START message!')
            Lurk.lurkSend(skt, startPacked)
        except struct.error:
            print('ERROR: Failed to pack START structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendError(skt, error):
        """_summary_

        Args:
            skt (socket): Receiving socket
            error (tuple): (msgType, errorCode, errorMsgLen, errorMsg)

        Raises:
            struct.error: _description_
            Lurk.lurkSend.Error: _description_

        Returns:
            _type_: _description_
        """
        try:
            errorPacked = struct.pack('<2BH%ds' %error[2], error[0], error[1], error[2], bytes(error[3], 'utf-8'))
            print('DEBUG: Sending ERROR message!')
            Lurk.lurkSend(skt, errorPacked)
        except struct.error:
            print('ERROR: Failed to pack ERROR structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendAccept(skt, accept):
        try:
            acceptPacked = struct.pack('<2B', ACCEPT, accept)
            print('DEBUG: Sending ACCEPT message!')
            Lurk.lurkSend(skt, acceptPacked)
        except struct.error:
            print('ERROR: Failed to pack ACCEPT structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendRoom(skt, room):
        try:
            roomPacked = struct.pack('<BH32sH%ds' %room[3], room[0], room[1], room[2], room[3], bytes(room[4], 'utf-8'))
            print('DEBUG: Sending ROOM message!')
            Lurk.lurkSend(skt, roomPacked)
        except struct.error:
            print('ERROR: Failed to pack ROOM structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendCharacter(skt, character):
        """_summary_

        Args:
            skt (_type_): _description_
            character (_type_): _description_

        Raises:
            struct.error: _description_
            Lurk.lurkSend.Error: _description_

        Returns:
            _type_: _description_
        """
        try:
            characterPacked = struct.pack('<B32sB7H%ds' %character[9], character[0], bytes(character[1], 'utf-8'), character[2], character[3], character[4], character[5], character[6], character[7], character[8], character[9], bytes(character[10], 'utf-8'))
            print('DEBUG: Sending CHARACTER message!')
            Lurk.lurkSend(skt, characterPacked)
        except struct.error:
            print('ERROR: Failed to pack CHARACTER structure!')
            raise struct.error
        except socket.error:
            print('ERROR: lurkSend() failed!')
            raise socket.error
        return 0
    def sendGame(skt, game):
        """_summary_

        Args:
            skt (_type_): _description_
            game (_type_): _description_

        Raises:
            struct.error: _description_
            Lurk.lurkSend.Error: _description_

        Returns:
            _type_: _description_
        """
        try:
            gamePacked = struct.pack('<B3H%ds' %game[3], game[0], game[1], game[2], game[3], bytes(game[4], 'utf-8'))
            print('DEBUG: Sending GAME message!')
            Lurk.lurkSend(skt, gamePacked)
        except struct.error:
            print('ERROR: Failed to pack GAME structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendLeave(skt):
        """Send a lurk LEAVE message to a socket.

        Args:
            skt (socket): Socket to send data to

        Raises:
            struct.error: Failed to pack data into a structure
            Lurk.lurkSend.Error: Function lurkSend failed

        Returns:
            int: 0 if function finishes successfully
        """
        try:
            leavePacked = struct.pack('<B', LEAVE)
            print('DEBUG: Sending LEAVE message!')
            Lurk.lurkSend(skt, leavePacked)
        except struct.error:
            print('ERROR: Failed to pack LEAVE structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendConnection(skt, connection):
        """Send a lurk CONNECTION message to a socket.

        Args:
            skt (socket): Socket to send data to
            connection (tuple): CONNECTION data

        Raises:
            struct.error: Failed to pack data into a structure
            Lurk.lurkSend.Error: Function lurkSend failed

        Returns:
            int: 0 if function finishes successfully
        """
        try:
            connectionPacked = struct.pack('<BH32sH%ds' %connection[3], connection[0], connection[1], connection[2], connection[3], connection[4])
            print('DEBUG: Sending CONNECTION message!')
            Lurk.lurkSend(skt, connectionPacked)
        except struct.error:
            print('ERROR: Failed to pack CONNECTION structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendVersion(skt, version):
        """Send a lurk VERSION message to a socket.

        Args:
            skt (socket): Socket to send data to
            version (tuple): VERSION data

        Raises:
            struct.error: Failed to pack data into a structure
            Lurk.lurkSend.Error: Function lurkSend failed

        Returns:
            int: 0 if function finishes successfully
        """
        try:
            versionPacked = struct.pack('<3BH', version[0], version[1], version[2], version[3])
            print('DEBUG: Sending VERSION message!')
            Lurk.lurkSend(skt, versionPacked)
        except struct.error:
            print('ERROR: Failed to pack VERSION structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0