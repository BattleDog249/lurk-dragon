'''
CS435 LurkDragon: Client
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

#!/usr/bin/env python3

# Import socket module, required for network communications
import socket
# Import custom lurk module
from lurk import *
import time

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining host address & port of server to connect to
host = 'localhost'
port = 5010

# Connect to server with assigned host & port
skt.connect((host, port))
print('DEBUG: Connecting to server:', host)

versionBuffer = skt.recv(6)
major, minor, extSize = Version.recvVersion(skt, versionBuffer)

gameBuffer = skt.recv(1024)
game = Game.recvGame(skt, gameBuffer)

characterDescription = "This is a collision test dummy, it is not sentient!"
character = Character("Test Dummy #1", 0x4, 25, 25, 50, 20, 100, 40, len(characterDescription), characterDescription)
character = Character.sendCharacter(character, skt)
character = Character("Test Dummy #2", 0x4, 25, 25, 100, 20, 100, 40, len(characterDescription), characterDescription)
character = Character.sendCharacter(character, skt)

while True:
    buffer = b''                                        # I think this method breaks if recv receives more than one message into buffer
    try:
        buffer = skt.recv(4096)
    except ConnectionError:                                             # Catch a ConnectionError if socket is closed
        print('WARN: Connection broken, stopping!')
        break

    if (buffer != b'' and buffer[0] == 7):
        error = Error.recvError(skt, buffer)
        character = Character("Test Dummy #3", 0x4, 25, 25, 50, 20, 100, 40, len(characterDescription), characterDescription)
        character = Character.sendCharacter(character, skt)
        #leave = Leave.sendLeave(skt)
    elif (buffer != b'' and buffer[0] == 8):
        accept = Accept.recvAccept(skt, buffer)
        roomBuffer = skt.recv(1024)
        room = Room.recvRoom(skt, roomBuffer)
        #leave = Leave.sendLeave(skt)
    else:
        continue