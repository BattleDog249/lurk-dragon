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

def add_character(character):
    name, flags, attack, defense, regen, health, gold, room_num, char_des_len, char_des = character
    lurk.Character.characters.update({name: [flags, attack, defense, regen, health, gold, room_num, char_des_len, char_des]})
def get_character(name):
    """Returns tuple of information of character with name.

    Args:
        name (string): Name of character

    Returns:
        _type_: _description_
    """
    name = name.replace('\x00', '')
    if name not in lurk.Character.characters:
        print(Fore.RED+f'ERROR: get_character: Cannot find {name} in {lurk.Character.characters.keys()}!')
        return None
    try:
        character = (name, lurk.Character.characters[name][0], lurk.Character.characters[name][1], lurk.Character.characters[name][2], lurk.Character.characters[name][3], lurk.Character.characters[name][4], lurk.Character.characters[name][5], lurk.Character.characters[name][6], lurk.Character.characters[name][7], lurk.Character.characters[name][8])
    except IndexError:
        return character
    return character
def send_characters(room_num):
    """Function for sending all characters to to all connected clients located in provided room number.

    Args:
        room_num (int): Room number.
    """
    #players = [name for name in sockets if room_num == characters[name][6]]
    #sockets = [socket for socket in sockets.keys() if ]
    #for player in players:
        #lurk.write(socket, (lurk.CHARACTER, name, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8]))
    for socket, name in sockets.copy().items():
        player = get_character(name)
        player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
        if player_room != room_num:
            continue
        for name, stats in lurk.Character.characters.copy().items():
            if stats[6] != room_num:
                continue
            try:
                lurk.write(socket, (lurk.CHARACTER, name, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8]))
            except IndexError:
                continue
        #players = [character for character in characters if character[6] == room_num and ]
        #print(f'DEBUG: players in old room: {players}')
        #for player in players:
            #lurk.write(socket, (lurk.CHARACTER, name, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8]))
        #for room_num in characters():
            #print(f'DEBUG: room_num: {room_num} character[6]: {characters[6]}')
