"""LURK protocol-related variables and functions that can be used in a client or server."""
#!/usr/bin/env python3

import socket
import struct

from ctypes import c_uint8, c_uint16, c_int16
from dataclasses import dataclass

from colorama import Fore

MESSAGE = 1
MESSAGE_LEN = 67
CHANGEROOM = 2
CHANGEROOM_LEN = 3
FIGHT = 3
FIGHT_LEN = 1
PVPFIGHT = 4
PVPFIGHT_LEN = 33
LOOT = 5
LOOT_LEN = 33
START = 6
START_LEN = 1
ERROR = 7
ERROR_LEN = 4
ACCEPT = 8
ACCEPT_LEN = 2
ROOM = 9
ROOM_LEN = 37
CHARACTER = 10
CHARACTER_LEN = 48
GAME = 11
GAME_LEN = 7
LEAVE = 12
LEAVE_LEN = 1
CONNECTION = 13
CONNECTION_LEN = 37
VERSION = 14
VERSION_LEN = 5

ALIVE = 0b10000000
JOIN_BATTLE = 0b01000000
MONSTER = 0b00100000
STARTED = 0b00010000
READY = 0b00001000

def recv(socket, message_length):
    """Receives a message of a specified length from the specified socket and returns it in byte format."""
    message = b''
    while len(message) < message_length:
        if chunk := socket.recv(message_length - len(message)):
            message += chunk
        else:
            print(f"{Fore.RED}ERROR: recv: Socket connection broken, returning None!")
            return None
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

@dataclass
class Client:
    pass

@dataclass
class Server:
    pass

@dataclass
class Message:
    """A class that represents a message in the game. This class is used to store information about a message, and to retrieve information about a message."""
    message_len: c_uint16
    recipient: str
    sender: str
    message: str
    lurk_type: c_uint8 = MESSAGE
    def recv_message(skt):
        """Receives a message message from the given socket, and unpacks it into a message object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        message_header = recv(skt, MESSAGE_LEN - 1)
        if not message_header:
            print(f"{Fore.RED}ERROR: recv_message: Socket connection broken, returning None!")
            return None
        try:
            message_len, recipient, sender = struct.unpack('<H32s32s', message_header)
        except struct.error as exc:
            raise struct.error("Failed to unpack message_header!") from exc
        message_data = recv(skt, message_len)
        if not message_data:
            print(f"{Fore.RED}ERROR: recv_message: Socket connection broken, returning None!")
            return None
        try:
            message, = struct.unpack(f'<{message_len}s', message_data)
        except struct.error as exc:
            raise struct.error("Failed to unpack message_data!") from exc
        message = Message(message_len=message_len, recipient=recipient.decode(), sender=sender.decode(), message=message.decode())
        return message
    def send_message(skt, message):
        """Packs a message message into bytes with the given message object and sends it to the given socket object. Returns the number of bytes sent, or None if the socket connection is broken. Raises a TypeError if the skt parameter is not a socket object, or if the message parameter is not a Message object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        if not isinstance(message, Message):
            raise TypeError("Provided message parameter must be a Message object!")
        packed = struct.pack(f'<BH32s32s{message.message_len}s', message.lurk_type, message.message_len, message.recipient.encode(), message.sender.encode(), message.message.encode())
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(f"{Fore.RED}ERROR: send_message: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_message: Sent {bytes_sent} byte MESSAGE!")
        return bytes_sent

