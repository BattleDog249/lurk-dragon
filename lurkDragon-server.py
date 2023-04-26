"""Logan's LURK Server"""
#!/usr/bin/env python3

import json
import socket
import sys
import threading

from colorama import Fore

import lurk

MAJOR = 2
MINOR = 3
EXT_SIZE = 0

INIT_POINTS = 100
STAT_LIMIT = 65535
GAME_DESCRIPTION = r"""Can you conquer the beasts?
    (                    (                                   
    )\ )               ) )\ )                                
(()/(   (   (    ( /((()/(   (       )  (  (              
    /(_)) ))\  )(   )\())/(_))  )(   ( /(  )\))(  (    (     
(_))  /((_)(()\ ((_)\(_))_  (()\  )(_))((_))\  )\   )\ )  
| |  (_))(  ((_)| |(_)|   \  ((_)((_)_  (()(_)((_) _(_/(  
| |__| || || '_|| / / | |) || '_|/ _` |/ _` |/ _ \| ' \)) 
|____|\_,_||_|  |_\_\ |___/ |_|  \__,_|\__, |\___/|_||_|  
                                        |___/              
"""
GAME_DESCRIPTION_LEN = len(GAME_DESCRIPTION)

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

# Populate character dictionary containing all monsters and characters in the game.
#   Key (string): UUID
#   Value (list): [name, flag, attack, defense, regen, health, gold, room number, description length, description]
with open(r'C:\Users\lhgray\Documents\CS-435-01\Lurk\characters.json', 'r', encoding='utf-8') as characters_json:
    characters_data = json.load(characters_json)
    for npc in characters_data:
        npc = lurk.Character(name=npc['name'].strip(), flag=npc['flag'], attack=npc['attack'], defense=npc['defense'], regen=npc['regen'], health=npc['health'], gold=npc['gold'], room=npc['room'], description_len=len(npc['description']), description=npc['description'].strip())
        lurk.Character.update_character(npc)
# Populate room dictionary containing all rooms in the game.
#   Key (int): Room Number
#   Value (list): [name, description_len, description, connections]
with open(r'C:\Users\lhgray\Documents\CS-435-01\Lurk\rooms.json', 'r', encoding='utf-8') as rooms_json:
    game_map = json.load(rooms_json)
    for location in game_map:
        location = lurk.Room(number=location['number'], name=location['name'], description_len=len(location['description']), description=location['description'], connections=location['connections'])
        lurk.Room.update_room(location)
# Populate error dictionary containing all errors in the game.
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
        player.flag ^= lurk.READY | lurk.STARTED  # This needs verification, basically set ready & started flags to 0, keeping all other flags the same.
        player.skt = None
        lurk.Character.update_character(player)
        leave_message = f"{player.name} has left the game!"
        for character in lurk.Character.characters.values():
            if character.skt is None:
                continue
            character_message = lurk.Message(message_len=len(leave_message), recipient=character.name, sender="Jarl", message=leave_message)
            lurk.Message.send_message(character.skt, character_message)
    try:
        del_name(sockets[skt])
        del_socket(skt)
    except KeyError:
        print(f"{Fore.YELLOW}WARN: cleanup_client: Client was not associated with a character, nothing to delete!")
    skt.shutdown(2)
    skt.close()
    print(f"{Fore.GREEN}INFO: cleanup_client: Finished!")
