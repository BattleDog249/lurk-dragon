"""Logan's LURK Server
"""
#!/usr/bin/env python3

import socket
import sys
import threading
import json

from colorama import Fore
from dataclasses import dataclass
from ctypes import *

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
    """Function for adding a character name to socket pair to the names dictionary.

    Args:
        skt (socket): Socket associated with a character.
        name (string): Name of character associated with a socket.
    """
    names.update({name: skt})
def del_name(name):
    return names.pop(name)
sockets = {}
def add_socket(skt, name):
    sockets.update({skt: name})
def del_socket(skt):
    return sockets.pop(skt)

# Character dictionary containing all monsters and characters in the game.
#   Key (string): UUID
#   Value (list): [name, flag, attack, defense, regen, health, gold, room number, description length, description]
with open(r'C:\Users\lhgray\Documents\CS-435-01\Lurk\characters.json', 'r') as characters_json:
    characters_data = json.load(characters_json)
    for character in characters_data:
        character = lurk.Character(name=character['name'], flag=character['flag'], attack=character['attack'], defense=character['defense'], regen=character['regen'], health=character['health'], gold=character['gold'], room=character['room'], description_len=len(character['description']), description=character['description'])
        lurk.Character.characters.update({character.name: [character.flag, character.attack, character.defense, character.regen, character.health, character.gold, character.room, character.description_len, character.description]})
        print(f'DEBUG: character as dataclass: {character}')
errors = {
    0: 'ERROR: This message type is not supported!',
    1: 'ERROR: Bad Room! Cannot change to requested room.',
    2: 'ERROR: Player Exists. Attempt to create a player that already exists.',
    3: 'ERROR: Bad Monster. Cannot loot a nonexistent, not present, or living monster.',
    4: 'ERROR: Stat error. Caused by setting inappropriate player stats. Try again!',
    5: 'ERROR: Not Ready. Caused by attempting an action too early, for example changing rooms before sending START or CHARACTER.',
    6: 'ERROR: No target. Attempt to loot nonexistent players, fight players in different rooms, message someone offline, etc.',
    7: 'ERROR: No fight. Sent if the requested fight cannot happen for some reason, like no live monsters in room.',
    8: 'ERROR: Player vs. player combat is not currently supported on this server.',
    9: 'ERROR: Monster. Cannot create or reprise a monster character.'
    }
