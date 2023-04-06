"""Logan's LURK Server"""
#!/usr/bin/env python3

import json
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
GAME_DESCRIPTION = str(r"""This is a testing branch, and probably broken!
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
    """Function for adding a character name: socket pair to the names dictionary."""
    names.update({name: skt})
def del_name(name):
    """Function for deleting a character name: socket pair from the names dictionary."""
    return names.pop(name)
sockets = {}
def add_socket(skt, name):
    """Function for adding a socket: name pair to the sockets dictionary."""
    sockets.update({skt: name})
def del_socket(skt):
    """Function for deleting a socket: name pair from the sockets dictionary."""
    return sockets.pop(skt)

# Character dictionary containing all monsters and characters in the game.
#   Key (string): UUID
#   Value (list): [name, flag, attack, defense, regen, health, gold, room number, description length, description]
with open(r'C:\Users\lhgray\Documents\CS-435-01\Lurk\characters.json', 'r', encoding='utf-8') as characters_json:
    characters_data = json.load(characters_json)
    for npc in characters_data:
        npc = lurk.Character(name=npc['name'], flag=npc['flag'], attack=npc['attack'], defense=npc['defense'], regen=npc['regen'], health=npc['health'], gold=npc['gold'], room=npc['room'], description_len=len(npc['description']), description=npc['description'])
        lurk.Character.update_character(npc)
# Room dictionary containing all rooms in the game.
#   Key (int): Room Number
#   Value (list): [name, description_len, description, connections]
with open(r'C:\Users\lhgray\Documents\CS-435-01\Lurk\rooms.json', 'r', encoding='utf-8') as rooms_json:
    game_map = json.load(rooms_json)
    for location in game_map:
        location = lurk.Room(number=location['number'], name=location['name'], description_len=len(location['description']), description=location['description'], connections=location['connections'])
        lurk.Room.update_room(location)
# Error dictionary containing all errors in the game.
#   Key (int): Error Code
#   Value (list): [description_len, description]
with open(r'C:\Users\lhgray\Documents\CS-435-01\Lurk\errors.json', 'r', encoding='utf-8') as errors_json:
    errors_list = json.load(errors_json)
    for error in errors_list:
        error = lurk.Error(number=error['number'], description_len=len(error['message']), description=error['message'])
        lurk.Error.update_error(error)
def cleanup_client(skt):
    """Function for cleaning up a disconnected client."""
    if skt in sockets:
        player = lurk.Character.get_character_with_name(sockets[skt])
        player.flag ^= lurk.READY | lurk.STARTED  # This needs varification, basically set ready & started flags to 0, keeping all other flags the same.
        lurk.Character.update_character(player)
    try:
        del_name(sockets[skt])
        del_socket(skt)
    except KeyError:
        print(Fore.YELLOW+'WARN: cleanup_client: Nothing to clean!')
    skt.shutdown(2)
    skt.close()
    print(Fore.WHITE+'INFO: cleanup_client: Finished!')
def handle_client(skt):
    """Thread function for handling a client."""
    while True:
        lurk_type = lurk.recv(skt, 1)
        if not lurk_type:
            print(Fore.RED+'ERROR: handle_client: lurk.recv returned None, breaking while loop!')
            cleanup_client(skt)
            break
        lurk_type = int.from_bytes(lurk_type, byteorder='little')
        if lurk_type < 1 or lurk_type > 14:
            print(Fore.RED+f'ERROR: read: {lurk_type} not a valid lurk message type!')
            continue
        if lurk_type == lurk.MESSAGE:
            lurk_type, msg_len, recipient_name, sender_name, message = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: Message Length:', msg_len)
            print('DEBUG: Recipient Name:', recipient_name)
            print('DEBUG: Sender Name:', sender_name)
            #print('DEBUG: Message:', message)
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Player not ready, sending ERROR code 5!')
                lurk.Error.send_error(skt, 5)
                continue
            if recipient_name not in names:
                print(Fore.YELLOW+f'WARN: Recipient {recipient_name} not online, sending ERROR code 6!')
                lurk.Error.send_error(skt, 6)
                continue
            lurk.Accept.send_accept(skt, lurk.MESSAGE)
            lurk.write(names[recipient_name], (lurk.MESSAGE, msg_len, recipient_name, sender_name, message))
            continue
        elif lurk_type == lurk.CHANGEROOM:
            changeroom = lurk.Changeroom.recv_changeroom(skt)
            if skt not in sockets:
                error_code = 5
                print(Fore.YELLOW+f'WARN: Player not ready, sending ERROR code {error_code}!')
                lurk.Error.send_error(skt, error_code)
                continue
            # Get current player information
            player = lurk.Character.get_character_with_name(sockets[skt])
            room = lurk.Room.get_room(player.room)
            if changeroom.target_room not in room.connections:
                error_code = 1
                print(Fore.YELLOW+f'WARN: {player.name} attempted bad move, sending ERROR code {error_code}!')
                lurk.Error.send_error(skt, error_code)
                continue
            # Track old room for later
            old_room = player.room
            # Update current player information with new room
            player.room = changeroom.target_room
            lurk.Character.update_character(player)
            # Send ROOM to player
            lurk.Room.send_room(skt, room)
            # Send updated CHARACTER to player
            lurk.Character.send_character(skt, player)
            # Send all characters in new room to player
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                lurk.Character.send_character(skt, character)
            # Send CONNECTION messages for all connections with new room to player
            lurk.Connection.send_connections_with_room(skt, player.room)
            # Send updated CHARACTER to all players in old room that player moved to new room
            characters = lurk.Character.get_characters_with_room(old_room)
            for character in characters:
                if character.name not in names or character.name == sockets[skt]:
                    continue
                lurk.Character.send_character(names[character.name], player)
            # Send updated character to all players in new room that player entered new room
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                if character.name not in names or character.name == sockets[skt]:
                    continue
                lurk.Character.send_character(names[character.name], player)
            continue
        elif lurk_type == lurk.FIGHT:
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.Error.send_error(skt, 5)
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            count = 0
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                if character.flag != lurk.MONSTER and lurk.ALIVE:
                    print(f'DEBUG: Character {character.name} not alive or not monster, skipping: {character.flag} lurk.MONSTER | lurk.ALIVE: {lurk.MONSTER | lurk.ALIVE}')
                    print(f'DEBUG: type(character.flag) = {type(character.flag)}; type(lurk.MONSTER): {type(lurk.MONSTER)}')
                    continue
                if character.flag != lurk.MONSTER and lurk.JOIN_BATTLE and lurk.ALIVE:
                    print(f'DEBUG: Character {character.name} not alive or not monster, skipping: {character.flag}')
                    continue
                print(Fore.WHITE+f'DEBUG: {character.name} has monster flag set, flag: {character.flag}')
                count+=1
                monster = lurk.Character.get_character_with_name(character.name)
                monster_damage = monster.attack * monster.attack / (monster.attack + monster.defense)
                player.health -= monster_damage
                player.health = round(player.health)
                print(f'DEBUG: player.health after fight: {player.health}')
                if player.health <= 0:
                    player.flag ^= lurk.ALIVE
                    player.health = 0
                lurk.Character.update_character(player)
                player_damage = player.attack * player.attack / (player.attack + player.defense)
                monster.health -= player_damage
                monster.health = round(monster.health)
                print(f'DEBUG: monster.health after fight: {monster.health}')
                if monster.health <= 0:
                    monster.flag ^= lurk.ALIVE
                    monster.health = 0
                lurk.Character.update_character(monster)
                # Send updated player stats to all other players in room that player is in
                # This is currently broken
                characters = lurk.Character.get_characters_with_room(player.room)
                for character in characters:
                    if character.name not in names:
                        continue
                    lurk.Character.send_character(names[player.name], player)
                    lurk.Character.send_character(names[player.name], monster)
            if count == 0:
                print(Fore.YELLOW+f"WARN: No valid monsters in {player.name}'s room {player.room}, sending ERROR code 7!")
                lurk.Error.send_error(skt, 7)
            continue
        elif lurk_type == lurk.PVPFIGHT:
            lurk_type, character_name = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: targetName:', character_name)
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.Error.send_error(skt, 5)
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            print(Fore.YELLOW+'WARN: Server does not currently support PVPFIGHT, sending ERROR code 8!')
            lurk.Error.send_error(skt, 8)
            continue
        elif lurk_type == lurk.LOOT:
            lurk_type, character_name = message
            print(Fore.WHITE+f'DEBUG: handle_client: Type: {lurk_type}')
            print(Fore.WHITE+f'DEBUG: targetName: {character_name}')
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.Error.send_error(skt, 5)
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            if player.flag != player.flag | lurk.STARTED:
                print(Fore.YELLOW+'WARN: Player flag STARTED not set, sending ERROR code 5!')
                lurk.Error.send_error(skt, 5)
                continue
            target = lurk.Character.get_character_with_name(character_name)
            if target is None or target.room != player.room:
                print(Fore.YELLOW+'WARN: Cannot loot nonexistent target, sending ERROR code 6!')
                lurk.Error.send_error(skt, 6)
                continue
            if target.flag == target.flag | lurk.ALIVE:
                print(Fore.YELLOW+'WARN: Cannot loot a living target, sending ERROR code 3!')
                lurk.Error.send_error(skt, 6)
                continue
            player.gold += target.gold
            target.gold = 0
            lurk.Character.update_character(player)
            lurk.Character.update_character(target)
            # Send updated player stats to all other players in room that player is in
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                if character.name not in names or player.name == sockets[skt]:
                    continue
                lurk.Character.send_character(names[player.name], character)
            continue
        elif lurk_type == lurk.START:
            try:
                player = lurk.Character.get_character_with_name(sockets[skt])
            except:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.Error.send_error(skt, 5)
                continue
            if player.room == 0:
                player.room = 1
            player.flag = player.flag | lurk.STARTED
            lurk.Character.update_character(player)
            # Send ACCEPT message
            lurk.Accept.send_accept(skt, lurk.START)
            # Send ROOM message
            room = lurk.Room.get_room(player.room)
            lurk.Room.send_room(skt, room)
            # Send all characters in room, including player
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                print(f'DEBUG: Sending character {character.name} to {player.name}')
                lurk.Character.send_character(skt, character)
            # Send updated character to all players in room that player joined (except player) the room
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                if character.name not in names or player.name == sockets[skt]:
                    continue
                lurk.Character.send_character(names[player.name], character)
            # Send CONNECTION messages for all connections with current room
            lurk.Connection.send_connections_with_room(skt, player.room)
            '''
            for room_num, connection in connections.items():
                if room_num != player.room:
                    continue
                for connection in connections:
                    connection = lurk.Connection.get_connection(connection)
                    lurk.Connection.send_connection(skt, connection)
                    #lurk.write(skt, (lurk.CONNECTION, connection, lurk.Room.rooms[connection][1], lurk.Room.rooms[connection][2], lurk.Room.rooms[connection][3]))
            '''
            continue
        elif lurk_type == lurk.ERROR:
            lurk_type, error_code, error_msg_len, error_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: errCode:', error_code)
            print('DEBUG: errMsgLen:', error_msg_len)
            print('DEBUG: errMsg:', error_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.Error.send_error(skt, 0)
            continue
        elif lurk_type == lurk.ACCEPT:
            lurk_type, accepted_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: acceptedMsg:', accepted_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.Error.send_error(skt, 0)
            continue
        elif lurk_type == lurk.ROOM:
            lurk_type, room_num, room_name, room_des_len, room_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: roomNum:', room_num)
            print('DEBUG: roomName:', room_name)
            print('DEBUG: roomDesLen:', room_des_len)
            print('DEBUG: roomDes:', room_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.Error.send_error(skt, 0)
            continue
        elif lurk_type == lurk.CHARACTER:
            player = lurk.Character.recv_character(skt)
            if player.name in names:
                error_code = 2
                print(Fore.YELLOW+f'WARN: Attempting to create character already tied to a socket, sending ERROR code {error_code}!')
                lurk.Error.send_error(skt, error_code)
                continue
            if player.name in lurk.Character.characters and (player.flag | lurk.MONSTER or player.flag ^ lurk.READY):
                print(Fore.YELLOW+f'WARN: Character attempted to access NPC/Monster {player.name}, which should have a MONSTER flag or not a READY flag if NPC, continuing!')
                continue
            if player.name not in lurk.Character.characters:
                if player.attack + player.defense + player.regen > INIT_POINTS:
                    error_code = 4
                    print(Fore.YELLOW+f'WARN: Character stats from {player.name} invalid, sending ERROR code {error_code}!')
                    lurk.Error.send_error(skt, error_code)
                    continue
                if player.flag | lurk.JOIN_BATTLE:
                    player.flag = lurk.ALIVE | lurk.JOIN_BATTLE | lurk.READY
                else:
                    player.flag = lurk.ALIVE | lurk.READY
                player.health = 100
                player.gold = 0
                player.room = 0
                player.description_len = len(player.description)
                lurk.Character.update_character(player)
                print(Fore.CYAN+f'INFO: Added new character {player.name} to dictionary')
            player = lurk.Character.get_character_with_name(player.name)
            player.flag = player.flag | lurk.ALIVE
            player.health = 100
            lurk.Character.update_character(player)
            print(Fore.CYAN+f'INFO: Accessing character {player.name} from database')
            add_name(skt, player.name)
            add_socket(skt, player.name)
            lurk.Accept.send_accept(skt, lurk.CHARACTER)
            lurk.Character.send_character(skt, player)
            # Send MESSAGE to client from narrator here, stating welcome back!
            continue
        elif lurk_type == lurk.GAME:
            lurk_type, init_points, stat_limit, game_des_len, game_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: initPoints:', init_points)
            print('DEBUG: statLimit:', stat_limit)
            print('DEBUG: gameDesLen:', game_des_len)
            print('DEBUG: gameDes:', game_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.Error.send_error(skt, 0)
            
            continue
        elif lurk_type == lurk.LEAVE:
            print(Fore.GREEN+'INFO: handle_client: Received LEAVE!')
            cleanup_client(skt)
            break
        elif lurk_type == lurk.CONNECTION:
            lurk_type, room_num, room_name, room_des_len, room_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: roomNum:', room_num)
            print('DEBUG: roomName:', room_name)
            print('DEBUG: roomDesLen:', room_des_len)
            print('DEBUG: roomDes:', room_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.Error.send_error(skt, 0)
            continue
        elif lurk_type == lurk.VERSION:
            lurk_type, major, minor, extension_len = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: major:', major)
            print('DEBUG: minor:', minor)
            print('DEBUG: extSize:', extension_len)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.Error.send_error(skt, 0)
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
    version = lurk.Version(major=MAJOR, minor=MINOR)
    lurk.Version.send_version(client_skt, version)
    game = lurk.Game(initial_points=INIT_POINTS, stat_limit=STAT_LIMIT, description_len=len(GAME_DESCRIPTION), description=GAME_DESCRIPTION)
    lurk.Game.send_game(client_skt, game)
    threading.Thread(target=handle_client, args=(client_skt,), daemon=True).start()