def handle_client(skt):
    """Thread function for handling a client."""
    lock = threading.Lock()
    while True:
        try:
            lock.release()
        except RuntimeError:
            pass
        lurk_type = lurk.recv(skt, 1)
        if not lurk_type:
            print(f"{Fore.YELLOW}WARN: Client disconnected while waiting for a lurk message!")
            cleanup_client(skt)
            break
        lurk_type = int.from_bytes(lurk_type, byteorder='little')
        if lurk_type < 1 or lurk_type > 14:
            print(f"{Fore.RED}ERROR: lurk_type {lurk_type} not a supported type, sending ERROR code 0!")
            lurk.Error.send_error(skt, 0)
            continue
        if lurk_type == lurk.MESSAGE:
            message = lurk.Message.recv_message(skt)
            print(f"{Fore.WHITE}DEBUG: Received MESSAGE: {message}")
            if message is None:
                print(f"{Fore.YELLOW}WARN: Cleaning up after client disconnect!")
                cleanup_client(skt)
                break
            if skt not in sockets:
                print(f"{Fore.YELLOW}WARN: Socket {skt} not yet associated with a character, sending ERROR code 5!")
                lurk.Error.send_error(skt, 5)
                continue
            if message.recipient not in names:
                print(f"{Fore.YELLOW}WARN: Message recipient {message.recipient} not online, sending ERROR code 6 to {sockets[skt]}!")
                lurk.Error.send_error(skt, 6)
                continue
            # Prevents a player from spoofing a message from another player by hardcoding the sender's name.
            sender = lurk.Character.get_character_with_name(sockets[skt])
            message.sender = sender.name
            lurk.Accept.send_accept(skt, message.lurk_type)
            print(f"{Fore.WHITE}DEBUG: Sending message '{message.message}' to {message.recipient} from {message.sender}")
            lurk.Message.send_message(names[message.recipient], message)
        elif lurk_type == lurk.CHANGEROOM:
            lock.acquire()
            changeroom = lurk.Changeroom.recv_changeroom(skt)
            print(f"{Fore.WHITE}DEBUG: Received CHANGEROOM: {changeroom}")
            if changeroom is None:
                print(f"{Fore.YELLOW}WARN: Cleaning up after client disconnect!")
                cleanup_client(skt)
                break
            if skt not in sockets:
                print(f"{Fore.YELLOW}WARN: Socket {skt} not yet associated with a character, sending ERROR code 5!")
                lurk.Error.send_error(skt, 5)
                continue
            old_room = lurk.Room.get_room(player.room)
            if changeroom.target_room not in old_room.connections:
                print(f"{Fore.YELLOW}WARN: {player.name} attempted bad move, sending ERROR code 1!")
                lurk.Error.send_error(skt, 1)
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            old_room = player.room
            player.room = changeroom.target_room
            lurk.Character.update_character(player)
            new_room = lurk.Room.get_room(player.room)
            # Send new ROOM to player
            lurk.Room.send_room(skt, new_room)
            # Send all characters in new room to player
            # Send updated player to all other players in new room that player entered room
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                print(f"{Fore.WHITE}DEBUG: Sending character {character.name} to {sockets[skt]}")
                lurk.Character.send_character(skt, character)
                if character.name not in names or character.name == sockets[skt]:
                    continue
                print(f"{Fore.WHITE}DEBUG: Sending character {player.name} to {character.name}")
                lurk.Character.send_character(names[character.name], player)
            # Send CONNECTION messages for all connections with new room to player
            lurk.Connection.send_connections_with_room(skt, player.room)
            # Send updated CHARACTER to all players in old room that player moved to new room
            characters = lurk.Character.get_characters_with_room(old_room)
            for character in characters:
                if character.name not in names or character.name == sockets[skt]:
                    continue
                print(f"{Fore.WHITE}DEBUG: Sending character {player.name} to {character.name}")
                lurk.Character.send_character(names[character.name], player)
            lock.release()
        elif lurk_type == lurk.FIGHT:
            print(f"{Fore.WHITE}DEBUG: Received FIGHT: {lurk_type}")
            if skt not in sockets:
                print(f"{Fore.YELLOW}WARN: Socket {skt} not yet associated with a character, sending ERROR code 5!")
                lurk.Error.send_error(skt, 5)
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            count = 0
            characters = lurk.Character.get_characters_with_room(player.room)
            print(f"{Fore.WHITE}DEBUG: Potential monsters to fight in room {player.room}: {characters}")
            for character in characters:
                if (character.flag != character.flag | lurk.MONSTER | lurk.ALIVE) or character.name == player.name:
                    print(f"{Fore.WHITE}DEBUG: Character {character.name} not a living monster (160), flag: {character.flag}")
                    continue
                print(f"{Fore.WHITE}DEBUG: {character.name} has MONSTER and ALIVE flag set, flag: {character.flag}")
                count+=1
                monster_damage = character.attack * character.attack / (character.attack + character.defense)
                player.health -= monster_damage
                player.health = round(player.health)
                print(f"{Fore.WHITE}DEBUG: {player.name}'s health after fight: {player.health}")
                if player.health <= 0:
                    player.flag ^= lurk.ALIVE
                    player.health = 0
                lurk.Character.update_character(player)
                player_damage = player.attack * player.attack / (player.attack + player.defense)
                character.health -= player_damage
                character.health = round(character.health)
                print(f"{Fore.WHITE}DEBUG: {character.name}'s health after fight: {character.health}")
                if character.health <= 0:
                    character.flag ^= lurk.ALIVE
                    character.health = 0
                lurk.Character.update_character(character)
                other_players = lurk.Character.get_characters_with_room(player.room)
                # Update current player with new player and monster stats
                print(f"{Fore.WHITE}DEBUG: Sending updated character to {player.name}")
                lurk.Character.send_character(skt, player)
                print(f"{Fore.WHITE}DEBUG: Sending updated monster to {player.name}")
                lurk.Character.send_character(skt, character)
                # Send updated player and monster stats to all other players in current room
                for other_player in other_players:
                    if other_player.name not in names or other_player.name == sockets[skt]:
                        print(f"{Fore.WHITE}DEBUG: {other_player.name} is not a player, continuing...")
                        continue
                    print(f"{Fore.WHITE}DEBUG: Sending updated player {player.name} to {other_player.name}")
                    lurk.Character.send_character(names[other_player.name], player)
                    print(f"{Fore.WHITE}DEBUG: Sending updated monster {character.name} to {other_player.name}")
                    lurk.Character.send_character(names[other_player.name], character)
            if count == 0:
                print(f"{Fore.YELLOW}WARN: No valid monsters in {player.name}'s room {player.room}, sending ERROR code 7!")
                lurk.Error.send_error(skt, 7)
        elif lurk_type == lurk.PVPFIGHT:
            pvpfight = lurk.Pvpfight.recv_pvpfight(skt)
            print(f"{Fore.WHITE}DEBUG: Received PVPFIGHT: {pvpfight}")
            if pvpfight is None:
                print(f"{Fore.YELLOW}WARN: Cleaning up after client disconnect!")
                cleanup_client(skt)
                break
            if skt not in sockets:
                print(f"{Fore.YELLOW}WARN: Socket {skt} not yet associated with a character, sending ERROR code 5!")
                lurk.Error.send_error(skt, 5)
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            print(f"{Fore.YELLOW}WARN: Server does not currently support PVPFIGHT, sending ERROR code 8!")
            lurk.Error.send_error(skt, 8)
        elif lurk_type == lurk.LOOT:
            loot = lurk.Loot.recv_loot(skt)
            print(f"{Fore.WHITE}DEBUG: Received LOOT: {loot}")
            if loot is None:
                print(f"{Fore.YELLOW}WARN: Cleaning up after client disconnect!")
                cleanup_client(skt)
                break
            if skt not in sockets:
                print(f"{Fore.YELLOW}WARN: Socket {skt} not yet associated with a character, sending ERROR code 5!")
                lurk.Error.send_error(skt, 5)
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            if player.flag != player.flag | lurk.STARTED:
                print(f"{Fore.YELLOW}WARN: Player flag STARTED not set, sending ERROR code 5!")
                lurk.Error.send_error(skt, 5)
                continue
            print(f"{Fore.WHITE}DEBUG: Player {player.name} attempting to loot {loot.target_name}")
            target = lurk.Character.get_character_with_name(loot.target_name.replace('\x00', ''))
            if target is None or target.room != player.room:
                print(f"{Fore.YELLOW}WARN: Cannot loot nonexistent target, sending ERROR code 6!")
                lurk.Error.send_error(skt, 6)
                continue
            if target.flag == target.flag | lurk.ALIVE:
                print(f"{Fore.YELLOW}WARN: Cannot loot a living target, sending ERROR code 3!")
                lurk.Error.send_error(skt, 6)
                continue
            player.gold += target.gold
            target.gold = 0
            lurk.Character.update_character(player)
            lurk.Character.update_character(target)
            # Send all characters in room to player, including player, and send player to all active players in room
            # BUG: Sends updated player to other players, but not updated target
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                print(f"{Fore.WHITE}DEBUG: Sending character {character.name} to {player.name}")
                lurk.Character.send_character(skt, character)
                if character.name not in names or character.name == sockets[skt]:
                    continue
                print(f"{Fore.WHITE}DEBUG: Sending character {player.name} to {character.name}")
                lurk.Character.send_character(names[character.name], player)
        elif lurk_type == lurk.START:
            print(f"{Fore.WHITE}DEBUG: Received START: {lurk_type}")
            if skt not in sockets:
                print(f"{Fore.YELLOW}WARN: Socket {skt} not yet associated with a character, sending ERROR code 5!")
                lurk.Error.send_error(skt, 5)
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            if player.room == 0:
                player.room = 1
            player.flag = player.flag | lurk.STARTED
            lurk.Character.update_character(player)
            # Send ACCEPT message
            lurk.Accept.send_accept(skt, lurk.START)
            # Send ROOM message
            room = lurk.Room.get_room(player.room)
            lurk.Room.send_room(skt, room)
            # Send all characters in room to player, including player, and send player to all active players in room
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                print(f"{Fore.WHITE}DEBUG: Sending character {character.name} to {player.name}")
                lurk.Character.send_character(skt, character)
                if character.name not in names or character.name == sockets[skt]:
                    continue
                print(f"{Fore.WHITE}DEBUG: Sending character {player.name} to {character.name}")
                lurk.Character.send_character(names[character.name], player)
            # Send CONNECTION messages for all connections with current room
            lurk.Connection.send_connections_with_room(skt, player.room)
            # Send MESSAGE to client from narrator here, player has joined the game!
            start_message = f"{player.name} has started the game!"
            for character in lurk.Character.characters.values():
                if character.skt is None:
                    continue
                character_message = lurk.Message(message_len=len(start_message), recipient=character.name, sender="Jarl", message=start_message)
                lurk.Message.send_message(character.skt, character_message)
        elif lurk_type == lurk.ERROR:
            print(f"{Fore.RED}ERROR: Server does not support receiving this message, sending ERROR code 0!")
            lurk.Error.send_error(skt, 0)
        elif lurk_type == lurk.ACCEPT:
            print(f"{Fore.RED}ERROR: Server does not support receiving this message, sending ERROR code 0!")
            lurk.Error.send_error(skt, 0)
        elif lurk_type == lurk.ROOM:
            print(f"{Fore.RED}ERROR: Server does not support receiving this message, sending ERROR code 0!")
            lurk.Error.send_error(skt, 0)
        elif lurk_type == lurk.CHARACTER:
            desired_player = lurk.Character.recv_character(skt)
            lock.acquire()
            print(f"{Fore.WHITE}DEBUG: Received CHARACTER: {desired_player}")
            # Check that client did not disconnect during recv_character
            if desired_player is None:
                print(f"{Fore.YELLOW}WARN: Cleaning up after client disconnect!")
                cleanup_client(skt)
                break
            # Check that client is not already associated with a character
            if desired_player.name in lurk.Character.characters and lurk.Character.characters[desired_player.name].skt is not None:
                print(f"{Fore.YELLOW}WARN: Character {desired_player.name} already in use, sending ERROR code 2!")
                lurk.Error.send_error(skt, 2)
                continue
            if desired_player.name not in lurk.Character.characters:
                if desired_player.attack + desired_player.defense + desired_player.regen > INIT_POINTS:
                    print(f"{Fore.YELLOW}WARN: Character stats from {desired_player.name} invalid, sending ERROR code 4!")
                    lurk.Error.send_error(skt, 4)
                    continue
                if desired_player.flag | lurk.JOIN_BATTLE:
                    desired_player.flag = lurk.ALIVE | lurk.JOIN_BATTLE | lurk.READY
                else:
                    desired_player.flag = lurk.ALIVE | lurk.READY
                desired_player.health = 100
                desired_player.gold = 0
                desired_player.room = 0
                desired_player.description_len = len(desired_player.description)
                print(f"{Fore.CYAN}INFO: Adding new character {desired_player.name} to database")
                lurk.Character.update_character(desired_player)
            player = lurk.Character.get_character_with_name(desired_player.name)
            print(f"{Fore.CYAN}INFO: Accessing character {player.name} from database")
            player.flag = player.flag | lurk.ALIVE
            player.health = 100
            player.skt = skt
            lurk.Character.update_character(player)
            add_name(skt, player.name)
            add_socket(skt, player.name)
            lurk.Accept.send_accept(skt, lurk.CHARACTER)
            lurk.Character.send_character(skt, player)
            # Send MESSAGE to client from narrator here, player has joined the game!
            start_message = f"{player.name} has joined the game!"
            for character in lurk.Character.characters.values():
                if character.skt is None:
                    continue
                print(f"DEBUG: message_len={len(start_message)}, recipient={character.name}, sender=Jarl, message={start_message}")
                character_message = lurk.Message(message_len=len(start_message), recipient=character.name, sender="Jarl", message=start_message)
                lurk.Message.send_message(character.skt, character_message)
            lock.release()
        elif lurk_type == lurk.GAME:
            print(f"{Fore.RED}ERROR: Server does not support receiving this message, sending ERROR code 0!")
            lurk.Error.send_error(skt, 0)
        elif lurk_type == lurk.LEAVE:
            print(f"{Fore.WHITE}DEBUG: Received LEAVE: {lurk_type} from {sockets[skt]}")
            cleanup_client(skt)
            break
        elif lurk_type == lurk.CONNECTION:
            connection = lurk.Connection.recv_connection(skt)
            print(f"{Fore.WHITE}DEBUG: Received CONNECTION: {connection}")
            print(f"{Fore.YELLOW}WARN: Server does not support receiving this message, sending ERROR code 0!")
            lurk.Error.send_error(skt, 0)
        elif lurk_type == lurk.VERSION:
            version = lurk.Version.recv_version(skt)
            print(f"{Fore.WHITE}DEBUG: Received VERSION: {version}")
            print(f"{Fore.YELLOW}WARN: Server does not support receiving this message, sending ERROR code 0!")
            lurk.Error.send_error(skt, 0)
        else:
            print(f"{Fore.RED}ERROR: lurk_type {lurk_type} not recognized, sending ERROR code 0!")
            lurk.Error.send_error(skt, 0)
# Establish IPv4 TCP socket
server_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if server_skt == -1:
    print(f"{Fore.RED}ERROR: Server socket creation error, stopping!")
    sys.exit(0)
# Assigned range: 5010 - 5014
ADDRESS = '0.0.0.0'
PORTS = [5010, 5011, 5012, 5013, 5014]
for port in PORTS:
    try:
        server_skt.bind((ADDRESS, port))
        break
    except OSError:
        print(f"{Fore.CYAN}WARN: Port {port} unavailable!")
        continue
server_skt.listen()
print(f"{Fore.WHITE}INFO: Listening on address: {ADDRESS}, {port}")
while True:
    client_skt, client_addr = server_skt.accept()
    version_to_send = lurk.Version(major=MAJOR, minor=MINOR)
    lurk.Version.send_version(client_skt, version_to_send)
    game_to_send = lurk.Game(initial_points=INIT_POINTS, stat_limit=STAT_LIMIT, description_len=len(GAME_DESCRIPTION), description=GAME_DESCRIPTION)
    lurk.Game.send_game(client_skt, game_to_send)
    threading.Thread(target=handle_client, args=(client_skt,), daemon=True).start()
