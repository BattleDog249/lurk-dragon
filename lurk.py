"""LURK protocol-related variables and functions that can be used in a client or server.
"""
#!/usr/bin/env python3

from ctypes import *
import socket
import struct
from dataclasses import dataclass

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

ALIVE = 0x80
JOIN_BATTLE = 0x40
MONSTER = 0x20
STARTED = 0x10
READY = 0x08

@dataclass
class Character:
    """"""
    uuid: str
    name: str
    flag: c_uint8
    attack: c_uint16
    defense: c_uint16
    regen: c_uint16
    health: c_int16
    gold: c_uint16
    room: c_uint16
    description_len: c_uint16
    description: str
    # Key (UUID): UUID, Value (list): [name, flag, attack, defense, regen, health, gold, room, description_len, description]
    characters = {}
    def get_characters_with_name(name):
        """"""
        characters = [(character) for character in Character.characters.values() if character[0] == name]
        print(f'DEBUG: Character(s) found with name {name}: {characters}')
        return characters
        
    def get_characters_with_room(room):
        """"""
        characters = [(character) for character in Character.characters.values() if character[7] == room]
        print(f'DEBUG: Character(s) found in room {room}: {characters}')
        return characters

@dataclass
class Player:
    """"""
    name: str
    flag: c_uint8
    attack: c_uint16
    defense: c_uint16
    regen: c_uint16
    health: c_int16
    gold: c_uint16
    room: c_uint16
    description_len: c_uint16
    description: str
    # Key (str): name, Value (list): [flag, attack, defense, regen, health, gold, room, description_len, description]
    players = {}
    def get_player_with_name(name):
        """"""
        if name in Player.players:
            print(Fore.GREEN+f'INFO: Requested player {name} found, returning player!')
            return (name, Player.players[name][0], Player.players[name][1], Player.players[name][2], Player.players[name][3], Player.players[name][4], Player.players[name][5], Player.players[name][6], Player.players[name][7], Player.players[name][8])
        else:
            print(Fore.YELLOW+f'WARN: Requested player {name} not found, returning None!')
            print(Fore.YELLOW+f'INFO: Current list of players: {Player.players}')
            return None
    def get_players_with_room(room):
        """"""
        players = [(name, info) for name, info in Player.players.items() if Player.players[name][7] == room]
        print(Fore.WHITE+f'INFO: Players(s) found in room {room}: {players}')
        return players

@dataclass
class Room:
    """"""
    room_number: c_uint16
    room_name: str
    room_description_len: c_uint16
    room_description: str
    connection_number: c_uint16
    connection_name: str
    connection_description_len: c_uint16
    connection_description: str
    # Key (int): room_number, Value (tuple): (room_name, room_description)
    rooms = {}
    # Key (int): connection_number (==room_number), Value (list of tuples): [(room_number, )]
    connections = {}
    def get_room(room_number):
        """"""
        rooms = [(room_number, room_info) for room_number, room_info in Room.rooms.items() if Room.rooms[room_number] == room_number]
        print(f'DEBUG: Room(s) found with number {room_number}: {rooms}')
        return rooms
    def get_connections(room_number):
        """"""
        connections = [(room_number, room_info) for room_number, room_info in Room.rooms.items() if Room.rooms[room_number] == room_number]

