#!/usr/bin/env python3

import threading

from lurklibtest import *

MAJOR = int(2)
MINOR = int(3)
EXT_SIZE = int(0)

INIT_POINTS = int(100)
STAT_LIMIT = int(65535)
GAME_DESCRIPTION = bytes(str("""Can you conquer the beast?
    (                    (                                   
    )\ )               ) )\ )                                
(()/(   (   (    ( /((()/(   (       )  (  (              
    /(_)) ))\  )(   )\())/(_))  )(   ( /(  )\))(  (    (     
(_))  /((_)(()\ ((_)\(_))_  (()\  )(_))((_))\  )\   )\ )  
| |  (_))(  ((_)| |(_)|   \  ((_)((_)_  (()(_)((_) _(_/(  
| |__| || || '_|| / / | |) || '_|/ _` |/ _` |/ _ \| ' \)) 
|____|\_,_||_|  |_\_\ |___/ |_|  \__,_|\__, |\___/|_||_|  
                                        |___/              
"""), 'utf-8')
GAME_DESCRIPTION_LEN = int(len(GAME_DESCRIPTION))

class Server:
    """Class for managing functions used across the server"""
    
    clients = {}
    
    def addClient(skt):
        Server.clients[skt] = skt.fileno()              # Add file descriptor to dictionary for tracking connections
        print('DEBUG: Added Client: ', Server.clients[skt])
    def removeClient(skt):
        print('DEBUG: Removing Client: ', Server.clients[skt])
        Server.clients.pop(skt)
        #print('DEBUG: Connected Clients:', Client.clients)
    def getClients():                   # Pull list of all connected clients
        return Server.clients
    def getClient(skt):                 # Pull information on specified client
        return Server.clients[skt]
    
    characters = {}
    
    def getCharacter(name):
        if name not in Server.characters:
            return None
        character = (CHARACTER, name, Server.characters[name][0], Server.characters[name][1], Server.characters[name][2], Server.characters[name][3], Server.characters[name][4], Server.characters[name][5], Server.characters[name][6], Server.characters[name][7], Server.characters[name][8])
        return character
        
    def getRoom(name):
        """Function for getting current room of provided character name"""
        if name not in Server.characters:
            print('ERROR: getRoom() cannot find character in dictionary of character!')
            return False
        character = Server.characters.get(name)
        print('DEBUG: getRoom() found {} in dictionary!'.format(name))
        room = character[6]
        print('DEBUG: getRoom() returning room number {}'.format(room))
        return room
    
    activeCharacters = {}
    
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
    
    rooms = {
        0: ('Pine Forest', 'Located deep in the forbidden mountain range, there is surprisingly little to see here beyond towering spruce trees and small game.'),
        1: ('Dark Grove', 'A hallway leading away from the starting room.'),
        2: ('Hidden Valley', 'Seems to be remnants of a ranch here...')
    }
    
    connections = {
        rooms[0]: (rooms[1], rooms[2]),
        rooms[1]: (rooms[2]),
        rooms[2]: (rooms[1])
    }

