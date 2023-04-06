"""LURK protocol-related variables and functions that can be used in a client or server."""
#!/usr/bin/env python3

import socket
import struct

from ctypes import c_uint8, c_uint16, c_int16
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

ALIVE = 0b10000000
JOIN_BATTLE = 0b01000000
MONSTER = 0b00100000
STARTED = 0b00010000
READY = 0b00001000

@dataclass
class Message:
    """A class that represents a message in the game. This class is used to store information about a message, and to retrieve information about a message."""
    message_len: c_uint16
    recipient: str
    sender: str
    message: str
    def recv_message(skt):
        """"""
        pass
    def send_message(skt, message):
        """"""
        pass

@dataclass
class Changeroom:
    """A class that represents a changeroom message in the game. This class is used to store information about a changeroom message, and to retrieve information about a changeroom message."""
    target_room: c_uint16
    lurk_type: c_uint8 = CHANGEROOM
    def recv_changeroom(skt):
        """"""
        pass
    def send_changeroom(skt, changeroom):
        """"""
        pass

@dataclass
class Fight:
    """A class that represents a fight message in the game. This class is used to store information about a fight message, and to retrieve information about a fight message."""
    lurk_type: c_uint8 = FIGHT
    def recv_fight(skt):
        """"""
        pass
    def send_fight(skt):
        """"""
        pass

@dataclass
class Pvpfight:
    """A class that represents a pvpfight message in the game. This class is used to store information about a pvpfight message, and to retrieve information about a pvpfight message."""
    target_name: str
    lurk_type: c_uint8 = PVPFIGHT
    def recv_pvpfight(skt):
        """"""
        pass
    def send_pvpfight(skt, pvpfight):
        """"""
        pass

