"""Logan's LURK Server
"""
#!/usr/bin/env python3

import socket
import struct
import sys
import threading

from colorama import Fore

import lurk

MAJOR = int(2)
MINOR = int(3)
EXT_SIZE = int(0)

INIT_POINTS = int(100)
STAT_LIMIT = int(65535)
GAME_DESCRIPTION = str(r"""Can you conquer the beast?
    (                    (                                   
    )\ )               ) )\ )                                
(()/(   (   (    ( /((()/(   (       )  (  (              
    /(_)) ))\  )(   )\())/(_))  )(   ( /(  )\))(  (    (     
(_))  /((_)(()\ ((_)\(_))_  (()\  )(_))((_))\  )\   )\ )  
| |  (_))(  ((_)| |(_)|   \  ((_)((_)_  (()(_)((_) _(_/(  
| |__| || || '_|| / / | |) || '_|/ _` |/ _` |/ _ \| ' \)) 
|____|\_,_||_|  |_\_\ |___/ |_|  \__,_|\__, |\___/|_||_|  
                                        |___/              
""")
GAME_DESCRIPTION_LEN = int(len(GAME_DESCRIPTION))


"""Class for managing functions used across the server"""
clients = {}
def add_client(skt):
    """_summary_

    Args:
        skt (_type_): _description_
    """
    clients[skt] = skt.fileno()              # Add file descriptor to dictionary for tracking connections
    print('DEBUG: Added Client: ', clients[skt])
def remove_client(skt):
    """_summary_

    Args:
        skt (_type_): _description_

    Returns:
        _type_: _description_
    """
    return clients.pop(skt)
# Dictionary (Key: Value)
# Key: Name
# Value (Tuple): (flags, attack, defense, regen, health, gold, currentRoomNum, charDesLen, charDes)
characters = {}
def get_character(name):
    """_summary_

    Args:
        name (_type_): _description_

    Returns:
        _type_: _description_
    """
    if name not in characters:
        print('ERROR: get_character() cannot find character in characters!')
        return None
    character = (lurk.CHARACTER, name, characters[name][0], characters[name][1], characters[name][2], characters[name][3], characters[name][4], characters[name][5], characters[name][6], characters[name][7], characters[name][8])
    return character
def send_character(skt, name):
    """Function for sending a character that is already found on the server

    Args:
        skt (_type_): _description_
        name (_type_): _description_

    Raises:
        struct.error: _description_
        socket.error: _description_

    Returns:
        _type_: _description_
    """
    name = str(name)
    character = get_character(name)
    lurk_type, name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des = character
    try:
        packed = struct.pack(f'<B32sB7H{char_des_len}s', lurk_type, bytes(name, 'utf-8'), flags, attack, defense, regen, health, gold, room, char_des_len, bytes(char_des, 'utf-8'))
        print('DEBUG: Sending CHARACTER message!')
        lurk.send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk.CHARACTER}')
        raise struct.error from exc
    return 0
# Must be a better way to associate connected sockets with an "in-use" character
# This stuff is heavily broken
# {skt: name}
activeCharacters = {}
def get_socket_by_name(name):
    """_summary_

    Args:
        name (_type_): _description_

    Returns:
        _type_: _description_
    """
    for key, value in activeCharacters:
        if value != name:
            continue
        return key
def get_name_by_socket(skt):
    """_summary_

    Args:
        skt (_type_): _description_

    Returns:
        _type_: _description_
    """
    for key, value in activeCharacters:
        if key != skt:
            continue
        return value
monsters = {}
errors = {
    0: 'ERROR: This message type is not supported!',
    1: 'ERROR: Bad Room! Attempt to change to an inappropriate room.',
    2: 'ERROR: Player Exists. Attempt to create a player that already exists.',
    3: 'ERROR: Bad Monster. Attempt to loot a nonexistent or not present monster.',
    4: 'ERROR: Stat error. Caused by setting inappropriate player stats. Try again!',
    5: 'ERROR: Not Ready. Caused by attempting an action too early, for example changing rooms before sending START or CHARACTER.',
    6: 'ERROR: No target. Sent in response to attempts to loot nonexistent players, fight players in different rooms, etc.',
    7: 'ERROR: No fight. Sent if the requested fight cannot happen for other reasons (i.e. no live monsters in room)',
    8: 'ERROR: No player vs. player combat on the server. Servers do not have to support player-vs-player combat.'
    }
