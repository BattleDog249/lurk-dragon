"""LURK protocol-related variables and functions that can be used in a client or server.
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
    """Sends an entire Lurk message to the specified socket.

    Args:
        skt (socket): Socket to send Lurk message to.
        message (packed): Lurk message, usually packed in byte format.

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
        skt (socket): Socket to receive from.
        size (int): Size of message to receive from socket buffer.

    Returns:
        bytearray: Raw data received from socket.
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
def pack():
    pass
def unpack():
    pass
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
                print(Fore.RED+f'ERROR: read: Received {lurk_type}, signaling a client disconnect, returning None!')
                return None
            lurk_type, = struct.unpack('<B', lurk_type)
        except struct.error:
            print(Fore.RED+'ERROR: read: Failed to unpack lurk_type!')
            continue
        if lurk_type < 1 or lurk_type > 14:
            print(Fore.RED+f'ERROR: read: {lurk_type} not a valid lurk message type!')
            continue
        if lurk_type == MESSAGE:
            print(f'DEBUG: read: Handling potential MESSAGE type {lurk_type}')
            try:
                lurk_header = recv(skt, MESSAGE_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: readAll returned None, signaling socket disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential MESSAGE header: {lurk_header}')
                msg_len, recipient_name, sender_name = struct.unpack('<H32s32s', lurk_header)
                lurk_data = recv(skt, msg_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: readAll returned None, signaling socket disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential MESSAGE data: {lurk_data}')
                message, = struct.unpack(f'<{msg_len}s', lurk_data)
                return (lurk_type, msg_len, recipient_name.decode('utf-8'), sender_name.decode('utf-8'), message.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack MESSAGE!')
                continue
        elif lurk_type == CHANGEROOM:
            print(f'DEBUG: read: Handling potential CHANGEROOM type {lurk_type}')
            try:
                lurk_header = recv(skt, CHANGEROOM_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential CHANGEROOM header: {lurk_header}')
                room_num, = struct.unpack('<H', lurk_header)
                return (lurk_type, room_num)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack CHANGEROOM!')
                continue
        elif lurk_type == FIGHT:
            print(f'DEBUG: read: Handling potential FIGHT type {lurk_type}')
            return (lurk_type,)
        elif lurk_type == PVPFIGHT:
            print(f'DEBUG: read: Handling potential PVPFIGHT type {lurk_type}')
            try:
                lurk_header = recv(skt, PVPFIGHT_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential PVPFIGHT header: {lurk_header}')
                character_name = struct.unpack('<32s', lurk_header)
                return (lurk_type, character_name.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack PVPFIGHT!')
                continue
        elif lurk_type == LOOT:
            print(f'DEBUG: read: Handling potential LOOT type {lurk_type}')
            try:
                lurk_header = recv(skt, LOOT_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential LOOT header: {lurk_header}')
                character_name = struct.unpack('<32s', lurk_header)
                return (lurk_type, character_name.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack LOOT!')
                continue
        elif lurk_type == START:
            print(f'DEBUG: read: Handling potential START type {lurk_type}')
            return (lurk_type,)
        elif lurk_type == ERROR:
            print(f'DEBUG: read: Handling potential ERROR type {lurk_type}')
            try:
                lurk_header = recv(skt, ERROR_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential ERROR header: {lurk_header}')
                error_code, error_msg_len = struct.unpack('<BH', lurk_header)
                lurk_data = recv(skt, error_msg_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential ERROR data: {lurk_data}')
                error_msg, = struct.unpack(f'<{error_msg_len}s', lurk_data)
                return (lurk_type, error_code, error_msg_len, error_msg.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack ERROR!')
                continue
        elif lurk_type == ACCEPT:
            print(f'DEBUG: read: Handling potential ACCEPT type {lurk_type}')
            try:
                lurk_header = recv(skt, ACCEPT_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential ACCEPT header: {lurk_header}')
                accepted_msg, = struct.unpack('<B', lurk_header)
                return (lurk_type, accepted_msg)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack ACCEPT!')
                continue
        elif lurk_type == ROOM:
            print(f'DEBUG: read: Handling potential ROOM type {lurk_type}')
            try:
                lurk_header = recv(skt, ROOM_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential ROOM header: {lurk_header}')
                room_num, room_name, room_des_len = struct.unpack('<H32sH', lurk_header)
                lurk_data = recv(skt, room_des_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential ROOM data: {lurk_data}')
                room_des, = struct.unpack(f'<{room_des_len}s', lurk_data)
                return (lurk_type, room_num, room_name.decode('utf-8'), room_des_len, room_des.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack ROOM!')
                continue
        elif lurk_type == CHARACTER:
            print(f'DEBUG: read: Handling potential CHARACTER type {lurk_type}')
            try:
                lurk_header = recv(skt, CHARACTER_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential CHARACTER header: {lurk_header}')
                name, flags, attack, defense, regen, health, gold, room, char_des_len = struct.unpack('<32sB3Hh3H', lurk_header)
                lurk_data = recv(skt, char_des_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential CHARACTER data: {lurk_data}')
                char_des, = struct.unpack(f'<{char_des_len}s', lurk_data)
                return (CHARACTER, name.decode('utf-16'), flags, attack, defense, regen, health, gold, room, char_des_len, char_des.decode('utf-16'))     # Issue here with lurktest -t; cannot decode 0xff with utf-8?
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack CHARACTER!')
                continue
        elif lurk_type == GAME:
            print(f'DEBUG: read: Handling potential GAME type {lurk_type}')
            try:
                lurk_header = recv(skt, GAME_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential GAME header: {lurk_header}')
                init_points, stat_limit, game_des_len = struct.unpack('<3H', lurk_header)
                lurk_data = recv(skt, game_des_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential GAME data: {lurk_data}')
                game_des, = struct.unpack(f'<{game_des_len}s', lurk_data)
                return (lurk_type, init_points, stat_limit, game_des_len, game_des.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack GAME!')
                continue
        elif lurk_type == LEAVE:
            print(f'DEBUG: read: Handling potential LEAVE type {lurk_type}')
            return (lurk_type,)
        elif lurk_type == CONNECTION:
            print(f'DEBUG: read: Handling potential CONNECTION type {lurk_type}')
            try:
                lurk_header = recv(skt, CONNECTION_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential CONNECTION header: {lurk_header}')
                room_num, room_name, room_des_len = struct.unpack('<H32sH', lurk_header)
                lurk_data = recv(skt, room_des_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential CONNECTION data: {lurk_data}')
                room_des = struct.unpack(f'<{room_des_len}s', lurk_data)
                return (lurk_type, room_num, room_name.decode('utf-8'), room_des_len, room_des.decode('utf-8'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack CONNECTION header!')
                continue
        elif lurk_type == VERSION:
            print(f'DEBUG: read: Handling potential VERSION type {lurk_type}')
            try:
                lurk_header = recv(skt, VERSION_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: Received b'', signaling a client disconnect, returning None!')
                    return None
                print(f'DEBUG: read: Potential VERSION header: {lurk_header}')
                major, minor, extension_len = struct.unpack('<2BH', lurk_header)
                return (lurk_type, major, minor, extension_len)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack VERSION header!')
                continue
        else:
            print(Fore.RED+f'ERROR: read: Invalid message type {lurk_type}, continuing!')
            continue
def sendMessage(skt, lurk_message):
    """Sends a Lurk MESSAGE message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk MESSAGE message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack(f'<BH32s30sH{lurk_message[1]}s', lurk_message[0], lurk_message[1], lurk_message[2], lurk_message[3], lurk_message[4], lurk_message[5])
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
def sendChangeroom(skt, lurk_message):
    """Sends a Lurk CHANGEROOM message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk CHANGEROOM message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack('<BH', lurk_message[0], lurk_message[1])
        print('DEBUG: Sending CHANGEROOM message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
def sendFight(skt):
    """Sends a Lurk FIGHT message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk FIGHT message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack('<B', FIGHT)
        print('DEBUG: Sending FIGHT message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {FIGHT}')
        raise struct.error from exc
    return 0
def sendPvpfight(skt, lurk_message):
    """Sends a Lurk PVPFIGHT message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk PVPFIGHT message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack('<B32s', lurk_message[0], lurk_message[1])
        print('DEBUG: Sending PVPFIGHT message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
def sendLoot(skt, lurk_message):
    """Sends a Lurk LOOT message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk LOOT message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack('<B32s', lurk_message[0], lurk_message[1])
        print('DEBUG: Sending LOOT message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
def sendStart(skt):
    """Sends a Lurk START message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk START message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack('<B', START)
        print('DEBUG: Sending START message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {START}')
        raise struct.error from exc
    return 0
def sendError(skt, lurk_message):
    """Sends a Lurk ERROR message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk ERROR message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack(f'<2BH{lurk_message[2]}s', lurk_message[0], lurk_message[1], lurk_message[2], bytes(lurk_message[3], 'utf-8'))
        print('DEBUG: Sending ERROR message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
def sendAccept(skt, lurk_message):
    """Sends a Lurk ACCEPT message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk VERSION message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack('<2B', ACCEPT, lurk_message)
        print('DEBUG: Sending ACCEPT message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {MESSAGE}')
        raise struct.error from exc
    return 0
def sendRoom(skt, lurk_message):
    """Sends a Lurk ROOM message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk ROOM message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack(f'<BH32sH{lurk_message[3]}s', lurk_message[0], lurk_message[1], lurk_message[2], lurk_message[3], bytes(lurk_message[4], 'utf-8'))
        print('DEBUG: Sending ROOM message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
def sendCharacter(skt, lurk_message):
    """Sends a Lurk CHARACTER message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk CHARACTER message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack(f'<B32sB3Hh3H{lurk_message[9]}s', lurk_message[0], lurk_message[1].encode(), lurk_message[2], lurk_message[3], lurk_message[4], lurk_message[5], lurk_message[6], lurk_message[7], lurk_message[8], lurk_message[9], lurk_message[10].encode())
        print('DEBUG: Sending CHARACTER message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
def sendGame(skt, lurk_message):
    """Sends a Lurk GAME message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk GAME message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack(f'<B3H{lurk_message[3]}s', lurk_message[0], lurk_message[1], lurk_message[2], lurk_message[3], bytes(lurk_message[4], 'utf-8'))
        print('DEBUG: Sending GAME message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
def sendLeave(skt):
    """Sends a Lurk LEAVE message to a specified socket.

    Args:
        skt (socket): Socket to send data to.

    Raises:
        struct.error: Raised if packing message failed.

    Returns:
        int: 0 if function finishes successfully
    """
    try:
        packed = struct.pack('<B', LEAVE)
        print('DEBUG: Sending LEAVE message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {LEAVE}')
        raise struct.error from exc
    return 0
def sendConnection(skt, lurk_message):
    """Sends a Lurk CONNECTION message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk CONNECTION message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        int: 0 if function finishes successfully
    """
    try:
        packed = struct.pack(f'<BH32sH{lurk_message[3]}s', lurk_message[0], lurk_message[1], lurk_message[2], lurk_message[3], lurk_message[4])
        print('DEBUG: Sending CONNECTION message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
def sendVersion(skt, lurk_message):
    """Sends a Lurk VERSION message to a specified socket.

    Args:
        skt (socket): Socket to send data to.
        lurk_message (tuple): Entire Lurk VERSION message to be sent.

    Raises:
        struct.error: Raised if passed tuple does not meet Lurk protocol standards for this message type.

    Returns:
        _type_: _description_
    """
    try:
        packed = struct.pack('<3BH', lurk_message[0], lurk_message[1], lurk_message[2], lurk_message[3])
        print('DEBUG: Sending VERSION message!')
        send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk_message[0]}')
        raise struct.error from exc
    return 0