rooms = {
    100: ('Narrator Room', 'Just a room with no connections where the narrator lives.'),
    0: ('Backrooms', 'You should not be here!'),
    1: ('Village of Valhalla', 'A rugged and hardy hamlet nestled in the shadow of towering mountains, home to a fearless group of dragon hunters. The air is tinged with the scent of woodsmoke and iron, and the sound of clanging swords and fierce battle cries can be heard echoing through the valley. The villagers here are skilled and battle-hardened, having spent their lives honing their craft and perfecting their dragon-slaying techniques.'),
    2: ('Aster Meadow', 'Green rolling hills full of wildflowers and small game for as far as the eye can see.'),
    3: ('Ashen Taiga', 'A dark and expansive spruce forest, with a slow climb to higher altitudes in the east.'),
    4: ('Rainless Fells', 'Endless miles of sun-soaked rock and sand under an endless blue sky, this massive tract of land is hostile to all known life.'),
    5: ('Sunset Coast', 'Where the setting sun meets the rolling sea, stretching for untold distances to the north and south.'),
    6: ('Hidden Groves', 'A lively grove of oak trees and song birds, tucked away in a shallow valley in the Aster meadow.'),
    7: ('Abandoned Swamps', 'Murky swamps that remained unexplored, for whatever reason.'),
    8: ('Bloodsoaked Gorge', 'A treacherous and foreboding terrain, where the ground is stained crimson with the blood of battles long past. The walls of the gorge rise high and steep, casting deep shadows that conceal hidden dangers and perils. A dangerous beast must live here, considering the gore and remains strewn about.'),
    9: ('Snowy Mountains', 'The Ashen Taiga gives way to rougher terrain, elevation, and rapidly thinning trees.'),
    10: ('Scorched Frontier', '''In the distant, there is a ruined caravan that looks like it is burnt to ashes.
                                There are a few bodies nearby, as well as some burnt tents. The ground is covered with ash and burnt wood.
                                It looks like a battle between monsters and humans happened.'''),
    11: ('Arid Badlands', 'A harsh and barren landscape, where the scorching sun beats down on rugged terrain, dotted with rocky outcroppings and sparse vegetation. The air is dry and the ground is parched, giving the feeling of a world devoid of life and water.'),
    12: ('Open Sea', '''The open sea gives you a stunning view of the blue ocean, filled with salty waves.
                        As far as you can see, you can see nothing but the massive, unending mass of water.'''),
    13: ('Rugged Coastline', '''A steep cliff-side, with massive rocks all over. It looks slippery and very hard to climb. You can hear ocean waves from the crashing rocks.'''),
    14: ('Forgotten Bog', '''A massive swamp, filled to the brim with thick, slimy moss. The trees are thin, bare, and twisted.
        It's wet, foggy, and smells of rotting flesh. In the distance, you can see the crumbling ruins of an abandoned temple, overrun and covered by fog.'''),
    15: ('Misty Temple', '''An ancient temple filled with a strange mist. The walls have ancient writing in an unknown language.
                            The air in the temple is humid and misty, and the walls smell of mildew.'''),
    16: ('Sulphur Pools', '''A massive crater, with dark, poisonous liquids. The ground is covered in thick, poisonous sludge, and it smells of sulfur and dead fish.
                            The area is incredibly dangerous.'''),
    17: ('Golden Marshes', 'A vast expanse of shimmering grasses and reeds, stretching out as far as the eye can see.'),
    18: ('Sheltered Crevices', 'A hidden and isolated recess nestled deep within the Bloodsoaked Gorge. Despite the turmoil and danger of the surrounding landscape, the Sheltered Crevice provides a small oasis of calm and respite. The sound of rushing water from a nearby stream provides a calming background noise, and the walls provide protection from the harsh elements and violence outside.'),
    19: ('Dark Cavern', 'A shadowy and eerie place, where the only light comes from the occasional flicker of a torch or the glow of luminescent fungi clinging to the walls. The air is damp and musty, and the sound of dripping water echoes through the twisting tunnels.'),
    20: ('Deep Abyss', 'A foreboding and mysterious place, shrouded in darkness and unfathomable depths. The walls of the abyss are jagged and uneven, with strange rock formations and otherworldly creatures lurking in the shadows.'),
    21: ('Submerged Cave', 'The cave is made up of black rocks, and looks slightly dangerous. The entire cave is flooded.'),
    22: ('Raging River', "A tumultuous and powerful force of nature, cutting a winding path through the landscape with an unrelenting force. The sound of rushing water fills the air, and the spray from the river's cascading rapids mists the surrounding rocks and trees."),
    23: ('Frozen Lake', 'A vast expanse of icy blue stretching out to the horizon, surrounded by snow-covered trees and mountains. The air is crisp and biting, and the only sounds are the creaking of the ice and the occasional howl of the wind.'),
    24: ('Jagged Peaks', 'A rugged and treacherous mountain range where the sharp peaks reach toward the sky like the teeth of a giant beast. The air is thin and crisp, and the wind howls through the jagged crevices.'),
    25: ('Peaceful Promontory', 'TBW'),
    26: ('Hidden Valley', "A verdant and lush valley hidden away from the world, where the air is thick with the scent of fresh herbs and the sound of buzzing bees. It's a place where one can feel connected to nature and the beauty of the earth, much like the classic salad dressing that bears its name."),
    27: ('Crop Fields', 'A picturesque and bountiful expanse of farmland nestled within the Hidden Valley. The fields are lush and green, bursting with an abundance of crops, from tall stalks of corn to rows of plump pumpkins.'),
    28: ('Cliffside Roost', "A perilous and foreboding location perched on the edge of a sheer cliff, where a fearsome dragon has made its lair. The dragon's presence is felt in the scorch marks on the rock face and the occasional echoing roar that shakes the nearby trees."),
    29: ('Glacial Highlands', 'A frigid and forbidding landscape where the imposing peaks of glaciers rise above the frozen tundra like jagged teeth. The air is biting cold and thin, and the wind howls through the icy crevices.'),
    30: ('Red Barn', "A charming and rustic structure nestled within the verdant landscape of the Hidden Valley. The barn's red-painted walls stand out against the sea of green, creating a picturesque scene straight out of a postcard."),
    31: ('Loft', 'A spacious and airy area located within the Red Barn, accessible by a steep staircase. The loft is filled with the scent of fresh hay and the sound of chirping birds.'),
    32: ('Roof', 'A flat expanse of weathered shingles located atop the Red Barn, offering an expansive view of the surrounding countryside. From the Roof, one can see the verdant fields of the Hidden Valley stretching out to the horizon, with distant hills and mountains providing a dramatic backdrop.'),
    33: ('Wintery Thicket', 'A tranquil yet forbidding place where the biting cold of winter has turned the thicket into a snowy wonderland. The trees are bare and the underbrush is buried beneath a blanket of snow, making navigation difficult.'),
    34: ('Dusty Ruins', 'A desolate place where the remnants of a forgotten civilization lie scattered amidst the shifting sands. The ruins are weathered and worn, their grandeur faded to mere shadows of their former glory.'),
    35: ('Smoldering Sands', 'A scorching desert expanse where the golden sand dances in the relentless heat, shadows stretch like mountains, and the air is thick with the scent of dry sand and smoke.'),
    36: ('Dire Pits', 'A gaping chasm of darkness filled with the scent of sulfur and brimstone, where jagged walls and otherworldly sounds create an overwhelming sense of unease.'),
    37: ('Rayless Depths', 'A dark and eerie underwater expanse where the sunlight never penetrates, leaving only the dim glow of bioluminescent creatures and the faint shimmer of phosphorescent algae.'),
    38: ('Korpijnen Shores', 'TBW'),
    39: ('Hiemal Inlet', 'TBW'),
    40: ('Remote Estuary', 'TBW'),
}
connections = {
    0: (1,),
    1: (2, 3, 4, 5),
    2: (1, 6, 7),
    3: (1, 8, 9),
    4: (1, 10, 11),
    5: (1, 12, 13),
    6: (2,),
    7: (2, 14, 16),
    8: (3, 18, 22),
    9: (3, 23, 26, 29),
    10: (4, 34),
    11: (4, 35),
    12: (5, 37),
    13: (5, 38, 40),
    14: (7, 15, 16),
    15: (14,),
    16: (7, 14, 17),
    17: (16,),
    18: (8, 19),
    19: (18, 20, 21),
    20: (19,),
    21: (19, 22, 23),
    22: (8,),
    23: (9, 24),
    24: (23, 25, 28),
    25: (24,),
    26: (9, 27, 30),
    27: (26, 30),
    28: (24,),
    29: (9, 33),
    30: (26, 27, 31),
    31: (30, 32),
    32: (31,),
    33: (29,),
    34: (10,),
    35: (11, 36),
    36: (35,),
    37: (12,),
    38: (13, 39),
    39: (38,),
    40: (13,)
}
def cleanup_client(skt):
    """Function for cleaning up a disconnected client.

    Args:
        skt (socket): Client socket.
    """
    if skt in sockets:
        player = lurk.Character.get_character_with_name(sockets[skt])
        name, flag, attack, defense, regen, health, gold, room, description_len, description = player
        flag ^= lurk.READY | lurk.STARTED  # This needs varification, basically set ready & started flags to 0, keeping all other flags the same.
        lurk.Character.characters.update({name: [flag, attack, defense, regen, health, gold, room, description_len, description]})
    try:
        del_name(sockets[skt])
        del_socket(skt)
    except KeyError:
        print(Fore.YELLOW+'WARN: cleanup_client: Nothing to clean!')
    skt.shutdown(2)
    skt.close()
    print(Fore.WHITE+'INFO: cleanup_client: Finished!')
