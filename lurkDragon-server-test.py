# Testing server using many recv instead of calling recv once and putting the whole message into a buffer.

#!/usr/bin/env python3

from serverlibtest import *

def handleClient(skt):
    while True:
        try:
            messages = lurkRecv(skt)
        except:
            break
        print('DEBUG: messages:', messages)
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
                continue
            elif (msgType == GAME):
                initPoints = message[1]
                print('DEBUG: initPoints:', initPoints)
                statLimit = message[2]
                print('DEBUG: initPoints:', statLimit)
                gameDesLen = message[3]
                print('DEBUG: initPoints:', gameDesLen)
                gameDes = message[4]
                print('DEBUG: initPoints:', gameDes)
                continue
            elif (msgType == LEAVE):
                continue
            elif (msgType == CONNECTION):
                continue
            elif (msgType == VERSION):
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
    
    version = Version.sendVersion(clientSkt)
    game = Game.sendGame(clientSkt)
    
    if (version == 0 and game == 0):
        Client.addClient(clientSkt)
        #Client.getClients()
        clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()    # Create thread for connected client and starts it
    else:
        print('ERROR: VERSION & GAME message failed somehow!')