def send_error(skt, code):
    """_summary_

    Args:
        skt (_type_): _description_
        code (_type_): _description_

    Raises:
        struct.error: _description_
        socket.error: _description_

    Returns:
        _type_: _description_
    """
    error_code = int(code)
    error_msg_len = len(errors[code])
    error_msg = errors[code]
    try:
        packed = struct.pack(f'<2BH{error_msg_len}s', lurk.ERROR, error_code, error_msg_len, bytes(error_msg, 'utf-8'))
        print('DEBUG: Sending ERROR message!')
        lurk.send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk.ERROR}')
        raise struct.error from exc
    return 0
rooms = {
    0: ('Pine Forest', 'Located deep in the forbidden mountain range, there is surprisingly little to see here beyond towering spruce trees and small game.'),
    1: ('Dark Grove', 'A hallway leading away from the starting room.'),
    2: ('Hidden Valley', 'Seems to be remnants of a ranch here...'),
    3: ('Decrepit Mine', 'A dark mineshaft full of cobwebs and dust.'),
    4: ('Red Barn', 'Simply put, a big red barn.'),
    5: ('Barn Loft', 'The loft, full things nobody wanted to throw away.'),
    6: ('Tool Shed', 'A rusted out tin shed in an advanced state of decay.')
}
def send_room(skt, room):
    """_summary_

    Args:
        skt (_type_): _description_
        room (_type_): _description_

    Raises:
        struct.error: _description_
        socket.error: _description_

    Returns:
        _type_: _description_
    """
    room_num = int(room)
    room_name = rooms[room_num][0]
    room_des_len = len(rooms[room_num][1])
    room_des = rooms[room_num][1]
    try:
        packed = struct.pack(f'<BH32sH{room_des_len}s', lurk.ROOM, room_num, bytes(room_name, 'utf-8'), room_des_len, bytes(room_des, 'utf-8'))
        print('DEBUG: Sending ROOM message!')
        lurk.send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk.MESSAGE}')
        raise struct.error from exc
    return 0
connections = {
    0: (1,),
    1: (2,),
    2: (1, 4, 6),
    3: (2),
    4: (2, 5),
    5: (4,),
    6: (2,)
}
def send_connection(skt, room):
    """Send a lurk CONNECTION message to a socket.

    Args:
        skt (socket): Socket to send data to
        room (tuple): Room number

    Raises:
        struct.error: Failed to pack data into a structure
        lurk.send.Error: Function send failed

    Returns:
        int: 0 if function finishes successfully
    """
    room_num = int(room)
    room_name = rooms[room_num][0]
    room_des_len = len(rooms[room_num][1])
    room_des = rooms[room_num][1]
    try:
        packed = struct.pack(f'<BH32sH{room_des_len}s', lurk.CONNECTION, room_num, bytes(room_name, 'utf-8'), room_des_len, bytes(room_des, 'utf-8'))
        print('DEBUG: Sending CONNECTION message!')
        lurk.send(skt, packed)
    except Exception as exc:
        print(f'ERROR: Failed to pack message type {lurk.CONNECTION}')
        raise struct.error from exc
    return 0
def cleanup_client(skt):
    """_summary_

    Args:
        skt (_type_): _description_
    """
    remove_client(skt)
    skt.shutdown(2)
    skt.close()