def recv(skt, size):
    """Receive size amount of bytes from a socket, returning full lurk message

    Args:
        skt (socket): Socket to receive from.
        size (int): Size of message to receive from socket buffer.

    Returns:
        bytearray: Raw data received from socket. Will not return partial messages.
        None: Connection broken.
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
        print(Fore.WHITE+f'DEBUG: send: Sent message type {message[0]}!')
        return 0
    except socket.error:
        print(Fore.RED+'ERROR: send: socket.error, returning None!')
        return None
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
                print(Fore.RED+'ERROR: read: socket.error, returning None!')
                return None
            lurk_type, = struct.unpack('<B', lurk_type)
        except struct.error:
            print(Fore.RED+'ERROR: read: Failed to unpack lurk_type!')
            continue
        if lurk_type < 1 or lurk_type > 14:
            print(Fore.RED+f'ERROR: read: {lurk_type} not a valid lurk message type!')
            continue
        print(Fore.WHITE+f'DEBUG: read: Received potential lurk type {lurk_type}')
        if lurk_type == MESSAGE:
            try:
                lurk_header = recv(skt, MESSAGE_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: recvall: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                msg_len, recipient_name, sender_name = struct.unpack('<H32s32s', lurk_header)
                lurk_data = recv(skt, msg_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: recvall: socket.error, returning None!')
                    return None
                #print(Fore.WHITE+f'DEBUG: read: lurk_data: {lurk_data}')
                message, = struct.unpack(f'<{msg_len}s', lurk_data)
                return (MESSAGE, msg_len, recipient_name.decode('utf-8', 'ignore'),
                        sender_name.decode('utf-8', 'ignore'), message.decode('utf-8', 'ignore'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == CHANGEROOM:
            try:
                lurk_header = recv(skt, CHANGEROOM_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: recvall: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                room_num, = struct.unpack('<H', lurk_header)
                return (CHANGEROOM, room_num)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == FIGHT:
            return (FIGHT,)
        elif lurk_type == PVPFIGHT:
            try:
                lurk_header = recv(skt, PVPFIGHT_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                character_name, = struct.unpack('<32s', lurk_header)
                return (PVPFIGHT, character_name)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == LOOT:
            try:
                lurk_header = recv(skt, LOOT_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                character_name, = struct.unpack('<32s', lurk_header)
                return (LOOT, character_name.decode('utf-8', 'ignore'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == START:
            return (START,)
        elif lurk_type == ERROR:
            try:
                lurk_header = recv(skt, ERROR_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                error_code, error_msg_len = struct.unpack('<BH', lurk_header)
                lurk_data = recv(skt, error_msg_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_data: {lurk_data}')
                error_msg, = struct.unpack(f'<{error_msg_len}s', lurk_data)
                return (ERROR, error_code, error_msg_len, error_msg.decode('utf-8', 'ignore'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == ACCEPT:
            try:
                lurk_header = recv(skt, ACCEPT_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                accepted_msg, = struct.unpack('<B', lurk_header)
                return (ACCEPT, accepted_msg)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == ROOM:
            try:
                lurk_header = recv(skt, ROOM_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                room_num, room_name, room_des_len = struct.unpack('<H32sH', lurk_header)
                lurk_data = recv(skt, room_des_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(f'DEBUG: read: Potential ROOM data: {lurk_data}')
                room_des, = struct.unpack(f'<{room_des_len}s', lurk_data)
                return (ROOM, room_num, room_name.decode('utf-8', 'ignore'),
                        room_des_len, room_des.decode('utf-8', 'ignore'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == CHARACTER:
            try:
                lurk_header = recv(skt, CHARACTER_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                name, flags, attack, defense, regen, health, gold, room, char_des_len = struct.unpack('<32sB3Hh3H', lurk_header)
                lurk_data = recv(skt, char_des_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_data: {lurk_data}')
                char_des, = struct.unpack(f'<{char_des_len}s', lurk_data)
                name = name.replace(b'\x00', b'')   # I think this fixed stuff? Weird..
                return (CHARACTER, name.decode('utf-8', 'ignore'), flags, attack, defense, regen,
                        health, gold, room, char_des_len, char_des.decode('utf-8', 'ignore'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == GAME:
            try:
                lurk_header = recv(skt, GAME_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                init_points, stat_limit, game_des_len = struct.unpack('<3H', lurk_header)
                lurk_data = recv(skt, game_des_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_data: {lurk_data}')
                game_des, = struct.unpack(f'<{game_des_len}s', lurk_data)
                return (GAME, init_points, stat_limit,
                        game_des_len, game_des.decode('utf-8', 'ignore'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == LEAVE:
            return (LEAVE,)
        elif lurk_type == CONNECTION:
            try:
                lurk_header = recv(skt, CONNECTION_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                room_num, room_name, room_des_len = struct.unpack('<H32sH', lurk_header)
                lurk_data = recv(skt, room_des_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_data: {lurk_data}')
                room_des, = struct.unpack(f'<{room_des_len}s', lurk_data)
                return (CONNECTION, room_num, room_name.decode('utf-8', 'ignore'),
                        room_des_len, room_des.decode('utf-8', 'ignore'))
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        elif lurk_type == VERSION:
            try:
                lurk_header = recv(skt, VERSION_LEN - 1)
                if not lurk_header:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_header: {lurk_header}')
                major, minor, extension_len = struct.unpack('<2BH', lurk_header)
                return (VERSION, major, minor, extension_len)
            except struct.error:
                print(Fore.RED+'ERROR: read: Failed to unpack lurk_header/data!')
                continue
        else:
            print(Fore.RED+f'ERROR: read: Invalid message type {lurk_type}, continuing!')
            continue
def write(skt, lurk_message):
    """Pack and send an entire lurk message to a specified socket.

    Args:
        skt (socket): Socket to send lurk_message to.
        lurk_message (tuple): Entire lurk protocol compliant message.
        If message is not compliant, send message anyway for debugging.

    Raises:
        struct.error: Raised if an error occurs in packing the message.

    Returns:
        None: Passed if socket.error occurred in nested send function.
        0: Finished sending lurk_message successfully.
    """
    if lurk_message[0] == MESSAGE:
        try:
            packed = struct.pack(f'<BH32s32s{lurk_message[1]}s', MESSAGE, lurk_message[1], bytes(lurk_message[2], 'utf-8'), bytes(lurk_message[3], 'utf-8'), bytes(lurk_message[4], 'utf-8'))
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {MESSAGE}')
            raise struct.error from exc
    elif lurk_message[0] == CHANGEROOM:
        try:
            packed = struct.pack('<BH', CHANGEROOM, lurk_message[1])
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {CHANGEROOM}')
            raise struct.error from exc
    elif lurk_message[0] == FIGHT:
        try:
            packed = struct.pack('<B', FIGHT)
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {FIGHT}')
            raise struct.error from exc
    elif lurk_message[0] == PVPFIGHT:
        try:
            packed = struct.pack('<B32s', PVPFIGHT, lurk_message[1])
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {PVPFIGHT}')
            raise struct.error from exc
    elif lurk_message[0] == LOOT:
        try:
            packed = struct.pack('<B32s', LOOT, lurk_message[1])
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {LOOT}')
            raise struct.error from exc
    elif lurk_message[0] == START:
        try:
            packed = struct.pack('<B', START)
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {START}')
            raise struct.error from exc
    elif lurk_message[0] == ERROR:
        try:
            packed = struct.pack(f'<2BH{lurk_message[2]}s', ERROR, lurk_message[1], lurk_message[2], bytes(lurk_message[3], 'utf-8'))
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {ERROR}')
            raise struct.error from exc
    elif lurk_message[0] == ACCEPT:
        try:
            packed = struct.pack('<2B', ACCEPT, lurk_message[1])
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {ACCEPT}')
            raise struct.error from exc
    elif lurk_message[0] == ROOM:
        try:
            packed = struct.pack(f'<BH32sH{lurk_message[3]}s', ROOM, lurk_message[1], bytes(lurk_message[2], 'utf-8'), lurk_message[3], bytes(lurk_message[4], 'utf-8'))
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {ROOM}')
            raise struct.error from exc
    elif lurk_message[0] == CHARACTER:
        try:
            packed = struct.pack(f'<B32sB3Hh3H{lurk_message[9]}s', CHARACTER, lurk_message[1].encode(), lurk_message[2], lurk_message[3], lurk_message[4], lurk_message[5], lurk_message[6], lurk_message[7], lurk_message[8], lurk_message[9], lurk_message[10].encode())
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {CHARACTER}')
            raise struct.error from exc
    elif lurk_message[0] == GAME:
        try:
            packed = struct.pack(f'<B3H{lurk_message[3]}s', GAME, lurk_message[1], lurk_message[2], lurk_message[3], bytes(lurk_message[4], 'utf-8'))
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {GAME}')
            raise struct.error from exc
    elif lurk_message[0] == LEAVE:
        try:
            packed = struct.pack('<B', LEAVE)
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {LEAVE}')
            raise struct.error from exc
    elif lurk_message[0] == CONNECTION:
        try:
            packed = struct.pack(f'<BH32sH{lurk_message[3]}s', CONNECTION, lurk_message[1], bytes(lurk_message[2], 'utf-8'), lurk_message[3], bytes(lurk_message[4], 'utf-8'))
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {CONNECTION}')
            raise struct.error from exc
    elif lurk_message[0] == VERSION:
        try:
            packed = struct.pack('<3BH', VERSION, lurk_message[1], lurk_message[2], lurk_message[3])
            status = send(skt, packed)
            if status != 0:
                print(Fore.RED+'ERROR: write: socket.error, returning None!')
                return None
        except Exception as exc:
            print(Fore.RED+f'ERROR: write: Failed to pack message type {VERSION}')
            raise struct.error from exc
    else:
        print(Fore.YELLOW+f'WARN: write: Invalid message passed to write: {lurk_message}')
        print(Fore.RED+f'WARN: write: Sending invalid message to socket, hope you are debugging!')
        status = send(skt, lurk_message)
        if status != 0:
            print(Fore.RED+'ERROR: write: socket.error, returning None!')
            return None
    return 0
