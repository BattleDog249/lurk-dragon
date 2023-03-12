"""Logan's LURK Server
"""
#!/usr/bin/env python3

import socket
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

names = {}
def add_name(skt, name):
    names.update({name: skt})
def del_name(name):
    return names.pop(name)
sockets = {}
def add_socket(skt, name):
    sockets.update({skt: name})
def del_socket(skt):
    return sockets.pop(skt)

# Dictionary (Key: Value)
# Key: Name
# Value (Tuple): (flags, attack, defense, regen, health, gold, currentRoomNum, charDesLen, charDes)
characters = {'Blue Bunny': [lurk.ALIVE & lurk.MONSTER, 1, 1, 1, 100, 5, 1, 10,
                             'Dark gray bunny with a red collar, is it a pet?'],
              'Undead Farmer': [lurk.ALIVE & lurk.MONSTER, 1, 1, 1, 100, 100, 3, 13,
                                'Test Dead Guy'],
              'Barnyard Bucko': [lurk.ALIVE & lurk.MONSTER, 1, 1, 1, 100, 100, 5, 43,
                                 'Some weird guy you should probably destroy.']}
def add_character(character):
    name, flags, attack, defense, regen, health, gold, room_num, char_des_len, char_des = character
    characters.update({name: [flags, attack, defense, regen, health, gold, room_num, char_des_len, char_des]})
def get_character(name):
    """Returns tuple of information of character with name.

    Args:
        name (string): Name of character

    Returns:
        _type_: _description_
    """
    if name not in characters:
        print('ERROR: get_character() cannot find character in characters!')
        return None
    character = (name, characters[name][0], characters[name][1], characters[name][2], characters[name][3], characters[name][4], characters[name][5], characters[name][6], characters[name][7], characters[name][8])
    return character
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
rooms = {
    100: ('Narrator Room', 'Just a room with no connections where the narrator lives.'),
    0: ('Starting Room', 'Just a room with no connections where players first arrive after first CHARACTER before being moved to starting room after START.'),
    1: ('Pine Forest', 'Located deep in the forbidden mountain range, there is surprisingly little to see here beyond towering spruce trees and small game.'),
    2: ('Dark Grove', 'A hallway leading away from the starting room.'),
    3: ('Hidden Valley', 'Seems to be remnants of a ranch here...'),
    4: ('Decrepit Mine', 'A dark mineshaft full of cobwebs and dust.'),
    5: ('Red Barn', 'Simply put, a big red barn.'),
    6: ('Barn Loft', 'The loft, full things nobody wanted to throw away.'),
    7: ('Tool Shed', 'A rusted out tin shed in an advanced state of decay.'),
    8: (),
    9: (),
    10: (),
    11: (),
    12: (),
    13: (),
}
connections = {
    0: (1,),
    1: (2,),
    2: (1, 3),
    3: (2, 4, 5, 7),
    4: (3,),
    5: (3, 6),
    6: (5,),
    7: (3,)
}
def cleanup_client(skt):
    """Function for cleaning up a disconnected client.

    Args:
        skt (socket): Client socket.
    """
    del_name(sockets[skt])
    del_socket(skt)
    skt.shutdown(2)
    skt.close()