@dataclass
class Changeroom:
    """A class that represents a changeroom message in the game. This class is used to store information about a changeroom message, and to retrieve information about a changeroom message."""
    target_room: c_uint16
    lurk_type: c_uint8 = CHANGEROOM
    def recv_changeroom(skt):
        """Receives a changeroom message from the given socket, and unpacks it into a changeroom object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        changeroom_header = recv(skt, CHANGEROOM_LEN - 1)
        if not changeroom_header:
            print(f"{Fore.RED}ERROR: recv_changeroom: Socket connection broken, returning None!")
            return None
        try:
            number, = struct.unpack('<H', changeroom_header)
        except struct.error as exc:
            raise struct.error("Failed to unpack changeroom_header!") from exc
        changeroom = Changeroom(target_room=number)
        return changeroom
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
            print(f"{Fore.RED}ERROR: recv_loot: Socket connection broken, returning None!")
            return None
        try:
            target_name, = struct.unpack('<32s', loot_header)
        except struct.error as exc:
            raise struct.error("Failed to unpack loot_header!") from exc
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
            raise TypeError("skt must be a socket object!")
        start = Start()
        packed = struct.pack(f'<B', start.lurk_type)
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(f"{Fore.RED}ERROR: send_start: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_start: Sent {bytes_sent} byte START!")
        return bytes_sent

@dataclass
class Error:
    """A class that represents an error message in the game. This class is used to store information about an error, and to retrieve information about an error."""
    number: c_uint8
    description_len: c_uint16
    description: str
    lurk_type: c_uint8 = ERROR
    errors = {}
    def update_error(error):
        """Updates the error with the given error object in the errors dictionary, or adds it if it doesn't exist."""
        Error.errors.update({error.number: [error.description_len, error.description]})
    def recv_error(skt):
        """Receives an error message from the given socket, and unpacks it into a error object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        error_header = recv(skt, ERROR_LEN - 1)
        if not error_header:
            print(f"{Fore.RED}ERROR: recv_error: Socket connection broken, returning None!")
            return None
        try:
            number, description_len = struct.unpack('<BH', error_header)
        except struct.error as exc:
            raise struct.error("Failed to unpack error_header!") from exc
        room_data = recv(skt, description_len)
        if not room_data:
            print(f"{Fore.RED}ERROR: recv_error: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', room_data)
        except struct.error as exc:
            raise struct.error("Failed to unpack error_data!") from exc
        error = Error(number=number, description_len=description_len, description=description.decode())
        return error
    def send_error(skt, code):
        """Retrieves the error message with the given code from the errors dictionary, packs it into bytes, and sends it to the given socket object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("skt must be a socket object!")
        if not isinstance(code, int):
            raise TypeError("code must be an int object!")
        if code not in Error.errors:
            raise ValueError("code must be a valid error code!")
        error = Error(number=code, description_len=Error.errors[code][0], description=Error.errors[code][1])
        packed = struct.pack(f'<2BH{error.description_len}s', error.lurk_type, error.number, error.description_len, error.description.encode())
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(f"{Fore.RED}ERROR: send_error: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_error: Sent {bytes_sent} byte ERROR!")
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
            print(f"{Fore.RED}ERROR: send_accept: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_accept: Sent {bytes_sent} byte ACCEPT!")
        return bytes_sent