def update_characters(target_name, old_room_num):
    """Used to update all connected clients in old_room_num that name moved to a new room"""
    for key, value in sockets.items():
        player = get_character(value)
        player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
        if player_room != old_room_num:
            continue
        target = get_character(target_name)
        target_name, target_flags, target_attack, target_defense, target_regen, target_health, target_gold, target_room, target_char_des_len, target_char_des = target
        lurk.write(key, (lurk.CHARACTER, target_name, target_flags, target_attack, target_defense, target_regen, target_health, target_gold, target_room, target_char_des_len, target_char_des))
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
            name, flag, attack, defense, regen, health, gold, old_room, description_len, description = player
            if new_room not in connections[old_room]:
                error_code = 1
                print(Fore.YELLOW+f'WARN: {name} attempted bad move, sending ERROR code {error_code}!')
                lurk.write(skt, (lurk.ERROR, error_code, len(errors[error_code]), errors[error_code]))
                continue
            # Update current player information with new room
            lurk.Character.characters.update({name: [flag, attack, defense, regen, health, gold, new_room, description_len, description]})
            # Send ROOM to player
            lurk.write(skt, (lurk.ROOM, new_room, rooms[new_room][0], len(rooms[new_room][1]), rooms[new_room][1]))
            # Send updated CHARACTER to player
            lurk.write(skt, (lurk.CHARACTER, name, flag, attack, defense, regen, health, gold, new_room, description_len, description))
            # Send all characters in new room to player
            characters = lurk.Character.get_characters_with_room(new_room)
            for character_name, stat in characters:
                lurk.write(skt, (lurk.CHARACTER, character_name, stat[0], stat[1], stat[2], stat[3], stat[4], stat[5], stat[6], stat[7], stat[8]))
            # Send CONNECTIONs to player
            # TODO: This is a bit of a hack, but it works for now.
            for room_num, connection in connections.items():
                if room_num != new_room:
                    continue
                for connection in connections[room_num]:
                    lurk.write(skt, (lurk.CONNECTION, connection, rooms[connection][0], len(rooms[connection][1]), rooms[connection][1]))
            
            
            # Send updated CHARACTER to all players in old room that player moved to new room
            characters = lurk.Character.get_characters_with_room(old_room)
            for player_name, stat in characters:
                if player_name not in names or player_name == sockets[skt]:
                    continue
                lurk.write(names[player_name], (lurk.CHARACTER, name, flag, attack, defense, regen, health, gold, new_room, description_len, description))
            
            # Send updated character to all players in new room that player moved to new room
            characters = lurk.Character.get_characters_with_room(new_room)
            for player_name, stat in characters:
                if player_name not in names or player_name == sockets[skt]:
                    continue
                lurk.write(names[player_name], (lurk.CHARACTER, name, flag, attack, defense, regen, health, gold, new_room, description_len, description))
            continue
        elif type(message) is tuple and message[0] == lurk.FIGHT:
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            player = lurk.Character.get_character_with_name(sockets[skt])
            player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
            count = 0
            for name, stats in lurk.Character.characters.items():
                if stats[6] != player_room or stats[0] != lurk.MONSTER | lurk.ALIVE or name == player_name:
                    continue
                print(Fore.WHITE+f'DEBUG: {name} has monster flag set, flag: {stats[0]}')
                count+=1
                monster = lurk.Character.get_character_with_name(name)
                monster_name, monster_flags, monster_attack, monster_defense, monster_regen, monster_health, monster_gold, monster_room, monster_char_des_len, monster_char_des = monster
                monster_damage = monster_attack * monster_attack / (monster_attack + monster_defense)
                player_health -= monster_damage
                player_health = round(player_health)
                print(f'DEBUG: player_health after fight: {player_health}')
                if player_health <= 0:
                    player_flags ^= lurk.ALIVE
                    player_health = 0
                lurk.Character.characters.update({player_name: [player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des]})
                player_damage = player_attack * player_attack / (player_attack + player_defense)
                monster_health -= player_damage
                monster_health = round(monster_health)
                print(f'DEBUG: monster_health after fight: {monster_health}')
                if monster_health <= 0:
                    monster_flags ^= lurk.ALIVE
                    monster_health = 0
                lurk.Character.characters.update({monster_name: [monster_flags, monster_attack, monster_defense, monster_regen, monster_health, monster_gold, monster_room, monster_char_des_len, monster_char_des]})
                send_characters(player_room)
            if count == 0:
                print(Fore.YELLOW+f"WARN: No monsters in {player_name}'s room, sending ERROR code 7!")
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
            player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
            if player_flags != player_flags | lurk.STARTED:
                print(Fore.YELLOW+'WARN: Player flag STARTED not set, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            target = lurk.Character.get_character_with_name(character_name)
            if target is None or target[7] != player_room:
                print(Fore.YELLOW+'WARN: Cannot loot nonexistent target, sending ERROR code 6!')
                lurk.write(skt, (lurk.ERROR, 6, len(errors[6]), errors[6]))
                continue
            target_name, target_flags, target_attack, target_defense, target_regen, target_health, target_gold, target_room, target_char_des_len, target_char_des = target
            if target_flags == target_flags | lurk.ALIVE:
                print(Fore.YELLOW+'WARN: Cannot loot a living target, sending ERROR code 3!')
                lurk.write(skt, (lurk.ERROR, 6, len(errors[6]), errors[6]))
                continue
            player_gold += target_gold
            target_gold = 0
            lurk.Character.characters.update({player_name: [player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des]})
            lurk.Character.characters.update({target_name: [target_flags, target_attack, target_defense, target_regen, target_health, target_gold, target_room, target_char_des_len, target_char_des]})
            send_characters(player_room)
            continue
        elif type(message) is tuple and message[0] == lurk.START:
            try:
                player = lurk.Character.get_character_with_name(sockets[skt])
                name, flag, attack, defense, regen, health, gold, room, description_len, description = player
            except:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            if room == 0:
                room = 1
            
            lurk.Character.characters.update({name:[flag | lurk.STARTED, attack, defense, regen, health, gold, room, description_len, description]})
            # Send ACCEPT message
            lurk.write(skt, (lurk.ACCEPT, lurk.START))
            # Send ROOM message
            lurk.write(skt, (lurk.ROOM, room, rooms[room][0], len(rooms[room][1]), rooms[room][1]))
            mutex = threading.Lock()
            mutex.acquire()
            # Send all characters in room
            characters = lurk.Character.get_characters_with_room(room)
            for name, stat in characters:
                print(f'DEBUG: Sending character {name} with stats {stat}')
                lurk.write(skt, (lurk.CHARACTER, name, stat[0], stat[1], stat[2], stat[3], stat[4], stat[5], stat[6], stat[7], stat[8]))
            # Send updated character to all players in room that player joined (except player) the room
            characters = lurk.Character.get_characters_with_room(room)
            for player_name, stat in characters:
                if player_name not in names or player_name == sockets[skt]:
                    continue
                lurk.write(names[player_name], (lurk.CHARACTER, name, flag, attack, defense, regen, health, gold, room, description_len, description))
            mutex.release()
            # Send CONNECTION messages for all connections with current room
            for room_num, connection in connections.items():
                if room_num != room:
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
            lurk.write(skt, (player.message_type, player.name, player.flag, player.attack, player.defense, player.regen, player.health, player.gold, player.room, player.description_len, player.description))
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