def handle_client(skt):
    """_summary_

    Args:
        skt (_type_): _description_
    """
    while True:
        message = lurk.read(skt)
        if not message:
            print('ERROR: handle_client: read returned None, breaking while loop!')
            print(Fore.GREEN+'INFO: handle_client: Running cleanup_client!')
            cleanup_client(skt)
            break
        if message[0] == lurk.MESSAGE:
            lurk_type, msg_len, recipient_name, sender_name, message = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: Message Length:', msg_len)
            print('DEBUG: Recipient Name:', recipient_name)
            print('DEBUG: Sender Name:', sender_name)
            print('DEBUG: Message:', message)
            message = (lurk_type, msg_len, sender_name, recipient_name, message)         # Flipped send/recv
            # Find socket to send to that corresponds with the desired recipient, then send message to that socket
            #sendSkt = Server.get_socket_by_name(recvName)
            #lurk.send_message(sendSkt, message)
            continue
        elif message[0] == lurk.CHANGEROOM:
            lurk_type, new_room_num = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: desiredRoom:', new_room_num)
            character = get_character(activeCharacters[skt])
            lurk_type, name, flags, attack, defense, regen, health, gold, old_room_num, char_des_len, char_des = character
            if flags != 0x98: # This should be bitewise calculated, to account for monsters, other types, etc. Just check that the flag STARTED is set, really
                print('ERROR: Character not started, sending ERROR code 5!')
                send_error(skt, 5)
                continue
            print('DEBUG: connections:', connections)
            print('DEBUG: connections[currentRoomNum]:', connections[old_room_num])
            if new_room_num not in connections[old_room_num]:            # This is giving me issues, needs work
                print('ERROR: Character attempting to move to invalid room, sending ERROR code 1!')
                send_error(skt, 1)
                continue
            characters.update({name: [flags, attack, defense, regen, health, gold, new_room_num, char_des_len, char_des]})
            print('DEBUG: Sending updated character after changeroom:', get_character(name))
            send_room(skt, new_room_num)
            # Send CHARACTER messages for all characters with same room number
            for key, value in characters.items():
                if value[6] != new_room_num:
                    continue
                send_character(skt, key)
            # Send CONNECTION messages for all connections with current room
            # Maybe there is a more efficient way of doing this?
            for key, value in connections.items():
                if key != new_room_num:
                    continue
                print('DEBUG: Found connections:', connections[key])
                for value in connections[key]:
                    print('DEBUG: Sending CONNECTION with value:', value)
                    send_connection(skt, value)
            continue
        elif message[0] == lurk.FIGHT:
            continue
        elif message[0] == lurk.PVPFIGHT:
            lurk_type, character_name = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: targetName:', character_name)
            continue
        elif message[0] == lurk.LOOT:
            lurk_type, character_name = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: targetName:', character_name)
            continue
        elif message[0] == lurk.START:
            print('DEBUG: Handling START!')
            try:
                character = get_character(activeCharacters[skt])
                lurk_type, name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des = character
                print('DEBUG: Got character from socket:', character)
            except:
                print('DEBUG: Could not find character in active, probably. Sending ERROR 5, as user must specify what character they want to use!')
                send_error(skt, 5)
                continue
            characters.update({name:[0x98, attack, defense, regen, health, gold, room, char_des_len, char_des]})    # Fix hardcoding specific flag
            # Send ROOM message
            send_room(skt, character[8])
            # Send CHARACTER messages for all characters with same room number
            for key, value in characters.items():
                if value[6] != room:
                    continue
                send_character(skt, key)
            # Send CONNECTION messages for all connections with current room
            for key, value in connections.items():
                print(f'DEBUG: Evaluating key: {key}, value: {value}')
                if key != room:
                    print(f'DEBUG: Key {key} is not currentRoom {room}, continuing')
                    continue
                print('DEBUG: Found connections:', connections[key])
                for value in connections[key]:
                    print('DEBUG: Sending CONNECTION with value:', value)
                    send_connection(skt, value)
            continue
        elif message[0] == lurk.ERROR:
            lurk_type, error_code, error_msg_len, error_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: errCode:', error_code)
            print('DEBUG: errMsgLen:', error_msg_len)
            print('DEBUG: errMsg:', error_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            status = send_error(skt, 0)
            continue
        elif message[0] == lurk.ACCEPT:
            lurk_type, accepted_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: acceptedMsg:', accepted_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            status = send_error(skt, 0)
            continue
        elif message[0] == lurk.ROOM:
            lurk_type, room_num, room_name, room_des_len, room_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: roomNum:', room_num)
            print('DEBUG: roomName:', room_name)
            print('DEBUG: roomDesLen:', room_des_len)
            print('DEBUG: roomDes:', room_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            status = send_error(skt, 0)
            continue
        elif message[0] == lurk.CHARACTER:
            lurk_type, name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: Name:', name)
            print('DEBUG: Flags:', flags)
            print('DEBUG: Attack:', attack)
            print('DEBUG: Defense:', defense)
            print('DEBUG: Regen:', regen)
            print('DEBUG: Health:', health)
            print('DEBUG: Gold:', gold)
            print('DEBUG: Room:', room)
            print('DEBUG: charDesLen:', char_des_len)
            print('DEBUG: charDes:', char_des)
            if attack + defense + regen > INIT_POINTS:
                print('WARN: Character stats invalid, sending ERROR code 4!')
                status = send_error(skt, 4)
                continue
            lurk.send_accept(skt, lurk.CHARACTER)
            if name in characters:
                print('INFO: Existing character found:', characters[name])
                print('INFO: All characters:', characters)
                activeCharacters.update({skt: name})
                print('DEBUG: New activeCharacter in activeCharacters:', activeCharacters[skt])
                print('DEBUG: All activeCharacters:', activeCharacters)
                old_character = get_character(name)
                print('DEBUG: Sending reprised character:', old_character)
                lurk.send_character(skt, old_character)
                # Send MESSAGE to client from narrator that the character has joined the game here, perhaps?
                continue
            characters.update({name: [0x88, attack, defense, regen, 100, 0, 0, char_des_len, char_des]})
            print('INFO: New character in characters:', characters[name])
            print('INFO: All characters:', characters)
            activeCharacters.update({skt: name})
            print('DEBUG: New activeCharacter in activeCharacters:', activeCharacters[skt])
            print('DEBUG: All activeCharacters:', activeCharacters)
            new_character = get_character(name)
            print('DEBUG: Sending validated character:', new_character)
            lurk.send_character(skt, new_character)
            # Send MESSAGE to client from narrator that the character has joined the game here, perhaps?
            continue
        elif message[0] == lurk.GAME:
            lurk_type, init_points, stat_limit, game_des_len, game_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: initPoints:', init_points)
            print('DEBUG: statLimit:', stat_limit)
            print('DEBUG: gameDesLen:', game_des_len)
            print('DEBUG: gameDes:', game_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            status = send_error(skt, 0)
            continue
        elif message[0] == lurk.LEAVE:
            print(Fore.GREEN+'INFO: handle_client: Received LEAVE, running cleanup_client!')
            cleanup_client(skt)
            break
        elif message[0] == lurk.CONNECTION:
            lurk_type, room_num, room_name, room_des_len, room_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: roomNum:', room_num)
            print('DEBUG: roomName:', room_name)
            print('DEBUG: roomDesLen:', room_des_len)
            print('DEBUG: roomDes:', room_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            status = send_error(skt, 0)
            continue
        elif message[0] == lurk.VERSION:
            lurk_type, major, minor, extension_len = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: major:', major)
            print('DEBUG: minor:', minor)
            print('DEBUG: extSize:', extension_len)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            status = send_error(skt, 0)
            continue
        else:
            print('DEBUG: message[0] not a valid LURK type?')
            continue
# Establish IPv4 TCP socket
server_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if server_skt == -1:
    print(Fore.RED+'ERROR: Server socket creation error, stopping!')
    sys.exit(0)
# Assigned range: 5010 - 5014
ADDRESS = '0.0.0.0'
PORTS = [5010, 5011, 5012, 5013, 5014]
for port in PORTS:
    try:
        server_skt.bind((ADDRESS, port))
        break
    except OSError:
        print(Fore.CYAN+f'WARN: Port {port} unavailable!')
        continue
server_skt.listen()
print(Fore.WHITE+f'INFO: Listening on address: {ADDRESS}, {port}')
while True:
    client_skt, client_addr = server_skt.accept()
    version = (lurk.VERSION, MAJOR, MINOR, EXT_SIZE)
    lurk.send_version(client_skt, version)
    game = (lurk.GAME, INIT_POINTS, STAT_LIMIT, GAME_DESCRIPTION_LEN, GAME_DESCRIPTION)
    lurk.send_game(client_skt, game)
    add_client(client_skt)
    threading.Thread(target=handle_client, args=(client_skt,), daemon=True).start()