def handleClient(skt):
    while True:
        try:
            messages = Lurk.lurkRecv(skt)
        except:
            break
        print('DEBUG: List of Messages:', messages)
        for message in messages:
            msgType = message[0]
            print('DEBUG: Type:', msgType)
            
            if (msgType == MESSAGE):
                msgLen = message[1]
                print('DEBUG: Message Length:', msgLen)
                recvName = message[2]
                print('DEBUG: Recipient Name:', recvName)
                sendName = message[3]
                print('DEBUG: Sender Name:', sendName)
                narration = message[4]
                print('DEBUG: End of sender Name or narration marker:', narration)
                message = message[5]
                print('DEBUG: Message:', message)
                continue
            
            elif (msgType == CHANGEROOM):
                desiredRoomNum = message[1]
                print('DEBUG: desiredRoomNum:', desiredRoomNum)
                continue
            
            elif (msgType == FIGHT):
                continue
            
            elif (msgType == PVPFIGHT):
                targetName = message[1]
                print('DEBUG: targetName:', targetName)
                continue
            
            elif (msgType == LOOT):
                targetName = message[1]
                print('DEBUG: targetName:', targetName)
                continue
            
            elif (msgType == START):
                continue
            
            elif (msgType == ERROR):
                errCode = message[1]
                print('DEBUG: errCode:', errCode)
                errMsgLen = message[2]
                print('DEBUG: errMsgLen:', errMsgLen)
                errMsg = message[3]
                print('DEBUG: errMsg:', errMsg)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = (ERROR, 0, len(Server.errors[0]), Server.errors[0])
                error = Lurk.sendError(skt, error)
                continue
            
            elif (msgType == ACCEPT):
                acceptedMsg = message[1]
                print('DEBUG: acceptedMsg:', acceptedMsg)
                continue
            
            elif (msgType == ROOM):
                roomNum = message[1]
                print('DEBUG: roomNum:', roomNum)
                roomName = message[2]
                print('DEBUG: roomName:', roomName)
                roomDesLen = message[3]
                print('DEBUG: roomDesLen:', roomDesLen)
                roomDes = message[4]
                print('DEBUG: roomDes:', roomDes)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = (ERROR, 0, len(Server.errors[0]), Server.errors[0])
                error = Lurk.sendError(skt, error)
                continue
            
            elif (msgType == CHARACTER):
                name = message[1]
                print('DEBUG: Name:', name)
                flags = message[2]
                print('DEBUG: Flags:', flags)
                attack = message[3]
                print('DEBUG: Attack:', attack)
                defense = message[4]
                print('DEBUG: Defense:', defense)
                regen = message[5]
                print('DEBUG: Regen:', regen)
                health = message[6]
                print('DEBUG: Health:', health)
                gold = message[7]
                print('DEBUG: Gold:', gold)
                room = message[8]
                print('DEBUG: Room:', room)
                charDesLen = message[9]
                print('DEBUG: charDesLen:', charDesLen)
                charDes = message[10]
                print('DEBUG: charDes:', charDes)
                
                if (attack + defense + regen > INIT_POINTS):
                    print('WARN: Character stats invalid, sending ERROR code 4!')
                    error = (ERROR, 4, len(Server.errors[4]), Server.errors[4])
                    error = Lurk.sendError(skt, error)
                    return 3
                
                accept = Lurk.sendAccept(skt, CHARACTER)
                
                if (name in Server.characters):
                    print('INFO: Existing character found, reprising!')
                    character = Server.getCharacter(name)
                    character = Lurk.sendCharacter(skt, character)
                    # Send MESSAGE to client from narrator that the character has joined the game here, perhaps?
                    continue
                
                print('INFO: Adding new character to world!')
                Server.characters.update({name: [0x58, attack, defense, regen, 100, 0, 0, charDesLen, charDes]})
                character = Server.getCharacter(name)
                print('DEBUG: Passing to Lurk.sendCharacter():', character)
                character = Lurk.sendCharacter(skt, character)
                # Send MESSAGE to client from narrator that the character has joined the game here, perhaps?
                continue
            
            elif (msgType == GAME):
                initPoints = message[1]
                print('DEBUG: initPoints:', initPoints)
                statLimit = message[2]
                print('DEBUG: statLimit:', statLimit)
                gameDesLen = message[3]
                print('DEBUG: gameDesLen:', gameDesLen)
                gameDes = message[4]
                print('DEBUG: gameDes:', gameDes)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = (ERROR, 0, len(Server.errors[0]), Server.errors[0])
                error = Lurk.sendError(skt, error)
                continue
            
            # Probably needs some work and potential error handling, alongside returning something useful rather than continue?
            elif (msgType == LEAVE):
                Server.removeClient(skt)
                skt.shutdown(2)
                skt.close()
                continue
            
            elif (msgType == CONNECTION):
                roomNum = message[1]
                print('DEBUG: roomNum:', roomNum)
                roomName = message[2]
                print('DEBUG: roomName:', roomName)
                roomDesLen = message[3]
                print('DEBUG: roomDesLen:', roomDesLen)
                roomDes = message[4]
                print('DEBUG: roomDes:', roomDes)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = (ERROR, 0, len(Server.errors[0]), Server.errors[0])
                error = Lurk.sendError(skt, error)
                continue
            
            elif (msgType == VERSION):
                major = message[1]
                print('DEBUG: major:', major)
                minor = message[2]
                print('DEBUG: minor:', minor)
                extSize = message[3]
                print('DEBUG: extSize:', extSize)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = (ERROR, 0, len(Server.errors[0]), Server.errors[0])
                error = Lurk.sendError(skt, error)
                continue
    # Cleanup disconencted client routine goes here

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if serverSkt == -1:
    print('ERROR: Server socket error!')
    exit

# Assigned range: 5010 - 5014
address = '0.0.0.0'
port = 5010

serverSkt.bind((address, port))

serverSkt.listen()
print('DEBUG: Listening on address:', address, 'port:', port)

while True:
    clientSkt, clientAddr = serverSkt.accept()
    
    version = (VERSION, MAJOR, MINOR, EXT_SIZE)
    version = Lurk.sendVersion(clientSkt, version)
    game = (GAME, INIT_POINTS, STAT_LIMIT, GAME_DESCRIPTION_LEN, GAME_DESCRIPTION)
    game = Lurk.sendGame(clientSkt, game)
    
    if (version == 0 and game == 0):
        Server.addClient(clientSkt)
        clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()
    else:
        print('ERROR: VERSION & GAME message failed somehow!')