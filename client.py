"""Logan's LURK Client"""
#!/usr/bin/env python3

# Isoptera IP: 74.118.22.194

import lurk
import socket
import sys
import threading
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal

from colorama import Fore

class ReceiveMessagesThread(QThread):
    message_received = pyqtSignal(object)

    def __init__(self, socket_obj):
        super().__init__()
        self.socket_obj = socket_obj

    def run(self):
        # Receive messages from the server
        while True:
            lurk_type = lurk.recv(self.socket_obj, 1)
            if not lurk_type:
                break
            lurk_type = int.from_bytes(lurk_type, byteorder='little')
            #self.message_received.emit(lurk_type)
            if lurk_type == lurk.MESSAGE:
                message = lurk.Message.recv_message(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received MESSAGE: {message}")
            elif lurk_type == lurk.CHANGEROOM:
                changeroom = lurk.Changeroom.recv_changeroom(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received CHANGEROOM: {changeroom}")
            elif lurk_type == lurk.FIGHT:
                print(f"{Fore.WHITE}DEBUG: Received FIGHT: {lurk_type}")
            elif lurk_type == lurk.PVPFIGHT:
                pvpfight = lurk.Pvpfight.recv_pvpfight(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received PVPFIGHT: {pvpfight}")
            elif lurk_type == lurk.LOOT:
                loot = lurk.Loot.recv_loot(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received LOOT: {loot}")
            elif lurk_type == lurk.START:
                print(f"{Fore.WHITE}DEBUG: Received START: {lurk_type}")
            elif lurk_type == lurk.ERROR:
                error = lurk.Error.recv_error(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received ERROR: {error}")
            elif lurk_type == lurk.ACCEPT:
                accept = lurk.Accept.recv_accept(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received ACCEPT: {accept}")
            elif lurk_type == lurk.ROOM:
                print(f"{Fore.RED}ERROR: Server does not support receiving this message, sending ERROR code 0!")
                lurk.Error.send_error(self.socket_obj, 0)
            elif lurk_type == lurk.CHARACTER:
                desired_player = lurk.Character.recv_character(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received CHARACTER: {desired_player}")
            elif lurk_type == lurk.GAME:
                game = lurk.Game.recv_game(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received GAME: {game}")
                self.message_received.emit(repr(game))
            elif lurk_type == lurk.LEAVE:
                print(f"{Fore.WHITE}DEBUG: Received LEAVE: {lurk_type}")
            elif lurk_type == lurk.CONNECTION:
                connection = lurk.Connection.recv_connection(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received CONNECTION: {connection}")
            elif lurk_type == lurk.VERSION:
                version = lurk.Version.recv_version(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received VERSION: {version}")
                self.message_received.emit(repr(version))
            else:
                print(f"{Fore.RED}ERROR: lurk_type {lurk_type} not recognized, sending ERROR code 0!")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lurk Dragon")
        self.setGeometry(100, 100, 500, 500)

        # Create IP address and port input fields
        self.ip_label = QLabel("IP address:", self)
        self.ip_label.move(10, 10)
        self.ip_field = QLineEdit(self)
        self.ip_field.move(120, 10)
        self.port_label = QLabel("Port:", self)
        self.port_label.move(10, 40)
        self.port_field = QLineEdit(self)
        self.port_field.move(120, 40)

        # Create Connect button
        self.connect_button = QPushButton("Connect", self)
        self.connect_button.move(360, 10)
        self.connect_button.clicked.connect(self.connect_to_server)

        # Create text box to display incoming messages
        self.incoming_messages_textbox = QTextEdit(self)
        self.incoming_messages_textbox.setReadOnly(True)
        self.incoming_messages_textbox.setGeometry(10, 70, 480, 300)

        # Create text box and send button to send messages
        self.send_message_textbox = QTextEdit(self)
        self.send_message_textbox.setGeometry(10, 390, 380, 100)
        self.send_message_button = QPushButton("Send", self)
        self.send_message_button.setGeometry(400, 390, 80, 100)
        self.send_message_button.clicked.connect(self.send_message)

        # Socket to receive messages
        self.socket = None
        
        # Thread to receive messages
        self.receive_thread = None

    def connect_to_server(self):
        # Get IP address and port from input fields
        server_ip = self.ip_field.text()
        server_port = int(self.port_field.text())

        # Create a socket object and connect to the server
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            socket_obj.connect((server_ip, server_port))
        except:
            QMessageBox.warning(self, "Connection Error", "Failed to connect to server.")
            return

        # Save the socket object and disable the IP address and port fields
        self.socket = socket_obj
        self.ip_field.setEnabled(False)
        self.port_field.setEnabled(False)
        
        # Create and start the receive messages thread
        self.receive_thread = ReceiveMessagesThread(self.socket)
        self.receive_thread.message_received.connect(self.receive_message_handler)
        self.receive_thread.start()

    def receive_message_handler(self, message):
        # Append received message to incoming messages text box
        self.incoming_messages_textbox.append(message)

    def send_message(self):
        # Send a message to the server
        message = self.send_message_textbox.toPlainText()
        if message:
            self.socket.sendall(message.encode())
            self.send_message_textbox.clear()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())