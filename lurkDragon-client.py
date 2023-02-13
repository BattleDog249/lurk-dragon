'''
CS435 LurkDragon: Client
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
'''

# Import socket module, required for network communications
import socket
# Import custom lurk module
from lurk import *

# Establish IPv4 TCP socket
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variables defining host address & port of server to connect to
host = 'localhost'
port = 5010

# Connect to server with assigned host & port
skt.connect((host, port))
print('DEBUG: Connecting to server:', host)

versionBuffer = skt.recv(1024)
version = Version.recvVersion(skt, versionBuffer)

gameBuffer = skt.recv(1024)
game = Game.recvGame(skt, gameBuffer)

if game == 0:
    characterDescription = "This is a test dummy description tester! Testing! 123!"
    character = Character("Test Dummy Character", 0x4, 25, 25, 50, 20, 100, 40, len(characterDescription), characterDescription)
    character = Character.sendCharacter(character, skt)
    print('DEBUG: Successfully received VERSION & GAME message, sent CHARACTER message in response!')

    validBuffer = skt.recv(1024)
    if (validBuffer[0] == 8):
        accept = Accept.recvAccept(skt, validBuffer)
        if (accept != 0):
            print('WARN: recvAccept() returned unexpected code', accept)
            exit
    elif (validBuffer[0] == 7):
        error = Error.recvError(skt, validBuffer)
        character = Character("Test Dummy # 512", 0x4, 25, 25, 50, 20, 100, 40, len(characterDescription), characterDescription)
        character.sendCharacter()
    else:
        print('WARN: Perhaps no ACCEPT or ERROR message received?')
        

else:
    print('ERROR: Failed to receive GAME message, not sending CHARACTER message!')

#skt.shutdown(2) # Not necessary AFAIK
#skt.close() # Close connection to server
#print('DEBUG: Closed connection')