def handle_client(skt):
    """Function for communicating with individual clients.

    Args:
        skt (socket): Client socket.
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
            if skt not in sockets:
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            if recipient_name not in names:
                lurk.write(skt, (lurk.ERROR, 6, len(errors[6]), errors[6]))
                continue
            lurk.write(skt, (lurk.ACCEPT, lurk.CHARACTER))
            lurk.write(names[recipient_name], (lurk.MESSAGE, msg_len, sender_name, recipient_name, message))
            continue
        elif message[0] == lurk.CHANGEROOM:
            lurk_type, new_room_num = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: desiredRoom:', new_room_num)
            if skt not in sockets:
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            character = get_character(sockets[skt])
            name, flags, attack, defense, regen, health, gold, old_room_num, char_des_len, char_des = character
            if flags != 0x98: # This should be bitewise calculated, to account for monsters, other types, etc. Just check that the flag STARTED is set, really
                print('ERROR: Character not started, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            print('DEBUG: connections:', connections)
            print('DEBUG: connections[currentRoomNum]:', connections[old_room_num])
            if new_room_num not in connections[old_room_num]:            # This is giving me issues, needs work
                print('ERROR: Character attempting to move to invalid room, sending ERROR code 1!')
                lurk.write(skt, (lurk.ERROR, 1, len(errors[1]), errors[1]))
                continue
            lurk.write(skt, (lurk.ACCEPT, lurk.CHANGEROOM))
            characters.update({name: [flags, attack, defense, regen, health, gold, new_room_num, char_des_len, char_des]})
            print('DEBUG: Sending updated character after changeroom:', get_character(name))
            lurk.write(skt, (lurk.ROOM, new_room_num, rooms[new_room_num][0], len(rooms[new_room_num][1]), rooms[new_room_num][1]))
            # Send CHARACTER messages for all characters with same room number
            for name, stats in characters.items():
                if stats[6] != new_room_num:
                    continue
                lurk.write(skt, (lurk.CHARACTER, name, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8]))
            # Send CONNECTION messages for all connections with current room
            # Maybe there is a more efficient way of doing this?
            for room_num, connection in connections.items():
                print(f'DEBUG: Evaluating key: {room_num}, connection: {connection}')
                if room_num != new_room_num:
                    print(f'DEBUG: Key {room_num} is not currentRoom {new_room_num}, continuing')
                    continue
                print('DEBUG: Found connections:', connections[room_num])
                for connection in connections[room_num]:
                    print('DEBUG: Sending CONNECTION with connection:', connection)
                    lurk.write(skt, (lurk.CONNECTION, connection, rooms[connection][0], len(rooms[connection][1]), rooms[connection][1]))
            continue
        elif message[0] == lurk.FIGHT:
            # Get character info who sent fight message
            character = get_character(sockets[skt])
            name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des = character
            # If no monsters in current room, send error type 7: no fight
            # Get all monsters in room
            # Potential damage calculation: damage = attack * attack / (attack + defense)
            continue
        elif message[0] == lurk.PVPFIGHT:
            lurk_type, character_name = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: targetName:', character_name)
            print('ERROR: Server does not currently support PVPFIGHT, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 8, len(errors[8]), errors[8]))
            continue
        elif message[0] == lurk.LOOT:
            lurk_type, character_name = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: targetName:', character_name)
            continue
        elif message[0] == lurk.START:
            print('DEBUG: Handling START!')
            try:
                character = get_character(sockets[skt])
                print('DEBUG: Got character from socket:', character)
                name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des = character
            except:
                print('DEBUG: Could not find character in active, probably. Sending ERROR 5, as user must specify what character they want to use!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            if room == 0:
                room = 1
                characters.update({name:[0x98, attack, defense, regen, health, gold, room, char_des_len, char_des]})    # Fix hardcoding specific flag
            else:
                characters.update({name:[0x98, attack, defense, regen, health, gold, room, char_des_len, char_des]})    # Fix hardcoding specific flag
            # Send ACCEPT message
            lurk.write(skt, (lurk.ACCEPT, lurk.START))
            # Send CHARACTER messages for all characters with same room number
            for name, stats in characters.items():
                if stats[6] != room:
                    continue
                lurk.write(skt, (lurk.CHARACTER, name, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8]))
            # Send ROOM message
            lurk.write(skt, (lurk.ROOM, room, rooms[room][0], len(rooms[room][1]), rooms[room][1]))
            # Send CONNECTION messages for all connections with current room
            for room_num, connection in connections.items():
                print(f'DEBUG: Evaluating key: {room_num}, connection: {connection}')
                if room_num != room:
                    print(f'DEBUG: Key {room_num} is not currentRoom {room}, continuing')
                    continue
                print('DEBUG: Found connections:', connections[room_num])
                for connection in connections[room_num]:
                    print('DEBUG: Sending CONNECTION with connection:', connection)
                    lurk.write(skt, (lurk.CONNECTION, connection, rooms[connection][0], len(rooms[connection][1]), rooms[connection][1]))
            continue
        elif message[0] == lurk.ERROR:
            lurk_type, error_code, error_msg_len, error_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: errCode:', error_code)
            print('DEBUG: errMsgLen:', error_msg_len)
            print('DEBUG: errMsg:', error_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif message[0] == lurk.ACCEPT:
            lurk_type, accepted_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: acceptedMsg:', accepted_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif message[0] == lurk.ROOM:
            lurk_type, room_num, room_name, room_des_len, room_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: roomNum:', room_num)
            print('DEBUG: roomName:', room_name)
            print('DEBUG: roomDesLen:', room_des_len)
            print('DEBUG: roomDes:', room_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
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
            # Check if player name is already active/online, send error if so
            if name in names:
                print(Fore.YELLOW+'WARN: Attempting to create character already tied to a socket, sending ERROR code 2!')
                lurk.write(skt, (lurk.ERROR, 2, len(errors[2]), errors[2]))
                continue
            if name in characters:
                old_character = get_character(name)
                add_name(skt, name)
                add_socket(skt, name)
                print('DEBUG: Sending reprised character:', old_character)
                name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des = old_character
                lurk.write(skt, (lurk.ACCEPT, lurk.CHARACTER))
                lurk.write(skt, (lurk.CHARACTER, name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des))
                # Send MESSAGE to client from narrator here, stating welcome back!
            else:
                if attack + defense + regen > INIT_POINTS:
                    print('WARN: Character stats invalid, sending ERROR code 4!')
                    lurk.write(skt, (lurk.ERROR, 4, len(errors[4]), errors[4]))
                    continue
                new_character = name, 0x88, attack, defense, regen, 100, 0, 0, char_des_len, char_des
                add_character(new_character)
                add_name(skt, name)
                add_socket(skt, name)
                print('DEBUG: Sending validated character:', new_character)
                lurk.write(skt, (lurk.ACCEPT, lurk.CHARACTER))
                lurk.write(skt, (lurk.CHARACTER, new_character[0], new_character[1], new_character[2], new_character[3], new_character[4], new_character[5], new_character[6], new_character[7], new_character[8], new_character[9]))
                # Send MESSAGE to client from narrator here, new player has joined!
            continue
        elif message[0] == lurk.GAME:
            lurk_type, init_points, stat_limit, game_des_len, game_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: initPoints:', init_points)
            print('DEBUG: statLimit:', stat_limit)
            print('DEBUG: gameDesLen:', game_des_len)
            print('DEBUG: gameDes:', game_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
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
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif message[0] == lurk.VERSION:
            lurk_type, major, minor, extension_len = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: major:', major)
            print('DEBUG: minor:', minor)
            print('DEBUG: extSize:', extension_len)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
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
    lurk.write(client_skt, version)
    game = (lurk.GAME, INIT_POINTS, STAT_LIMIT, GAME_DESCRIPTION_LEN, GAME_DESCRIPTION)
    lurk.write(client_skt, game)
    threading.Thread(target=handle_client, args=(client_skt,), daemon=True).start()
