"""Logan's LURK Client"""
#!/usr/bin/env python3

# Isoptera IP: 74.118.22.194

import socket
import sys
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator, QKeySequence
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QSplitter, QMessageBox, QLabel, QSpinBox, QCheckBox, QGroupBox

from colorama import Fore

import lurk

class MainWindow(QMainWindow):
    """Main window for LURK client"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Socket to receive messages
        self.socket = None
        
        # Thread to receive messages
        self.receive_thread = None

    def init_ui(self):
        self.setWindowTitle("Lurk Dragon")
        self.setMinimumSize(400, 400)
        
        # Create connection info widgets
        # Include a label for the IP address, a textbox for the IP address, a label for the port, a textbox for the port, a connect button, and a disconnect button
        self.connection_box = QGroupBox("Server Connection")
        
        self.textbox_ip = QLineEdit("isoptera.lcsc.edu")
        self.textbox_ip.setPlaceholderText("IP Address")
        
        self.textbox_port = QLineEdit("5010")
        self.textbox_port.setPlaceholderText("Port")
        self.textbox_port.setFixedWidth(50)
        self.textbox_port.setValidator(QIntValidator(0, 65535, self))
        
        self.button_connect = QPushButton("Connect")
        
        self.button_disconnect = QPushButton("Disconnect")
        self.button_disconnect.setEnabled(False)
        
        # Create game info widgets
        self.game_box = QGroupBox("Game Info")
        
        self.version_info = QLabel()
        self.version_info.setText("LURK Version: Extension Size: ")
        self.version_info.setWordWrap(True)
        
        self.game_info = QLabel()
        self.game_info.setText("Initial Points: Stat Limit: \nDescription: ")
        self.game_info.setWordWrap(True)
        
        # Create widgets
        self.textbox_input = QTextEdit()
        self.textbox_input.setPlaceholderText("Messages from server will appear here")
        self.textbox_output = QTextEdit()
        self.textbox_output.setPlaceholderText("LURK Message to send to server")
        self.button_send = QPushButton("Send")
        self.button_send.setEnabled(False)
        
        # Added: New QHBoxLayout with requested widgets
        self.character_name = QLineEdit()
        self.character_name.setMaxLength(32)
        self.character_name.setPlaceholderText("Character Name")
        self.auto_join_fight = QCheckBox("Auto join fights")
        self.attack_value = QSpinBox()
        self.attack_value.setRange(0, 100)
        self.attack_value.setSuffix(" Attack")
        self.defense_value = QSpinBox()
        self.defense_value.setRange(0, 100)
        self.defense_value.setSuffix(" Defense")
        self.regen_value = QSpinBox()
        self.regen_value.setRange(0, 100)
        self.regen_value.setSuffix(" Regen")
        self.health_value = QSpinBox()
        self.health_value.setRange(0, 65535)
        self.health_value.setSuffix(" Health")
        self.health_value.setEnabled(True)
        self.gold_value = QSpinBox()
        self.gold_value.setRange(0, 65535)
        self.gold_value.setSuffix(" Gold")
        self.gold_value.setEnabled(True)
        self.room_value = QSpinBox()
        self.room_value.setRange(0, 65535)
        self.room_value.setPrefix("Room ")
        self.room_value.setEnabled(True)
        self.character_description = QLineEdit()
        self.character_description.setPlaceholderText("Character Description")
        self.button_send_character = QPushButton("Character")
        self.button_send_character.setEnabled(False)
        self.button_send_start = QPushButton("Start")
        self.button_send_start.setEnabled(False)
        self.list_of_characters = QTextEdit()
        self.list_of_characters.setPlaceholderText("Characters in room appear here")
        self.list_of_characters.setReadOnly(True)

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
        character_layout = QHBoxLayout()
        character_description_layout = QHBoxLayout()
        list_of_characters_layout = QHBoxLayout()

        # Add widgets to layouts
        incoming_layout.addWidget(splitter)
        outgoing_layout.addWidget(self.button_send)
        address_layout.addWidget(self.textbox_ip)
        address_layout.addWidget(self.textbox_port)
        address_layout.addWidget(self.button_connect)
        address_layout.addWidget(self.button_disconnect)
        self.connection_box.setLayout(address_layout)
        character_layout.addWidget(self.character_name)
        character_layout.addWidget(self.auto_join_fight)
        character_layout.addWidget(self.attack_value)
        character_layout.addWidget(self.defense_value)
        character_layout.addWidget(self.regen_value)
        character_layout.addWidget(self.health_value)
        character_layout.addWidget(self.gold_value)
        character_layout.addWidget(self.room_value)
        character_layout.addWidget(self.button_send_character)
        character_description_layout.addWidget(self.character_description)
        character_description_layout.addWidget(self.button_send_start)
        list_of_characters_layout.addWidget(self.list_of_characters)

        # Add layouts to main layout
        main_layout.addWidget(self.connection_box)  # Added
        main_layout.addWidget(self.version_info)  # Added
        main_layout.addWidget(self.game_info)  # Added
        main_layout.addLayout(character_layout)
        main_layout.addLayout(character_description_layout)
        main_layout.addLayout(list_of_characters_layout)
        main_layout.addLayout(incoming_layout)
        main_layout.addLayout(outgoing_layout)
        main_layout.addLayout(button_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect signals and slots
        self.button_send.clicked.connect(self.send_message)
        self.button_connect.clicked.connect(self.connect_to_server)
        self.button_disconnect.clicked.connect(self.disconnect_from_server)
        self.button_send_character.clicked.connect(self.send_character)
        self.button_send_start.clicked.connect(self.send_start)
        self.textbox_output.keyPressEvent = self.handle_key_press

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
        '''Handle connecting to the server'''

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
        self.button_send_character.setEnabled(True)
        self.button_send_start.setEnabled(True)
        
        # Create and start the receive messages thread
        self.receive_thread = ReceiveMessagesThread(self.socket)
        self.receive_thread.message_received.connect(self.receive_message_handler)
        self.receive_thread.start()
    
    def disconnect_from_server(self):
        '''Disconnect from the server by sending a LEAVE message and closing the socket'''
        self.button_connect.setEnabled(True)
        self.button_disconnect.setEnabled(False)
        self.button_send.setEnabled(False)
        self.textbox_ip.setEnabled(True)
        self.textbox_port.setEnabled(True)
        self.character_name.setEnabled(True)
        self.attack_value.setEnabled(True)
        self.defense_value.setEnabled(True)
        self.regen_value.setEnabled(True)
        self.health_value.setEnabled(True)
        self.gold_value.setEnabled(True)
        self.room_value.setEnabled(True)
        self.character_description.setEnabled(True)
        self.button_send_character.setEnabled(False)
        self.button_send_start.setEnabled(False)
        main_window.game_info.setText("")
        main_window.version_info.setText("")
        lurk.Leave.send_leave(self.socket)

    def receive_message_handler(self, message):
        # Append received message to incoming messages text box
        self.textbox_input.append(message)
    
    def send_start(self):
        lurk.Start.send_start(self.socket)
    
    def send_character(self):
        name = self.character_name.text()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Name must be a valid string.")
            return
        if len(name) > 32:
            QMessageBox.warning(self, "Invalid Name", "Name must be less than 32 characters.")
            return
        flag = self.auto_join_fight.isChecked()
        if flag is True:
            flag = 255 #Testing
        flag = 128
        attack = self.attack_value.value()
        print(f"DEBUG: attack: {attack}")
        defense = self.defense_value.value()
        regen = self.regen_value.value()
        if attack + defense + regen > 100:          # This shouldn't be hardcoded, but grabbed from initial_points of server
            QMessageBox.warning(self, "Invalid Stats", "Total stats must be less than 100.")
            return
        health = self.health_value.value()
        gold = self.gold_value.value()
        room = self.room_value.value()
        description = self.character_description.text()
        description_len = len(description)
        
        player = lurk.Character(name, flag, attack, defense, regen, health, gold, room, description_len, description)
        print(f"DEBUG: Sending CHARACTER: {player}")
        lurk.Character.send_character(self.socket, player)

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
                print(f"{Fore.WHITE}DEBUG: Received ACCEPT: {lurk_type}")
                self.message_received.emit(f"Server accepted message type {accept.accept_type}")
            elif lurk_type == lurk.ROOM:
                room = lurk.Room.recv_room(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received ROOM: {room}")
                self.message_received.emit(f"Room {room.number}: {room.description}")
            elif lurk_type == lurk.CHARACTER:
                player = lurk.Character.recv_character(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received CHARACTER: {player}")
                if player.name.replace('\x00', '') == main_window.character_name.text(): # If the character is the one we're playing
                    print(f"DEBUG: Received CHARACTER is the one we're playing: {player}")
                    main_player = player
                    main_window.character_name.setText(main_player.name)
                    main_window.character_name.setEnabled(False)
                    main_window.attack_value.setValue(main_player.attack)
                    main_window.attack_value.setEnabled(False)
                    main_window.defense_value.setValue(main_player.defense)
                    main_window.defense_value.setEnabled(False)
                    main_window.regen_value.setValue(main_player.regen)
                    main_window.regen_value.setEnabled(False)
                    main_window.health_value.setValue(main_player.health)
                    main_window.health_value.setEnabled(False)
                    main_window.gold_value.setValue(main_player.gold)
                    main_window.gold_value.setEnabled(False)
                    main_window.room_value.setValue(main_player.room)
                    main_window.room_value.setEnabled(False)
                    main_window.character_description.setText(main_player.description)
                    main_window.character_description.setEnabled(False)
                else:
                    main_window.list_of_characters.append(f"{player.name}: {player.attack} {player.defense} {player.regen} {player.health} {player.gold} is in room {player.room}")
            elif lurk_type == lurk.GAME:
                game = lurk.Game.recv_game(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received GAME: {game}")
                #self.message_received.emit(f"Server has {game.initial_points} initial points and a stat limit of {game.stat_limit}")
                #self.message_received.emit(f"{game.description}")
                main_window.game_info.setText(f"Initial Points: {game.initial_points}, Stat Limit: {game.stat_limit}\n{game.description}")
            elif lurk_type == lurk.LEAVE:
                print(f"{Fore.WHITE}DEBUG: Received LEAVE: {lurk_type}")
            elif lurk_type == lurk.CONNECTION:
                connection = lurk.Connection.recv_connection(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received CONNECTION: {connection}")
            elif lurk_type == lurk.VERSION:
                version = lurk.Version.recv_version(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received VERSION: {version}")
                #self.message_received.emit(f"LURK Version {version.major}.{version.minor} with extensions: {version.extensions}")
                main_window.version_info.setText(f"LURK Version {version.major}.{version.minor} with extension length: {version.extensions_len}")
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
