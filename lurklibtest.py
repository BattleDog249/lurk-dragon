# Used for testing a new lurkRecv
    # Rather than calling socket.recv once into a big buffer, call only as much as expected.
    # This should fix server failing thorough lurktest

#!/usr/bin/env python3

import socket
import struct

from colorama import Fore

MESSAGE = int(1)
MESSAGE_LEN = int(67)
CHANGEROOM = int(2)
CHANGEROOM_LEN = int(3)
FIGHT = int(3)
FIGHT_LEN = int(1)
PVPFIGHT = int(4)
PVPFIGHT_LEN = int(33)
LOOT = int(5)
LOOT_LEN = int(33)
START = int(6)
START_LEN = int(1)
ERROR = int(7)
ERROR_LEN = int(4)
ACCEPT = int(8)
ACCEPT_LEN = int(2)
ROOM = int(9)
ROOM_LEN = int(37)
CHARACTER = int(10)
CHARACTER_LEN = int(48)
GAME = int(11)
GAME_LEN = int(7)
LEAVE = int(12)
LEAVE_LEN = int(1)
CONNECTION = int(13)
CONNECTION_LEN = int(37)
VERSION = int(14)
VERSION_LEN = int(5)

class Lurk:
    def lurkSend(skt, message):
        try:
            skt.sendall(message)
            print(Fore.WHITE+'DEBUG: lurkSend: Sent message!')
            return 0
        except socket.error:
            print(Fore.RED+'ERROR: lurkSend: Caught socket.error, returning None!')
            return None
    
    def recvAll(skt, n):
        data = bytearray()
        while len(data) < n:
            try:
                packet = skt.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            except socket.error:
                return None
        return data
    
    def lurkRecv(skt):
        while True:
            try:
                msgType = Lurk.recvAll(skt, 1)
                if not msgType:
                    print(Fore.RED+'ERROR: lurkRecv: Received {}, signaling a client disconnect, returning None!'.format(msgType))
                    return None
                msgType, = struct.unpack('<B', msgType)
            except struct.error:
                print(Fore.RED+'ERROR: lurkRecv: Failed to unpack msgType!')
                continue
            print('msgType:', msgType, 'Type:', type(msgType))
            if msgType < 1 or msgType > 14:
                print(Fore.RED+'ERROR: lurkRecv: {} not a valid lurk message type!'.format(msgType))
                continue
        
            if msgType == MESSAGE:
                print('DEBUG: lurkRecv: Handling potential MESSAGE type {}'.format(msgType))
                try:
                    messageHeader = Lurk.recvAll(skt, MESSAGE_LEN - 1)
                    if not messageHeader:
                        print(Fore.RED+'ERROR: lurkRecv: lurkRecvAll returned None, signaling socket disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential MESSAGE header: {}'.format(messageHeader))
                    msgLen, recvName, sendName = struct.unpack('<H32s32s', messageHeader)
                    messageData = Lurk.recvAll(skt, msgLen)
                    if not messageData:
                        print(Fore.RED+'ERROR: lurkRecv: lurkRecvAll returned None, signaling socket disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential MESSAGE data: {}'.format(messageData))
                    message, = struct.unpack('<%ds' %msgLen, messageData)
                    return (msgType, msgLen, recvName.decode('utf-8'), sendName.decode('utf-8'), message.decode('utf-8'))
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack MESSAGE!')
                    continue
            
            elif msgType == CHANGEROOM:
                print('DEBUG: lurkRecv: Handling potential CHANGEROOM type {}'.format(msgType))
                try:
                    changeroomHeader = Lurk.recvAll(skt, CHANGEROOM_LEN - 1)
                    if not changeroomHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential CHANGEROOM header: {}'.format(changeroomHeader))
                    desiredRoomNum, = struct.unpack('<H', changeroomHeader)
                    return (msgType, desiredRoomNum)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack CHANGEROOM!')
                    continue
            
            elif msgType == FIGHT:
                print('DEBUG: lurkRecv: Handling potential FIGHT type {}'.format(msgType))
                return (msgType,)
            
            elif msgType == PVPFIGHT:
                print('DEBUG: lurkRecv: Handling potential PVPFIGHT type {}'.format(msgType))
                try:
                    pvpfightHeader = Lurk.recvAll(skt, PVPFIGHT_LEN - 1)
                    if not pvpfightHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential PVPFIGHT header: {}'.format(pvpfightHeader))
                    targetName = struct.unpack('<32s', pvpfightHeader)
                    return (msgType, targetName.decode('utf-8'))
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack PVPFIGHT!')
                    continue
            
            elif msgType == LOOT:
                print('DEBUG: lurkRecv: Handling potential LOOT type {}'.format(msgType))
                try:
                    lootHeader = Lurk.recvAll(skt, LOOT_LEN - 1)
                    if not lootHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential LOOT header: {}'.format(lootHeader))
                    targetName = struct.unpack('<32s', lootHeader)
                    return (msgType, targetName.decode('utf-8'))
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack LOOT!')
                    continue
            
            elif msgType == START:
                print('DEBUG: lurkRecv: Handling potential START type {}'.format(msgType))
                return (msgType,)
            
            elif msgType == ERROR:
                print('DEBUG: lurkRecv: Handling potential ERROR type {}'.format(msgType))
                try:
                    errorHeader = Lurk.recvAll(skt, ERROR_LEN - 1)
                    if not errorHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential ERROR header: {}'.format(errorHeader))
                    errCode, errMsgLen = struct.unpack('<BH', errorHeader)
                    errorData = Lurk.recvAll(skt, errMsgLen)
                    if not errorData:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential ERROR data: {}'.format(errorData))
                    errMsg, = struct.unpack('<%ds' %errMsgLen, errorData)
                    return (msgType, errCode, errMsgLen, errMsg.decode('utf-8'))
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack ERROR!')
                    continue
            
            elif msgType == ACCEPT:
                print('DEBUG: lurkRecv: Handling potential ACCEPT type {}'.format(msgType))
                try:
                    acceptHeader = Lurk.recvAll(skt, ACCEPT_LEN - 1)
                    if not acceptHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential ACCEPT header: {}'.format(acceptHeader))
                    acceptedMsg, = struct.unpack('<B', acceptHeader)
                    return (msgType, acceptedMsg)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack ACCEPT!')
                    continue
            
            elif msgType == ROOM:
                print('DEBUG: lurkRecv: Handling potential ROOM type {}'.format(msgType))
                try:
                    roomHeader = Lurk.recvAll(skt, ROOM_LEN - 1)
                    if not roomHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential ROOM header: {}'.format(roomHeader))
                    roomNum, roomName, roomDesLen = struct.unpack('<H32sH', roomHeader)
                    roomData = Lurk.recvAll(skt, roomDesLen)
                    if not roomData:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential ROOM data: {}'.format(roomData))
                    roomDes, = struct.unpack('<%ds' %roomDesLen, roomData)
                    return (msgType, roomNum, roomName.decode('utf-8'), roomDesLen, roomDes.decode('utf-8'))   
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack ROOM!')
                    continue
            
            elif msgType == CHARACTER:
                print('DEBUG: lurkRecv: Handling potential CHARACTER type {}'.format(msgType))
                try:
                    characterHeader = Lurk.recvAll(skt, CHARACTER_LEN - 1)
                    if not characterHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential CHARACTER header: {}'.format(characterHeader))
                    name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<32sB3Hh3H', characterHeader)
                    characterData = Lurk.recvAll(skt, charDesLen)
                    if not characterData:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential CHARACTER data: {}'.format(characterData))
                    charDes, = struct.unpack('<%ds' %charDesLen, characterData)
                    return (msgType, name.decode('utf-8'), flags, attack, defense, regen, health, gold, room, charDesLen, charDes.decode('utf-8'))
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack CHARACTER!')
                    continue
            
            elif msgType == GAME:
                print('DEBUG: lurkRecv: Handling potential GAME type {}'.format(msgType))
                try:
                    gameHeader = Lurk.recvAll(skt, GAME_LEN - 1)
                    if not gameHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential GAME header: {}'.format(gameHeader))
                    initPoints, statLimit, gameDesLen = struct.unpack('<3H', gameHeader)
                    gameData = Lurk.recvAll(skt, gameDesLen)
                    if not gameData:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential GAME data: {}'.format(gameData))
                    gameDes, = struct.unpack('<%ds' %gameDesLen, gameData)
                    return (msgType, initPoints, statLimit, gameDesLen, gameDes.decode('utf-8'))
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack GAME!')
                    continue
            
            elif msgType == LEAVE:
                print('DEBUG: lurkRecv: Handling potential LEAVE type {}'.format(msgType))
                return (msgType,)
            
            elif msgType == CONNECTION:
                print('DEBUG: lurkRecv: Handling potential CONNECTION type {}'.format(msgType))
                try:
                    connectionHeader = Lurk.recvAll(skt, CONNECTION_LEN - 1)
                    if not connectionHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential CONNECTION header: {}'.format(connectionHeader))
                    roomNum, roomName, roomDesLen = struct.unpack('<H32sH', connectionHeader)
                    connectionData = Lurk.recvAll(skt, roomDesLen)
                    if not connectionData:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential CONNECTION data: {}'.format(connectionData))
                    roomDes = struct.unpack('<%ds' %roomDesLen, connectionData)
                    return (msgType, roomNum, roomName.decode('utf-8'), roomDesLen, roomDes.decode('utf-8'))
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack CONNECTION header!')
                    continue
            
            elif msgType == VERSION:
                print('DEBUG: lurkRecv: Handling potential VERSION type {}'.format(msgType))
                try:
                    versionHeader = Lurk.recvAll(skt, VERSION_LEN - 1)
                    if not versionHeader:
                        print(Fore.RED+'ERROR: lurkRecv: Received b'', signaling a client disconnect, returning None!')
                        return None
                    print('DEBUG: lurkRecv: Potential VERSION header: {}'.format(versionHeader))
                    major, minor, extSize = struct.unpack('<2BH', versionHeader)
                    return (msgType, major, minor, extSize)
                except struct.error:
                    print(Fore.RED+'ERROR: lurkRecv: Failed to unpack VERSION header!')
                    continue
            
            else:
                print(Fore.RED+'ERROR: lurkRecv: Invalid message type {}, continuing!'.format(msgType))
                continue
    
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
            characterPacked = struct.pack('<B32sB3Hh3H%ds' %character[9], character[0], character[1].encode(), character[2], character[3], character[4], character[5], character[6], character[7], character[8], character[9], character[10].encode())
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