@dataclass
class Room:
    """A class that represents a room in the game. This class is used to store information about a room, and to retrieve information about a room."""
    number: c_uint16
    name: str
    description_len: c_uint16
    description: str
    connections: list
    lurk_type: c_uint8 = ROOM
    # Key (int): number, Value (tuple): (name, description_len, description, connections)
    rooms = {}
    def update_room(room):
        """Updates the room with the given room object in the rooms dictionary, or adds it if it doesn't exist."""
        Room.rooms.update({room.number: [room.name, room.description_len, room.description, room.connections]})
    def get_room(number):
        """Returns a room with the given number. If the room is not found, returns None."""
        room = [(room_number, room_info) for room_number, room_info in Room.rooms.items() if number in Room.rooms and number == room_number]
        room = Room(number=room[0][0], name=room[0][1][0], description_len=room[0][1][1], description=room[0][1][2], connections=room[0][1][3])
        return room
    def recv_room(skt):
        """Receives a room message from the given socket, and unpacks it into a room object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        room_header = recv(skt, ROOM_LEN - 1)
        if not room_header:
            print(f"{Fore.RED}ERROR: recv_room: Socket connection broken, returning None!")
            return None
        try:
            number, name, description_len = struct.unpack('<H32sH', room_header)
        except struct.error as exc:
            raise struct.error("Failed to unpack room_header!") from exc
        room_data = recv(skt, description_len)
        if not room_data:
            print(f"{Fore.RED}ERROR: recv_room: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', room_data)
        except struct.error as exc:
            raise struct.error("Failed to unpack room_data!") from exc
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
            print(f"{Fore.RED}ERROR: send_room: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_room: Sent {bytes_sent} byte ROOM!")
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
    lurk_type: c_uint8 = CHARACTER
    # Key (str): character.name, Value (Character): Character(name, flag, attack, defense, regen, health, gold, room, description_len, description...)
    characters = {}
    def get_character_with_name(target_name):
        """Returns a character with the given name. If the character is not found, returns None."""
        character_with_name = None
        target_name = target_name.strip()
        for character in Character.characters:
            print(f"DEBUG: get_character_with_name: Checking {Character.characters[character].name} against {target_name}!")
            if Character.characters[character].name == target_name:
                print(f"DEBUG: get_character_with_name: Found {Character.characters[character].name}!")
                character_with_name = Character.characters[character]
        return character_with_name
    def get_characters_with_room(room):
        """Returns a list of character objects that are in the given room. If no characters are found, returns an empty list."""
        characters_with_room = []
        for character in Character.characters:
            if Character.characters[character].room == room:
                characters_with_room.append(Character.characters[character])
        return characters_with_room
    def update_character(character):
        """Updates the character with the given character object in the characters dictionary, or adds it if it doesn't exist."""
        Character.characters.update({character.name: character})
    def recv_character(skt):
        """Receives a character message from the given socket, and unpacks it into a character object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        character_header = recv(skt, CHARACTER_LEN - 1)
        if not character_header:
            print(f"{Fore.RED}ERROR: recv_character: Socket connection broken, returning None!")
            return None
        try:
            name, flag, attack, defense, regen, health, gold, room, description_len = struct.unpack('<32sB3Hh3H', character_header)
        except struct.error as exc:
            raise struct.error("Failed to unpack character_header!") from exc
        character_data = recv(skt, description_len)
        if not character_data:
            print(f"{Fore.RED}ERROR: recv_character: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', character_data)
        except struct.error as exc:
            raise struct.error("Failed to unpack character_data!") from exc
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
            print(f"{Fore.RED}ERROR: send_character: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_character: Sent {bytes_sent} byte CHARACTER!")
        return bytes_sent

@dataclass
class Game:
    """A class that represents a game in the game. This class is used to store information about a game, and to retrieve information about a game."""
    initial_points: c_uint16
    stat_limit: c_uint16
    description_len: c_uint16
    description: str
    lurk_type: c_uint8 = GAME
    def recv_game(skt):
        """Receives a game message from the given socket, and unpacks it into a game object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        game_header = recv(skt, CONNECTION_LEN - 1)
        if not game_header:
            print(f"{Fore.RED}ERROR: recv_game: Socket connection broken, returning None!")
            return None
        try:
            init_points, stat_limit, description_len = struct.unpack('<3H', game_header)
        except struct.error as exc:
            raise struct.error("Failed to unpack game_header!") from exc
        game_data = recv(skt, description_len)
        if not game_data:
            print(f"{Fore.RED}ERROR: recv_game: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', game_data)
        except struct.error as exc:
            raise struct.error("Failed to unpack game_data!") from exc
        game = Game(init_points=init_points,stat_limit=stat_limit, description_len=description_len, description=description.decode())
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
            print(f"{Fore.RED}ERROR: send_game: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_game: Sent {bytes_sent} byte GAME!")
        return bytes_sent

@dataclass
class Leave:
    """A class that represents a leave in the game. This class is used to store information about a leave, and to retrieve information about a leave."""
    lurk_type: c_uint8 = LEAVE
    def send_leave(skt):
        """Packs a leave message into bytes and sends it to the given socket object. Returns the number of bytes sent, or None if the socket connection is broken. Raises a TypeError if the skt parameter is not a socket object."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        packed = struct.pack('<B', Leave.lurk_type)
        bytes_sent = send(skt, packed)
        if bytes_sent != len(packed):
            print(f"{Fore.RED}ERROR: send_leave: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_leave: Sent {bytes_sent} byte LEAVE!")
        return bytes_sent

@dataclass
class Connection:
    """A class that represents a connection in the game. This class is used to store information about a connection, and to retrieve information about a connection."""
    number: c_uint16
    name: str
    description_len: c_uint16
    description: str
    lurk_type: c_uint8 = CONNECTION
    def get_connections_with_room(number):
        """Returns a list of connections that are connected to the given room number."""
        connections = Room.get_room(number).connections
        connections_to_return = []
        for connection in connections:
            connection = Room.get_room(connection)
            connections_to_return.append(connection)
        print(f"{Fore.WHITE}DEBUG: Connection(s) to room {number}: {connections_to_return}")
        return connections_to_return
    def send_connections_with_room(skt, number):
        """"""
        connections = Room.get_room(number).connections
        connections_list = []
        for connection in connections:
            connection = Room.get_room(connection)
            connections_list.append(connection)
        for room in connections_list:
            print(f"{Fore.WHITE}DEBUG: send_connections_with_room: Sending connection {room.name} to client")
            connection = Connection(number=room.number, name=room.name, description_len=room.description_len, description=room.description)
            bytes_sent = Connection.send_connection(skt, connection)
        return bytes_sent
    def recv_connection(skt):
        """Receives a connection message from the given socket, and unpacks it into a connection object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        connection_header = recv(skt, CONNECTION_LEN - 1)
        if not connection_header:
            print(f"{Fore.RED}ERROR: recv_connection: Socket connection broken, returning None!")
            return None
        try:
            number, name, description_len = struct.unpack('<H32sH', connection_header)
        except struct.error as exc:
            raise struct.error("Failed to unpack connection_header!") from exc
        connection_data = recv(skt, description_len)
        if not connection_data:
            print(f"{Fore.RED}ERROR: recv_connection: Socket connection broken, returning None!")
            return None
        try:
            description, = struct.unpack(f'<{description_len}s', connection_data)
        except struct.error as exc:
            raise struct.error("Failed to unpack connection_data!") from exc
        connection = Connection(number=number, name=name.decode(), description_len=description_len, description=description.decode())
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
            print(f"{Fore.RED}ERROR: send_connection: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_connection: Sent {bytes_sent} byte CONNECTION!")
        return bytes_sent

@dataclass
class Version:
    """A class that represents a Lurk version message. This class is used to send and receive version messages."""
    major: c_uint8
    minor: c_uint8
    extensions_len: c_uint16 = 0
    extensions: str = ''
    lurk_type: c_uint8 = VERSION
    def recv_version(skt):
        """Receives a version message from the given socket, and unpacks it into a version object that is returned, or None if an error occurred."""
        if not isinstance(skt, socket.socket):
            raise TypeError("Provided skt parameter must be a socket object!")
        version_header = recv(skt, VERSION_LEN - 1)
        if not version_header:
            print(f"{Fore.RED}ERROR: recv_version: Socket connection broken, returning None!")
            return None
        try:
            major, minor, extensions_len = struct.unpack('<2BH', version_header)
        except struct.error as exc:
            raise struct.error("Failed to unpack version_header!") from exc
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
            print(f"{Fore.RED}ERROR: send_version: Socket connection broken, only sent {bytes_sent} out of {len(packed)} bytes!")
            return None
        print(f"{Fore.WHITE}DEBUG: send_version: Sent {bytes_sent} byte VERSION!")
        return bytes_sent
