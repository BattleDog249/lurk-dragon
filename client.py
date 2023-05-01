"""Logan's LURK Client"""
#!/usr/bin/env python3

# Isoptera IP: 74.118.22.194

import socket
import sys
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIntValidator, QKeySequence
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QSplitter, QMessageBox

from colorama import Fore

import lurk

class MainWindow(QMainWindow):
    """Main window for LURK client"""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Lurk Dragon")
        self.setMinimumSize(400, 400)

        # Create widgets
        self.textbox_ip = QLineEdit()
        self.textbox_ip.setPlaceholderText("IP Address")
        self.textbox_port = QLineEdit()
        self.textbox_port.setPlaceholderText("Port")
        self.textbox_port.setFixedWidth(100)
        self.textbox_port.setValidator(QIntValidator(0, 65535, self))
        self.textbox_input = QTextEdit()
        self.textbox_input.setPlaceholderText("Messages from server will appear here")
        self.textbox_output = QTextEdit()
        self.textbox_output.setPlaceholderText("LURK Message to send to server")
        self.button_send = QPushButton("Send")
        self.button_send.setEnabled(False)
        self.button_connect = QPushButton("Connect")
        self.button_disconnect = QPushButton("Disconnect")
        self.button_disconnect.setEnabled(False)

        # Set up splitter widget
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.textbox_input)
        splitter.addWidget(self.textbox_output)

        # Create layouts
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        incoming_layout = QHBoxLayout()
        outgoing_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        address_layout = QHBoxLayout()

        # Add widgets to layouts
        incoming_layout.addWidget(splitter)
        outgoing_layout.addWidget(self.button_send)
        button_layout.addWidget(self.button_connect)
        button_layout.addWidget(self.button_disconnect)
        address_layout.addWidget(self.textbox_ip)
        address_layout.addWidget(self.textbox_port)

        # Add layouts to main layout
        main_layout.addLayout(address_layout)
        main_layout.addLayout(incoming_layout)
        main_layout.addLayout(outgoing_layout)
        main_layout.addLayout(button_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect signals and slots
        self.button_send.clicked.connect(self.send_message)
        self.button_connect.clicked.connect(self.connect_to_server)
        self.button_disconnect.clicked.connect(self.disconnect_from_server)
        self.textbox_output.keyPressEvent = self.handle_key_press

        # Socket to receive messages
        self.socket = None
        
        # Thread to receive messages
        self.receive_thread = None

    def handle_key_press(self, event):
        if event.key() == QKeySequence('Return'):
            print("Enter pressed, evaluating potential command!")
            if self.textbox_output.toPlainText().split('\n')[-1] == '/make':
                print("Detected /make command")
            self.send_message()
        elif event.key() == QKeySequence('Backspace'):
            print("Backspace pressed!")
            self.textbox_output.textCursor().deletePreviousChar()
        else:
            super().keyPressEvent(event)
            self.textbox_output.insertPlainText(event.text())

    def send_message(self):
        # Send a message to the server
        message = self.textbox_output.toPlainText().split('\n')[-1]
        if message:
            self.socket.sendall(message.encode())
            #self.textbox_output.clear()
            self.textbox_output.insertPlainText('\n')

    def connect_to_server(self):
        # Get IP address and port from input fields
        server_ip = self.textbox_ip.text()
        print(f"DEBUG: Connecting to {server_ip}...")
        server_port = int(self.textbox_port.text())
        if server_port < 0 or server_port > 65535:
            self.textbox_port.clear()
            QMessageBox.warning(self, "Invalid Port", "Port must be a valid integer between 0 and 65535.")
            return
        print(f"DEBUG: On port {server_port}...")

        # Create a socket object and connect to the server
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            socket_obj.connect((server_ip, server_port))
        except:
            QMessageBox.warning(self, "Connection Error", "Failed to connect to server.")
            return

        # Save the socket object and disable the IP address and port fields
        self.socket = socket_obj
        self.button_connect.setEnabled(False)
        self.button_disconnect.setEnabled(True)
        self.button_send.setEnabled(True)
        self.textbox_ip.setEnabled(False)
        self.textbox_port.setEnabled(False)
        
        # Create and start the receive messages thread
        self.receive_thread = ReceiveMessagesThread(self.socket)
        self.receive_thread.message_received.connect(self.receive_message_handler)
        self.receive_thread.start()
    
    def disconnect_from_server(self):
        # Add code to disconnect from server here
        self.button_connect.setEnabled(True)
        self.button_disconnect.setEnabled(False)
        self.button_send.setEnabled(False)
        self.textbox_ip.setEnabled(True)
        self.textbox_port.setEnabled(True)
        lurk.Leave.send_leave(self.socket)

    def receive_message_handler(self, message):
        # Append received message to incoming messages text box
        self.textbox_input.append(message)

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
                print("DEBUG: Detected NONE from lurk.recv()!")
                break
            lurk_type = int.from_bytes(lurk_type, byteorder='little')
            #self.message_received.emit(f"Received type: {lurk_type}")
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
                self.message_received.emit(f"ERROR {error.number}: {error.description}")
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
                self.message_received.emit(f"Server has {game.initial_points} initial points and a stat limit of {game.stat_limit}")
                self.message_received.emit(f"{game.description}")
            elif lurk_type == lurk.LEAVE:
                print(f"{Fore.WHITE}DEBUG: Received LEAVE: {lurk_type}")
            elif lurk_type == lurk.CONNECTION:
                connection = lurk.Connection.recv_connection(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received CONNECTION: {connection}")
            elif lurk_type == lurk.VERSION:
                version = lurk.Version.recv_version(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received VERSION: {version}")
                self.message_received.emit(f"LURK Version {version.major}.{version.minor} with extensions: {version.extensions}")
            else:
                print(f"{Fore.RED}ERROR: lurk_type {lurk_type} not recognized, sending ERROR code 0!")
        self.message_received.emit("Connection to server lost!")
        main_window.disconnect_from_server()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
