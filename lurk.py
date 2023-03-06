"""_summary_

    Raises:
        struct.error: _description_
        send.Error: _description_

    Returns:
        _type_: _description_
"""
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

def send(skt, message):
    """_summary_

    Args:
        skt (_type_): _description_
        message (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        skt.sendall(message)
        print(Fore.WHITE+'DEBUG: send: Sent message!')
        return 0
    except socket.error:
        print(Fore.RED+'ERROR: send: Caught socket.error, returning None!')
        return None
def recv(skt, size):
    """Receives size amount of bytes from a socket, and returns full lurk message

    Args:
        skt (socket): _description_
        size (int): _description_

    Returns:
        bytearray: _description_
        None: recv call failed
    """
    data = bytearray()
    while len(data) < size:
        try:
            packet = skt.recv(size - len(data))
            if not packet:
                return None
            data.extend(packet)
        except socket.error:
            return None
    return data
def read(skt):
    """Reads and interprets binary lurk messages from socket.

    Args:
        skt (socket): Socket to receive from

    Returns:
        tuple: Containing interpreted lurk message
    """
    while True:
        try:
            lurk_type = recv(skt, 1)
            if not lurk_type:
                print(Fore.RED+'ERROR: read: Received {}, signaling a client disconnect, returning None!'.format(lurk_type))
                return None
            lurk_type, = struct.unpack('<B', lurk_type)
        except struct.error:
            print(Fore.RED+'ERROR: read: Failed to unpack lurk_type!')
            continue
        if lurk_type < 1 or lurk_type > 14:
            print(Fore.RED+'ERROR: read: {} not a valid lurk message type!'.format(lurk_type))
            continue
        if lurk_type == MESSAGE:
            print('DEBUG: read: Handling potential MESSAGE type {}'.format(lurk_type))
            try:
                lurk_header = recv(skt, MESSAGE_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: readAll returned None, signaling socket disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential MESSAGE header: {}'.format(lurk_header))
                msg_len, recipient_name, sender_name = struct.unpack('<H32s32s', lurk_header)
                lurk_data = recv(skt, msg_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: readAll returned None, signaling socket disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential MESSAGE data: {}'.format(lurk_data))
                message, = struct.unpack('<%ds' %msg_len, lurk_data)
                return (lurk_type, msg_len, recipient_name.decode('utf-8'), sender_name.decode('utf-8'), message.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack MESSAGE!')
                continue
        elif lurk_type == CHANGEROOM:
            print('DEBUG: read: Handling potential CHANGEROOM type {}'.format(lurk_type))
            try:
                lurk_header = recv(skt, CHANGEROOM_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential CHANGEROOM header: {}'.format(lurk_header))
                room_num, = struct.unpack('<H', lurk_header)
                return (lurk_type, room_num)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack CHANGEROOM!')
                continue
        elif lurk_type == FIGHT:
            print('DEBUG: read: Handling potential FIGHT type {}'.format(lurk_type))
            return (lurk_type,)
        elif lurk_type == PVPFIGHT:
            print('DEBUG: read: Handling potential PVPFIGHT type {}'.format(lurk_type))
            try:
                pvpfightHeader = recv(skt, PVPFIGHT_LEN - 1)
                if not pvpfightHeader:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential PVPFIGHT header: {}'.format(pvpfightHeader))
                targetName = struct.unpack('<32s', pvpfightHeader)
                return (lurk_type, targetName.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack PVPFIGHT!')
                continue
        elif lurk_type == LOOT:
            print('DEBUG: read: Handling potential LOOT type {}'.format(lurk_type))
            try:
                lootHeader = recv(skt, LOOT_LEN - 1)
                if not lootHeader:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential LOOT header: {}'.format(lootHeader))
                targetName = struct.unpack('<32s', lootHeader)
                return (lurk_type, targetName.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack LOOT!')
                continue
        elif lurk_type == START:
            print('DEBUG: read: Handling potential START type {}'.format(lurk_type))
            return (lurk_type,)
        elif lurk_type == ERROR:
            print('DEBUG: read: Handling potential ERROR type {}'.format(lurk_type))
            try:
                errorHeader = recv(skt, ERROR_LEN - 1)
                if not errorHeader:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential ERROR header: {}'.format(errorHeader))
                errCode, errMsgLen = struct.unpack('<BH', errorHeader)
                errorData = recv(skt, errMsgLen)
                if not errorData:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential ERROR data: {}'.format(errorData))
                errMsg, = struct.unpack('<%ds' %errMsgLen, errorData)
                return (lurk_type, errCode, errMsgLen, errMsg.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack ERROR!')
                continue
        elif lurk_type == ACCEPT:
            print('DEBUG: read: Handling potential ACCEPT type {}'.format(lurk_type))
            try:
                acceptHeader = recv(skt, ACCEPT_LEN - 1)
                if not acceptHeader:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential ACCEPT header: {}'.format(acceptHeader))
                acceptedMsg, = struct.unpack('<B', acceptHeader)
                return (lurk_type, acceptedMsg)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack ACCEPT!')
                continue
        elif lurk_type == ROOM:
            print('DEBUG: read: Handling potential ROOM type {}'.format(lurk_type))
            try:
                roomHeader = recv(skt, ROOM_LEN - 1)
                if not roomHeader:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential ROOM header: {}'.format(roomHeader))
                roomNum, roomName, roomDesLen = struct.unpack('<H32sH', roomHeader)
                roomData = recv(skt, roomDesLen)
                if not roomData:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential ROOM data: {}'.format(roomData))
                roomDes, = struct.unpack('<%ds' %roomDesLen, roomData)
                return (lurk_type, roomNum, roomName.decode('utf-8'), roomDesLen, roomDes.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack ROOM!')
                continue
        elif lurk_type == CHARACTER:
            print('DEBUG: read: Handling potential CHARACTER type {}'.format(lurk_type))
            try:
                characterHeader = recv(skt, CHARACTER_LEN - 1)
                if not characterHeader:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential CHARACTER header: {}'.format(characterHeader))
                name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<32sB3Hh3H', characterHeader)
                characterData = recv(skt, charDesLen)
                if not characterData:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential CHARACTER data: {}'.format(characterData))
                charDes, = struct.unpack('<%ds' %charDesLen, characterData)
                return (lurk_type, name.decode('utf-8'), flags, attack, defense, regen, health, gold, room, charDesLen, charDes.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack CHARACTER!')
                continue
        elif lurk_type == GAME:
            print('DEBUG: read: Handling potential GAME type {}'.format(lurk_type))
            try:
                gameHeader = recv(skt, GAME_LEN - 1)
                if not gameHeader:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential GAME header: {}'.format(gameHeader))
                initPoints, statLimit, gameDesLen = struct.unpack('<3H', gameHeader)
                gameData = recv(skt, gameDesLen)
                if not gameData:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential GAME data: {}'.format(gameData))
                gameDes, = struct.unpack('<%ds' %gameDesLen, gameData)
                return (lurk_type, initPoints, statLimit, gameDesLen, gameDes.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack GAME!')
                continue
        elif lurk_type == LEAVE:
            print('DEBUG: read: Handling potential LEAVE type {}'.format(lurk_type))
            return (lurk_type,)
        elif lurk_type == CONNECTION:
            print('DEBUG: read: Handling potential CONNECTION type {}'.format(lurk_type))
            try:
                connectionHeader = recv(skt, CONNECTION_LEN - 1)
                if not connectionHeader:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential CONNECTION header: {}'.format(connectionHeader))
                roomNum, roomName, roomDesLen = struct.unpack('<H32sH', connectionHeader)
                connectionData = recv(skt, roomDesLen)
                if not connectionData:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential CONNECTION data: {}'.format(connectionData))
                roomDes = struct.unpack('<%ds' %roomDesLen, connectionData)
                return (lurk_type, roomNum, roomName.decode('utf-8'), roomDesLen, roomDes.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack CONNECTION header!')
                continue
        elif lurk_type == VERSION:
            print('DEBUG: read: Handling potential VERSION type {}'.format(lurk_type))
            try:
                versionHeader = recv(skt, VERSION_LEN - 1)
                if not versionHeader:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print('DEBUG: read: Potential VERSION header: {}'.format(versionHeader))
                major, minor, extSize = struct.unpack('<2BH', versionHeader)
                return (lurk_type, major, minor, extSize)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack VERSION header!')
                continue
        else:
            print(Fore.RED+'ERROR: read: Invalid message type {}, continuing!'.format(lurk_type))
            continue
def sendMessage(skt, message):
    try:
        messagePacked = struct.pack('<BH32s30sH%ds' %message[1], message[0], message[1], message[2], message[3], message[4], message[5])
        print('DEBUG: Sending MESSAGE message!')
        send(skt, messagePacked)
    except struct.error:
        print('ERROR: Failed to pack MESSAGE structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendChangeroom(skt, changeRoom):
    try:
        changeroomPacked = struct.pack('<BH', changeRoom[0], changeRoom[1])
        print('DEBUG: Sending CHANGEROOM message!')
        send(skt, changeroomPacked)
    except struct.error:
        print('ERROR: Failed to pack CHANGEROOM structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendFight(skt):
    try:
        fightPacked = struct.pack('<B', FIGHT)
        print('DEBUG: Sending FIGHT message!')
        send(skt, fightPacked)
    except struct.error:
        print('ERROR: Failed to pack FIGHT structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendPvpfight(skt, pvpFight):
    try:
        pvpfightPacked = struct.pack('<B32s', pvpFight[0], pvpFight[1])
        print('DEBUG: Sending PVPFIGHT message!')
        send(skt, pvpfightPacked)
    except struct.error:
        print('ERROR: Failed to pack PVPFIGHT structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendLoot(skt, loot):
    try:
        lootPacked = struct.pack('<B32s', loot[0], loot[1])
        print('DEBUG: Sending LOOT message!')
        send(skt, lootPacked)
    except struct.error:
        print('ERROR: Failed to pack LOOT structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendStart(skt, start):
    try:
        startPacked = struct.pack('<B', START)
        print('DEBUG: Sending START message!')
        send(skt, startPacked)
    except struct.error:
        print('ERROR: Failed to pack START structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendError(skt, error):
    """_summary_

    Args:
        skt (socket): Receiving socket
        error (tuple): (lurk_type, errorCode, errorMsgLen, errorMsg)

    Raises:
        struct.error: _description_
        send.Error: _description_

    Returns:
        _type_: _description_
    """
    try:
        errorPacked = struct.pack('<2BH%ds' %error[2], error[0], error[1], error[2], bytes(error[3], 'utf-8'))
        print('DEBUG: Sending ERROR message!')
        send(skt, errorPacked)
    except struct.error:
        print('ERROR: Failed to pack ERROR structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendAccept(skt, accept):
    try:
        acceptPacked = struct.pack('<2B', ACCEPT, accept)
        print('DEBUG: Sending ACCEPT message!')
        send(skt, acceptPacked)
    except struct.error:
        print('ERROR: Failed to pack ACCEPT structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendRoom(skt, room):
    try:
        roomPacked = struct.pack('<BH32sH%ds' %room[3], room[0], room[1], room[2], room[3], bytes(room[4], 'utf-8'))
        print('DEBUG: Sending ROOM message!')
        send(skt, roomPacked)
    except struct.error:
        print('ERROR: Failed to pack ROOM structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendCharacter(skt, character):
    """_summary_

    Args:
        skt (_type_): _description_
        character (_type_): _description_

    Raises:
        struct.error: _description_
        send.Error: _description_

    Returns:
        _type_: _description_
    """
    try:
        characterPacked = struct.pack('<B32sB3Hh3H%ds' %character[9], character[0], character[1].encode(), character[2], character[3], character[4], character[5], character[6], character[7], character[8], character[9], character[10].encode())
        print('DEBUG: Sending CHARACTER message!')
        send(skt, characterPacked)
    except struct.error:
        print('ERROR: Failed to pack CHARACTER structure!')
        raise struct.error
    except socket.error:
        print('ERROR: send() failed!')
        raise socket.error
    return 0
def sendGame(skt, game):
    """_summary_

    Args:
        skt (_type_): _description_
        game (_type_): _description_

    Raises:
        struct.error: _description_
        send.Error: _description_

    Returns:
        _type_: _description_
    """
    try:
        gamePacked = struct.pack('<B3H%ds' %game[3], game[0], game[1], game[2], game[3], bytes(game[4], 'utf-8'))
        print('DEBUG: Sending GAME message!')
        send(skt, gamePacked)
    except struct.error:
        print('ERROR: Failed to pack GAME structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendLeave(skt):
    """Send a lurk LEAVE message to a socket.

    Args:
        skt (socket): Socket to send data to

    Raises:
        struct.error: Failed to pack data into a structure
        send.Error: Function send failed

    Returns:
        int: 0 if function finishes successfully
    """
    try:
        leavePacked = struct.pack('<B', LEAVE)
        print('DEBUG: Sending LEAVE message!')
        send(skt, leavePacked)
    except struct.error:
        print('ERROR: Failed to pack LEAVE structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendConnection(skt, connection):
    """Send a lurk CONNECTION message to a socket.

    Args:
        skt (socket): Socket to send data to
        connection (tuple): CONNECTION data

    Raises:
        struct.error: Failed to pack data into a structure
        send.Error: Function send failed

    Returns:
        int: 0 if function finishes successfully
    """
    try:
        connectionPacked = struct.pack('<BH32sH%ds' %connection[3], connection[0], connection[1], connection[2], connection[3], connection[4])
        print('DEBUG: Sending CONNECTION message!')
        send(skt, connectionPacked)
    except struct.error:
        print('ERROR: Failed to pack CONNECTION structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
def sendVersion(skt, version):
    """Send a lurk VERSION message to a socket.

    Args:
        skt (socket): Socket to send data to
        version (tuple): VERSION data

    Raises:
        struct.error: Failed to pack data into a structure
        send.Error: Function send failed

    Returns:
        int: 0 if function finishes successfully
    """
    try:
        versionPacked = struct.pack('<3BH', version[0], version[1], version[2], version[3])
        print('DEBUG: Sending VERSION message!')
        send(skt, versionPacked)
    except struct.error:
        print('ERROR: Failed to pack VERSION structure!')
        raise struct.error
    except send.error:
        print('ERROR: send() failed!')
        raise send.Error
    return 0