@dataclass
class Loot:
    """A class that represents a loot message in the game. This class is used to store information about a loot message, and to retrieve information about a loot message."""
    target_name: str
    lurk_type: c_uint8 = LOOT
    def recv_loot(skt):
        """Receives a loot message from the given socket, and unpacks it into a loot object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        loot_header = recv(skt, LOOT_LEN - 1)
        if not loot_header:
            print(Fore.RED+"ERROR: recv_loot: Socket connection broken, returning None!")
            return None
        try:
            target_name, = struct.unpack('<32s', loot_header)
        except struct.error:
            raise struct.error("Failed to unpack loot_header!")
        loot = Loot(target_name=target_name.decode())
        return loot
    def send_loot(skt, loot):
        """"""
        pass

@dataclass
class Start:
    """A class that represents a start message in the game. This class is used to store information about a start message, and to retrieve information about a start message."""
    lurk_type: c_uint8 = START
    def send_start(skt):
        """Packs a start message into bytes and sends it to the given socket object."""
        if not isinstance(skt, socket.socket):
            raise TypeError('skt must be a socket object!')
        start = Start()
        packed = struct.pack(f'<B', start.lurk_type)
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(Fore.RED+f'ERROR: send_start: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!')
            return None
        print(Fore.WHITE+f'DEBUG: send_start: Sent {bytes_sent} byte START!')
        return bytes_sent

@dataclass
class Error:
    """A class that represents an error message in the game. This class is used to store information about an error, and to retrieve information about an error."""
    number: c_uint8
    description_len: c_uint16
    description: str
    lurk_type: c_uint8 = ERROR
    errors = {}
    def recv_error(skt):
        """Receives an error message from the given socket, and unpacks it into a error object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        error_header = recv(skt, ERROR_LEN - 1)
        if not error_header:
            print(Fore.RED+"ERROR: recv_error: Socket connection broken, returning None!")
            return None
        try:
            number, description_len = struct.unpack('<BH', error_header)
        except struct.error:
            raise struct.error("Failed to unpack error_header!")
        room_data = recv(skt, description_len)
        if not room_data:
            print(Fore.RED+"ERROR: recv_error: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', room_data)
        except struct.error:
            raise struct.error("Failed to unpack error_data!")
        error = Error(number=number, description_len=description_len, description=description.decode())
        return error
    def send_error(skt, code):
        """Retrieves the error message with the given code from the errors dictionary, packs it into bytes, and sends it to the given socket object."""
        if not isinstance(skt, socket.socket):
            raise TypeError('skt must be a socket object!')
        if not isinstance(code, int):
            raise TypeError('code must be an int object!')
        if code not in Error.errors:
            raise ValueError('code must be a valid error code!')
        error = Error(number=code, description_len=Error.errors[code][0], description=Error.errors[code][1])
        packed = struct.pack(f'<B3H{error.description_len}s', error.lurk_type, error.number, error.description_len, error.description.encode())
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(Fore.RED+f"ERROR: send_error: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(Fore.WHITE+f'DEBUG: send_error: Sent {bytes_sent} byte ERROR!')
        return bytes_sent
@dataclass
class Accept:
    """A class that represents an accept message in the game. This class is used to store information about an accept message, and to retrieve information about an accept message."""
    accept_type: c_uint8
    lurk_type: c_uint8 = ACCEPT
    def recv_accept():
        """"""
        pass
    def send_accept(skt, code):
        """Packs an accept message with the given code that corresponds to the accepted lurk type into bytes and sends it to the given socket object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("skt must be a socket object!")
        if not isinstance(code, int):
            raise TypeError("code must be an int object!")
        accept = Accept(accept_type=code)
        packed = struct.pack(f'<2B', accept.lurk_type, accept.accept_type)
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(Fore.RED+f"ERROR: send_accept: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(Fore.WHITE+f'DEBUG: send_accept: Sent {bytes_sent} byte ACCEPT!')
        return bytes_sent

@dataclass
class Room:
    """A class that represents a room in the game. This class is used to store information about a room, and to retrieve information about a room."""
    number: c_uint16
    name: str
    description_len: c_uint16
    description: str
    lurk_type: c_uint8 = ROOM
    # Key (int): number, Value (tuple): (name, description_len, description)
    rooms = {}
    def update_room(room):
        """Updates the room with the given room object in the rooms dictionary, or adds it if it doesn't exist."""
        Room.rooms.update({room.number: [room.name, room.description_len, room.description]})
    def get_room(number):
        """Returns a room with the given number. If the room is not found, returns None."""
        room = [(room_number, room_info) for room_number, room_info in Room.rooms.items() if number in Room.rooms and number == room_number]
        room = Room(number=room[0][0], name=room[0][1][0], description_len=room[0][1][1], description=room[0][1][2])
        return room
    def recv_room(skt):
        """Receives a room message from the given socket, and unpacks it into a room object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        room_header = recv(skt, ROOM_LEN - 1)
        if not room_header:
            print(Fore.RED+"ERROR: recv_room: Socket connection broken, returning None!")
            return None
        try:
            number, name, description_len = struct.unpack('<H32sH', room_header)
        except struct.error:
            raise struct.error("Failed to unpack room_header!")
        room_data = recv(skt, description_len)
        if not room_data:
            print(Fore.RED+"ERROR: recv_room: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', room_data)
        except struct.error:
            raise struct.error("Failed to unpack room_data!")
        room = Room(number=number, name=name.decode(), description_len=description_len, description=description.decode())
        return room
    def send_room(skt, room):
        """Packs a room message into bytes with the given room object and sends it to the given socket object. Returns the number of bytes sent, or None if the socket connection is broken. Raises a TypeError if the skt parameter is not a socket object, or if the room parameter is not a Room object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        if not isinstance(room, Room):
            raise TypeError("Provided room parameter must be a Game object!")
        packed = struct.pack(f'<BH32sH{room.description_len}s', room.lurk_type, room.number, room.name.encode(), room.description_len, room.description.encode())
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(Fore.RED+f"ERROR: send_room: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(Fore.WHITE+f'DEBUG: send_room: Sent {bytes_sent} byte ROOM!')
        return bytes_sent

@dataclass
class Character:
    """A class that represents a character in the game. This class is used to store information about a character, and to retrieve information about a character."""
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
    lurk_type: c_uint8 = 10
    struct_format: str = '<32sB3Hh3H'
    # Key (str): name, Value (list): [flag, attack, defense, regen, health, gold, room, description_len, description]
    characters = {}
    def get_character_with_name(target_name):
        """Returns a character with the given name. If the character is not found, returns None."""
        character = [(name, stat) for name, stat in Character.characters.items() if name in Character.characters and target_name == name]
        character = Character(name=character[0][0], flag=character[0][1][0], attack=character[0][1][1], defense=character[0][1][2], regen=character[0][1][3], health=character[0][1][4], gold=character[0][1][5], room=character[0][1][6], description_len=character[0][1][7], description=character[0][1][8])
        return character
    def get_characters_with_room(room):
        """Returns a list of character objects that are in the given room. If no characters are found, returns an empty list."""
        characters_with_room = [(name, stat) for name, stat in Character.characters.items() if Character.characters[name][6] == room]
        characters = []
        for character in characters_with_room:
            character_with_room = Character(name=character[0], flag=character[1][0], attack=character[1][1], defense=character[1][2], regen=character[1][3], health=character[1][4], gold=character[1][5], room=character[1][6], description_len=character[1][7], description=character[1][8])
            characters.append(character_with_room)
        return characters
    def update_character(character):
        """Updates the character with the given character object in the characters dictionary, or adds it if it doesn't exist."""
        Character.characters.update({character.name: [character.flag, character.attack, character.defense, character.regen, character.health, character.gold, character.room, character.description_len, character.description]})
    def recv_character(skt):
        """Receives a character message from the given socket, and unpacks it into a character object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        character_header = recv(skt, CHARACTER_LEN - 1)
        if not character_header:
            print(Fore.RED+"ERROR: recv_character: Socket connection broken, returning None!")
            return None
        try:
            name, flag, attack, defense, regen, health, gold, room, description_len = struct.unpack(Character.struct_format, character_header)
        except struct.error:
            raise struct.error("Failed to unpack character_header!")
        character_data = recv(skt, description_len)
        if not character_data:
            print(Fore.RED+"ERROR: recv_character: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', character_data)
        except struct.error:
            raise struct.error("Failed to unpack character_data!")
        name = name.replace(b'\x00', b'')   # I think this fixed stuff? Weird..
        character = Character(name=name.decode('utf-8', 'ignore'), flag=flag, attack=attack, defense=defense, regen=regen, health=health, gold=gold, room=room, description_len=description_len, description=description.decode('utf-8', 'ignore'))
        return character
    def send_character(skt, character):
        """Packs a character message into bytes with the given character object and sends it to the given socket object. Returns the number of bytes sent, or None if the socket connection is broken. Raises a TypeError if the skt parameter is not a socket object, or if the character parameter is not a Character object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        if not isinstance(character, Character):
            raise TypeError("Provided character parameter must be a Character object!")
        packed = struct.pack(f'<B32sB3Hh3H{character.description_len}s', character.lurk_type, character.name.encode(), character.flag, character.attack, character.defense, character.regen, character.health, character.gold, character.room, character.description_len, character.description.encode())
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(Fore.RED+f"ERROR: send_character: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(Fore.WHITE+f'DEBUG: send_character: Sent {bytes_sent} byte CHARACTER!')
        return bytes_sent

@dataclass
class Game:
    """A class that represents a game in the game. This class is used to store information about a game, and to retrieve information about a game."""
    initial_points: c_uint16
    stat_limit: c_uint16
    description_len: c_uint16
    description: str
    lurk_type: c_uint8 = 11
    def recv_game(skt):
        """Receives a game message from the given socket, and unpacks it into a game object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        game_header = recv(skt, CONNECTION_LEN - 1)
        if not game_header:
            print(Fore.RED+"ERROR: recv_game: Socket connection broken, returning None!")
            return None
        try:
            init_points, stat_limit, description_len = struct.unpack('<3H', game_header)
        except struct.error:
            raise struct.error("Failed to unpack game_header!")
        game_data = recv(skt, description_len)
        if not game_data:
            print(Fore.RED+"ERROR: recv_game: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', game_data)
        except struct.error:
            raise struct.error("Failed to unpack game_data!")
        game = Game(init_points=init_points,stat_limit=stat_limit, description_len=description_len, description=description.decode('utf-8', 'ignore'))
        return game
    def send_game(skt, game):
        """Packs a game message into bytes with the given game object and sends it to the given socket object. Returns the number of bytes sent, or None if the socket connection is broken. Raises a TypeError if the skt parameter is not a socket object, or if the game parameter is not a Game object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        if not isinstance(game, Game):
            raise TypeError("Provided game parameter must be a Game object!")
        packed = struct.pack(f'<B3H{game.description_len}s', game.lurk_type, game.initial_points, game.stat_limit, game.description_len, game.description.encode())
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(Fore.RED+f"ERROR: send_game: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(Fore.WHITE+f'DEBUG: send_game: Sent {bytes_sent} byte GAME!')
        return bytes_sent

@dataclass
class Leave:
    """A class that represents a leave in the game. This class is used to store information about a leave, and to retrieve information about a leave."""
    lurk_type: c_uint8 = LEAVE
    struct_format: str = '<B'
    def send_leave(skt):
        """Packs a leave message into bytes and sends it to the given socket object. Returns the number of bytes sent, or None if the socket connection is broken. Raises a TypeError if the skt parameter is not a socket object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        packed = struct.pack(Leave.struct_format, Leave.lurk_type)
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(Fore.RED+f"ERROR: send_leave: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(Fore.WHITE+f'DEBUG: send_leave: Sent {bytes_sent} byte LEAVE!')
        return bytes_sent

@dataclass
class Connection:
    """A class that represents a connection in the game. This class is used to store information about a connection, and to retrieve information about a connection."""
    number: c_uint16
    name: str
    description_len: c_uint16
    description: str
    lurk_type: c_uint8 = CONNECTION
    # Key (int): number (==room_number), Value (list of tuples): [(room_number, )]
    connections = {}
    def get_connection(number):
        """Returns a connection with the given number. If the connection is not found, returns None."""
        connection = [(room_number, connection_info) for room_number, connection_info in Connection.connections.items() if number in Connection.connections and Connection.connections[number] == number]
        connection = Connection(number=connection[0], name=connection[0][0], description_len=connection[0][1], description=connection[0][2])
        print(f'DEBUG: Connection(s) found with number {number}: {connection}')
        return connection
    def recv_connection(skt):
        """Receives a connection message from the given socket, and unpacks it into a connection object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        connection_header = recv(skt, CONNECTION_LEN - 1)
        if not connection_header:
            print(Fore.RED+"ERROR: recv_connection: Socket connection broken, returning None!")
            return None
        try:
            number, name, description_len = struct.unpack('<H32sH', connection_header)
        except struct.error:
            raise struct.error("Failed to unpack connection_header!")
        connection_data = recv(skt, description_len)
        if not connection_data:
            print(Fore.RED+"ERROR: recv_connection: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', connection_data)
        except struct.error:
            raise struct.error("Failed to unpack connection_data!")
        connection = Connection(number=number, name=name.decode('utf-8', 'ignore'), description_len=description_len, description=description.decode('utf-8', 'ignore'))
        return connection
    def send_connection(skt, connection):
        """Packs a connection message into bytes with the given connection object and sends it to the given socket object. Returns the number of bytes sent, or None if the socket connection is broken. Raises a TypeError if the skt parameter is not a socket object, or if the connection parameter is not a Connection object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        if not isinstance(connection, Connection):
            raise TypeError("Provided connection parameter must be a Connection object!")
        packed = struct.pack(f'<BH32sH{connection.description_len}s', connection.lurk_type,  connection.number, connection.name.encode(), connection.description_len, connection.description.encode())
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(Fore.RED+f"ERROR: send_connection: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(Fore.WHITE+f'DEBUG: send_connection: Sent {bytes_sent} byte CONNECTION!')
        return bytes_sent

@dataclass
class Version:
    """A class that represents a Lurk version message. This class is used to send and receive version messages."""
    major: c_uint8
    minor: c_uint8
    extensions_len: c_uint16 = 0
    extensions: str = ''
    lurk_type: c_uint8 = VERSION
    struct_format: str = '<2BH'
    def recv_version(skt):
        """Receives a version message from the given socket, and unpacks it into a version object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        version_header = recv(skt, VERSION_LEN - 1)
        if not version_header:
            print(Fore.RED+"ERROR: recv_version: Socket connection broken, returning None!")
            return None
        try:
            major, minor, extensions_len = struct.unpack(Version.struct_format, version_header)
        except struct.error:
            raise struct.error("Failed to unpack version_header!")
        version = Version(major=major, minor=minor, extensions_len=extensions_len)
        return version
    def send_version(skt, version):
        """Packs a version message into bytes with the given version object and sends it to the given socket object. Returns the number of bytes sent, or None if the socket connection is broken. Raises a TypeError if the skt parameter is not a socket object, or if the version parameter is not a Version object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        if not isinstance(version, Version):
            raise TypeError("Provided version parameter must be a Version object!")
        packed = struct.pack(f'<3BH{version.extensions_len}s', version.lurk_type, version.major, version.minor, version.extensions_len, version.extensions.encode())
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(Fore.RED+f"ERROR: send_version: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(Fore.WHITE+f'DEBUG: send_version: Sent {bytes_sent} byte VERSION!')
        return bytes_sent

def recv(socket, message_length):
    """Receives a message of a specified length from the specified socket and returns it in byte format."""
    message = b''
    while len(message) < message_length:
        chunk = socket.recv(message_length - len(message))
        if not chunk:
            raise RuntimeError(Fore.RED+"Socket connection broken!")
        message += chunk
    return message
def send(skt, message):
    """Sends a packed bytes message to the specified socket."""
    total_sent = 0
    message_length = len(message)
    while total_sent < message_length:
        sent = skt.send(message[total_sent:])
        if sent == 0:
            break
        total_sent += sent
    return total_sent
def read(skt):
    """Reads and interprets binary lurk messages from socket."""
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
                name, flag, attack, defense, regen, health, gold, room, description_len = struct.unpack('<32sB3Hh3H', lurk_header)
                lurk_data = recv(skt, description_len)
                if not lurk_data:
                    print(Fore.RED+'ERROR: read: socket.error, returning None!')
                    return None
                print(Fore.WHITE+f'DEBUG: read: lurk_data: {lurk_data}')
                description, = struct.unpack(f'<{description_len}s', lurk_data)
                name = name.replace(b'\x00', b'')   # I think this fixed stuff? Weird..
                character = Character(name=name.decode('utf-8', 'ignore'), flag=flag, attack=attack, defense=defense, regen=regen, health=health, gold=gold, room=room, description_len=description_len, description=description.decode('utf-8', 'ignore'))
                print(f'DEBUG: Returning character: {character}, Type: {type(character)}')
                return character
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
        print(Fore.RED+'WARN: write: Sending invalid message to socket, hope you are debugging!')
        status = send(skt, lurk_message)
        if status != 0:
            print(Fore.RED+'ERROR: write: socket.error, returning None!')
            return None
    return 0
