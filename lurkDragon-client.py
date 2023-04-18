#!/usr/bin/env python3

import curses
import lurk
import socket

from colorama import Fore

# Variables defining host address & port of server to connect to
HOST = 'localhost'
PORT = 5010

def main(stdscr):
    # Set up the screen
    stdscr.clear()
    stdscr.addstr(0, 0, "Press Ctrl+C to exit")

    # Create a window for user input
    input_window = curses.newwin(3, curses.COLS, curses.LINES-3, 0)
    input_window.addstr(0, 0, "Send a message: ")
    input_window.refresh()

    # Create a window for displaying messages from the server
    display_window = curses.newwin(curses.LINES-3, curses.COLS, 0, 0)
    display_window.scrollok(True)
    display_window.refresh()
    
    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    # Loop for user input
    while True:
        # Get user input
        input_window.clear()
        input_window.addstr(1, 0, "> ")
        input_window.refresh()
        message = input_window.getstr().decode()

        # Send message to server
        s.sendall(message.encode())

        # Receive response from server
        response = s.recv(1024).decode()

        # Display response in the display window
        display_window.addstr(response)
        display_window.refresh()

if __name__ == '__main__':
    # Set up curses and run the main function
    curses.wrapper(main)