def handle_client(skt):
    """Function for communicating with individual clients.

    Args:
        skt (socket): Client socket.
    """
    while True:
        message = lurk.read(skt)
        if not message:
            print(Fore.RED+'ERROR: handle_client: read returned None, breaking while loop!')
            cleanup_client(skt)
            break
        if type(message) is tuple and message[0] == lurk.MESSAGE:
            lurk_type, msg_len, recipient_name, sender_name, message = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: Message Length:', msg_len)
            print('DEBUG: Recipient Name:', recipient_name)
            print('DEBUG: Sender Name:', sender_name)
            #print('DEBUG: Message:', message)
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Player not ready, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            if recipient_name not in names:
                print(Fore.YELLOW+f'WARN: Recipient {recipient_name} not online, sending ERROR code 6!')
                lurk.write(skt, (lurk.ERROR, 6, len(errors[6]), errors[6]))
                continue
            lurk.write(skt, (lurk.ACCEPT, lurk.MESSAGE))
            lurk.write(names[recipient_name], (lurk.MESSAGE, msg_len, recipient_name, sender_name, message))
            continue
        elif type(message) is tuple and message[0] == lurk.CHANGEROOM:
            lurk_type, new_room = message
            if skt not in sockets:
                error_code = 5
                print(Fore.YELLOW+f'WARN: Player not ready, sending ERROR code {error_code}!')
                lurk.write(skt, (lurk.ERROR, error_code, len(errors[error_code]), errors[error_code]))
                continue
            # Get current player information
            player = lurk.Character.get_character_with_name(sockets[skt])
            #name, flag, attack, defense, regen, health, gold, old_room, description_len, description = player
            if new_room not in connections[player.room]:
                error_code = 1
                print(Fore.YELLOW+f'WARN: {player.name} attempted bad move, sending ERROR code {error_code}!')
                lurk.write(skt, (lurk.ERROR, error_code, len(errors[error_code]), errors[error_code]))
                continue
            # Track old room for later
            old_room = player.room
            # Update current player information with new room
            player.room = new_room
            lurk.Character.update_character(player)
            # Send ROOM to player
            lurk.write(skt, (lurk.ROOM, player.room, rooms[player.room][0], len(rooms[player.room][1]), rooms[player.room][1]))
            # Send updated CHARACTER to player
            lurk.Character.send_character(skt, player)
            # Send all characters in new room to player
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                lurk.Character.send_character(skt, character)
            # Send CONNECTIONs to player
            # TODO: This is a bit of a hack, but it works for now.
            for room_num, connection in connections.items():
                if room_num != new_room:
                    continue
                for connection in connections[room_num]:
                    lurk.write(skt, (lurk.CONNECTION, connection, rooms[connection][0], len(rooms[connection][1]), rooms[connection][1]))
            
            
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
        elif type(message) is tuple and message[0] == lurk.FIGHT:
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            count = 0
            characters = lurk.Character.get_characters_with_room(player.room)
            for character in characters:
                if character.room != player.room or character.flag != lurk.MONSTER | lurk.ALIVE or character.name == player.name:
                    continue
                print(Fore.WHITE+f'DEBUG: {character.name} has monster flag set, flag: {character.flag}')
                count+=1
                monster = lurk.Character.get_character_with_name(character.name)
                #monster_name, monster_flags, monster_attack, monster_defense, monster_regen, monster_health, monster_gold, monster_room, monster_char_des_len, monster_char_des = monster
                monster_damage = monster.attack * monster.attack / (monster.attack + monster.defense)
                player.health -= monster_damage
                player.health = round(player.health)
                print(f'DEBUG: player.health after fight: {player.health}')
                if player.health <= 0:
                    player.flag ^= lurk.ALIVE
                    player.health = 0
                lurk.Character.update_character(player)
                #lurk.Character.characters.update({player_name: [player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des]})
                player_damage = player.attack * player.attack / (player.attack + player.defense)
                monster.health -= player_damage
                monster.health = round(monster.health)
                print(f'DEBUG: monster.health after fight: {monster.health}')
                if monster.health <= 0:
                    monster.flag ^= lurk.ALIVE
                    monster.health = 0
                lurk.Character.update_character(monster)
                #lurk.Character.characters.update({monster_name: [monster_flags, monster_attack, monster_defense, monster_regen, monster_health, monster_gold, monster_room, monster_char_des_len, monster_char_des]})
                # Send updated player stats to all other players in room that player is in
                characters = lurk.Character.get_characters_with_room(player.room)
                for character in characters:
                    if character.name not in names or player.name == sockets[skt]:
                        continue
                    lurk.Character.send_character(names[player.name], character)
            if count == 0:
                print(Fore.YELLOW+f"WARN: No monsters in {player.name}'s room, sending ERROR code 7!")
                lurk.write(skt, (lurk.ERROR, 7, len(errors[7]), errors[7]))
            continue
        elif type(message) is tuple and message[0] == lurk.PVPFIGHT:
            lurk_type, character_name = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: targetName:', character_name)
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
            print('ERROR: Server does not currently support PVPFIGHT, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 8, len(errors[8]), errors[8]))
            continue
        elif type(message) is tuple and message[0] == lurk.LOOT:
            lurk_type, character_name = message
            print(Fore.WHITE+f'DEBUG: handle_client: Type: {lurk_type}')
            print(Fore.WHITE+f'DEBUG: targetName: {character_name}')
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            if player.flag != player.flag | lurk.STARTED:
                print(Fore.YELLOW+'WARN: Player flag STARTED not set, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            target = lurk.Character.get_character_with_name(character_name)
            if target is None or target.room != player.room:
                print(Fore.YELLOW+'WARN: Cannot loot nonexistent target, sending ERROR code 6!')
                lurk.write(skt, (lurk.ERROR, 6, len(errors[6]), errors[6]))
                continue
            if target.flag == target.flag | lurk.ALIVE:
                print(Fore.YELLOW+'WARN: Cannot loot a living target, sending ERROR code 3!')
                lurk.write(skt, (lurk.ERROR, 6, len(errors[6]), errors[6]))
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
        elif type(message) is tuple and message[0] == lurk.START:
            try:
                player = lurk.Character.get_character_with_name(sockets[skt])
                #name, flag, attack, defense, regen, health, gold, room, description_len, description = player
            except:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            if player.room == 0:
                player.room = 1
            player.flag = player.flag | lurk.STARTED
            lurk.Character.update_character(player)
            # Send ACCEPT message
            lurk.write(skt, (lurk.ACCEPT, lurk.START))
            # Send ROOM message
            lurk.write(skt, (lurk.ROOM, player.room, rooms[player.room][0], len(rooms[player.room][1]), rooms[player.room][1]))
            mutex = threading.Lock()
            mutex.acquire()
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
            mutex.release()
            # Send CONNECTION messages for all connections with current room
            for room_num, connection in connections.items():
                if room_num != player.room:
                    continue
                for connection in connections[room_num]:
                    lurk.write(skt, (lurk.CONNECTION, connection, rooms[connection][0], len(rooms[connection][1]), rooms[connection][1]))
            continue
        elif type(message) is tuple and message[0] == lurk.ERROR:
            lurk_type, error_code, error_msg_len, error_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: errCode:', error_code)
            print('DEBUG: errMsgLen:', error_msg_len)
            print('DEBUG: errMsg:', error_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif type(message) is tuple and message[0] == lurk.ACCEPT:
            lurk_type, accepted_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: acceptedMsg:', accepted_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif type(message) is tuple and message[0] == lurk.ROOM:
            lurk_type, room_num, room_name, room_des_len, room_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: roomNum:', room_num)
            print('DEBUG: roomName:', room_name)
            print('DEBUG: roomDesLen:', room_des_len)
            print('DEBUG: roomDes:', room_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif type(message) is lurk.Character:
            print(Fore.WHITE+f'DEBUG: handle_client: Received message: {message}')
            player = message
            if player.name in names:
                error_code = 2
                print(Fore.YELLOW+f'WARN: Attempting to create character already tied to a socket, sending ERROR code {error_code}!')
                lurk.write(skt, (lurk.ERROR, error_code, len(errors[error_code]), errors[error_code]))
                continue
            if player.name in lurk.Character.characters and (player.flag | lurk.MONSTER or player.flag ^ lurk.READY):
                print(Fore.YELLOW+f'WARN: Character attempted to access NPC/Monster {player.name}, which should have a MONSTER flag or not a READY flag if NPC, continuing!')
                continue
            if player.name not in lurk.Character.characters:
                if player.attack + player.defense + player.regen > INIT_POINTS:
                    error_code = 4
                    print(Fore.YELLOW+f'WARN: Character stats from {player.name} invalid, sending ERROR code {error_code}!')
                    lurk.write(skt, (lurk.ERROR, error_code, len(errors[error_code]), errors[error_code]))
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
            lurk.write(skt, (lurk.ACCEPT, lurk.CHARACTER))
            lurk.Character.send_character(skt, player)
            # Send MESSAGE to client from narrator here, stating welcome back!
            continue
        elif type(message) is tuple and message[0] == lurk.GAME:
            lurk_type, init_points, stat_limit, game_des_len, game_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: initPoints:', init_points)
            print('DEBUG: statLimit:', stat_limit)
            print('DEBUG: gameDesLen:', game_des_len)
            print('DEBUG: gameDes:', game_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif type(message) is tuple and message[0] == lurk.LEAVE:
            print(Fore.GREEN+'INFO: handle_client: Received LEAVE!')
            cleanup_client(skt)
            break
        elif type(message) is tuple and message[0] == lurk.CONNECTION:
            lurk_type, room_num, room_name, room_des_len, room_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: roomNum:', room_num)
            print('DEBUG: roomName:', room_name)
            print('DEBUG: roomDesLen:', room_des_len)
            print('DEBUG: roomDes:', room_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif type(message) is tuple and message[0] == lurk.VERSION:
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
