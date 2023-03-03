#!/usr/bin/env python3

import threading

from lurklibtest import *

MAJOR = int(2)
MINOR = int(3)
EXT_SIZE = int(0)

INIT_POINTS = int(100)
STAT_LIMIT = int(65535)
GAME_DESCRIPTION = str("""Can you conquer the beast?
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
            return None
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
    
    def sendError(skt, code):
        errCode = int(code)
        errMsgLen = len(Server.errors[code])
        errMsg = Server.errors[code]
        try:
            errorPacked = struct.pack('<2BH%ds' %errMsgLen, ERROR, errCode, errMsgLen, bytes(errMsg, 'utf-8'))
            print('DEBUG: Sending ERROR message!')
            Lurk.lurkSend(skt, errorPacked)
        except struct.error:
            print('ERROR: Failed to pack ERROR structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    
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
            if (messages == None):
                print('WARN: Client must have disconnected is messages is None.')
                break
        except ConnectionError:
            print('WARN: Lurk.lurkRecv() ConnectionError, breaking')
            break
        print('DEBUG: List of Messages:', messages)
        for message in messages:
            
            if (message[0] == MESSAGE):
                msgType, msgLen, recvName, sendName, narration, message = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: Message Length:', msgLen)
                print('DEBUG: Recipient Name:', recvName)
                print('DEBUG: Sender Name:', sendName)
                print('DEBUG: End of sender Name or narration marker:', narration)
                print('DEBUG: Message:', message)
                continue
            
            elif (message[0] == CHANGEROOM):
                msgType, desiredRoomNum = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: desiredRoomNum:', desiredRoomNum)
                
                character = Server.getRoom(name)                 # UNDER CONSTRUCTION
                if roomNum in Server.connections:
                    pass
                continue
            
            elif (message[0] == FIGHT):
                continue
            
            elif (message[0] == PVPFIGHT):
                msgType, targetName = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: targetName:', targetName)
                continue
            
            elif (message[0] == LOOT):
                msgType, targetName = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: targetName:', targetName)
                continue
            
            elif (message[0] == START):
                activeCharacter = Server.activeCharacters.update({skt: name})
                print('DEBUG: activeCharacters:', activeCharacter)
                Server.characters.update({name:[flags, attack, defense, regen, 100, 0, 1, charDesLen, charDes]})
                room = Server.getRoom(name)
                room = Server.sendRoom(skt, room)
                character = Lurk.sendCharacter(name)
                # Send CHARACTER messages for all characters with same room number
                continue
            
            elif (message[0] == ERROR):
                msgType, errCode, errMsgLen, errMsg = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: errCode:', errCode)
                print('DEBUG: errMsgLen:', errMsgLen)
                print('DEBUG: errMsg:', errMsg)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                status = Server.sendError(skt, 0)
                continue
            
            elif (message[0] == ACCEPT):
                msgType, acceptedMsg = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: acceptedMsg:', acceptedMsg)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                status = Server.sendError(skt, 0)
                continue
            
            elif (message[0] == ROOM):
                msgType, roomNum, roomName, roomDesLen, roomDes = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: roomNum:', roomNum)
                print('DEBUG: roomName:', roomName)
                print('DEBUG: roomDesLen:', roomDesLen)
                print('DEBUG: roomDes:', roomDes)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                status = Server.sendError(skt, 0)
                continue
            
            elif (message[0] == CHARACTER):
                msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: Name:', name)
                print('DEBUG: Flags:', flags)
                print('DEBUG: Attack:', attack)
                print('DEBUG: Defense:', defense)
                print('DEBUG: Regen:', regen)
                print('DEBUG: Health:', health)
                print('DEBUG: Gold:', gold)
                print('DEBUG: Room:', room)
                print('DEBUG: charDesLen:', charDesLen)
                print('DEBUG: charDes:', charDes)
                
                if (attack + defense + regen > INIT_POINTS):
                    print('WARN: Character stats invalid, sending ERROR code 4!')
                    status = Server.sendError(skt, 4)
                    continue
                
                status = Lurk.sendAccept(skt, CHARACTER)
                
                if (name in Server.characters):
                    print('INFO: Existing character found, reprising!')
                    character = Server.getCharacter(name)
                    status = Lurk.sendCharacter(skt, character)
                    # Send MESSAGE to client from narrator that the character has joined the game here, perhaps?
                    continue
                
                print('INFO: Adding new character to world!')
                Server.characters.update({name: [0x58, attack, defense, regen, 100, 0, 0, charDesLen, charDes]})
                character = Server.getCharacter(name)
                print('DEBUG: Passing to Lurk.sendCharacter():', character)
                status = Lurk.sendCharacter(skt, character)
                # Send MESSAGE to client from narrator that the character has joined the game here, perhaps?
                continue
            
            elif (message[0] == GAME):
                msgType, initPoints, statLimit, gameDesLen, gameDes = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: initPoints:', initPoints)
                print('DEBUG: statLimit:', statLimit)
                print('DEBUG: gameDesLen:', gameDesLen)
                print('DEBUG: gameDes:', gameDes)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                status = Server.sendError(skt, 0)
                continue
            
            # Probably needs some work and potential error handling, alongside returning something useful rather than continue?
            elif (message[0] == LEAVE):
                Server.removeClient(skt)
                skt.shutdown(2)
                skt.close()
                continue
            
            elif (message[0] == CONNECTION):
                msgType, roomNum, roomName, roomDesLen, roomDes = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: roomNum:', roomNum)
                print('DEBUG: roomName:', roomName)
                print('DEBUG: roomDesLen:', roomDesLen)
                print('DEBUG: roomDes:', roomDes)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                status = Server.sendError(skt, 0)
                continue
            
            elif (message[0] == VERSION):
                msgType, major, minor, extSize = message
                print('DEBUG: Type:', msgType)
                print('DEBUG: major:', major)
                print('DEBUG: minor:', minor)
                print('DEBUG: extSize:', extSize)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                status = Server.sendError(skt, 0)
                continue
    # Cleanup disconencted client routine goes here
    print('Client disconnected, removing:', skt)
    Server.removeClient(skt)

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