"""Logan's LURK Client"""
#!/usr/bin/env python3

# Isoptera IP: 74.118.22.194

import socket
import sys
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator, QKeySequence
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QSplitter, QMessageBox, QLabel, QSpinBox, QCheckBox, QGroupBox, QGridLayout

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
        self.setMinimumSize(700, 600)
        
        # Create and configure server connection info widgets
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
        
        self.label_version = QLabel()
        self.label_version.setText("LURK Version: ")
        self.label_version.setWordWrap(True)
        
        self.label_extensions = QLabel()
        self.label_extensions.setText("Extensions: ")
        self.label_extensions.setWordWrap(True)
        
        self.label_init_points = QLabel()
        self.label_init_points.setText("Initial Points: ")
        self.label_init_points.setWordWrap(True)
        
        self.label_stat_limit = QLabel()
        self.label_stat_limit.setText("Stat Limit: ")
        self.label_stat_limit.setWordWrap(True)
        
        self.label_game_description = QLabel()
        self.label_game_description.setText("Description: ")
        self.label_game_description.setWordWrap(True)
        
        # Create and configure character info widgets
        self.character_box = QGroupBox("Character Info")
        
        self.character_name = QLineEdit()
        self.character_name.setMaxLength(32)
        self.character_name.setPlaceholderText("Name")
        
        self.auto_join_fight = QCheckBox("Join fights?")
        
        self.attack_value = QSpinBox()
        self.attack_value.setRange(0, 65535)
        self.attack_value.setSuffix(" Attack")
        
        self.defense_value = QSpinBox()
        self.defense_value.setRange(0, 65535)
        self.defense_value.setSuffix(" Defense")
        
        self.regen_value = QSpinBox()
        self.regen_value.setRange(0, 65535)
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
        self.character_description.setPlaceholderText("Description")
        
        self.button_send_character = QPushButton("Character")
        self.button_send_character.setEnabled(False)
        
        self.button_send_start = QPushButton("Start")
        self.button_send_start.setEnabled(False)
        
        self.list_of_characters = QTextEdit()
        self.list_of_characters.setPlaceholderText("No NPCs or Players in current room")
        self.list_of_characters.setReadOnly(True)
        
        self.list_of_monsters = QTextEdit()
        self.list_of_monsters.setPlaceholderText("No Monsters in current room")
        self.list_of_monsters.setReadOnly(True)
        
        # Create and configure room info widgets
        self.room_box = QGroupBox("Room Info")
        
        self.current_room = QTextEdit()
        self.current_room.setPlaceholderText("No room info available")
        self.current_room.setReadOnly(True)
        
        self.connections = QTextEdit()
        self.connections.setPlaceholderText("No connections available")
        self.connections.setReadOnly(True)
        
        self.changeroom = QLineEdit()
        self.changeroom.setPlaceholderText("Room number to change to")
        
        self.button_send_changeroom = QPushButton("Change Room")
        self.button_send_changeroom.setEnabled(False)
        
        # Create and configure incoming messages widgets
        self.textbox_input = QTextEdit()
        self.textbox_input.setPlaceholderText("Messages from server will appear here")

        # Create layouts
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        incoming_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        connection_layout = QGridLayout()
        character_layout = QGridLayout()
        room_layout = QHBoxLayout()
        
        # Add widgets to layouts
        connection_layout.addWidget(self.textbox_ip, 0, 0)
        connection_layout.addWidget(self.textbox_port, 0, 1)
        connection_layout.addWidget(self.button_connect, 0, 2)
        connection_layout.addWidget(self.button_disconnect, 0, 3)
        connection_layout.addWidget(self.label_version, 1, 0, 1, 3)
        connection_layout.addWidget(self.label_extensions, 1, 3, 1, 3)
        connection_layout.addWidget(self.label_stat_limit, 2, 3, 1, 3)
        connection_layout.addWidget(self.label_init_points, 2, 0, 1, 3)
        connection_layout.addWidget(self.label_game_description, 3, 0, 1, 8)
        self.connection_box.setLayout(connection_layout)
        
        character_layout.addWidget(self.character_name, 0, 0)
        character_layout.addWidget(self.auto_join_fight, 0, 1)
        character_layout.addWidget(self.attack_value, 0, 2)
        character_layout.addWidget(self.defense_value, 0, 3)
        character_layout.addWidget(self.regen_value, 0, 4)
        character_layout.addWidget(self.health_value, 0, 5)
        character_layout.addWidget(self.gold_value, 0, 6)
        character_layout.addWidget(self.room_value, 0, 7)
        character_layout.addWidget(self.button_send_character, 0, 8)
        character_layout.addWidget(self.character_description, 1, 0, 1, 8)
        character_layout.addWidget(self.button_send_start, 1, 8)
        character_layout.addWidget(self.list_of_characters, 2, 0, 1, 4)
        character_layout.addWidget(self.list_of_monsters, 2, 4, 1, 4)
        self.character_box.setLayout(character_layout)
        
        room_layout.addWidget(self.current_room)
        room_layout.addWidget(self.connections)
        room_layout.addWidget(self.changeroom)
        room_layout.addWidget(self.button_send_changeroom)
        self.room_box.setLayout(room_layout)

        # Add layouts to main layout
        main_layout.addWidget(self.connection_box)
        main_layout.addWidget(self.character_box)
        main_layout.addWidget(self.room_box)
        main_layout.addLayout(incoming_layout)
        main_layout.addLayout(button_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect signals and slots
        self.button_connect.clicked.connect(self.connect_to_server)
        self.button_disconnect.clicked.connect(self.disconnect_from_server)
        self.button_send_character.clicked.connect(self.send_character)
        self.button_send_start.clicked.connect(self.send_start)

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
        try:
            socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_obj.connect((server_ip, server_port))
        except:
            QMessageBox.warning(self, "Connection Error", "Failed to connect to server.")
            return

        # Save the socket object and disable the IP address and port fields
        self.socket = socket_obj
        self.button_connect.setEnabled(False)
        self.button_disconnect.setEnabled(True)
        self.textbox_ip.setEnabled(False)
        self.textbox_port.setEnabled(False)
        self.button_send_character.setEnabled(True)
        self.button_send_start.setEnabled(True)
        self.button_send_changeroom.setEnabled(True)
        
        # Create and start the receive messages thread
        self.receive_thread = ReceiveMessagesThread(self.socket)
        self.receive_thread.message_received.connect(self.receive_message_handler)
        self.receive_thread.start()
    
    def disconnect_from_server(self):
        '''Disconnect from the server by sending a LEAVE message and closing the socket'''
        self.button_connect.setEnabled(True)
        self.button_disconnect.setEnabled(False)
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
        self.label_version.setText("LURK Version: ")
        self.label_extensions.setText("Extensions: ")
        self.label_init_points.setText("Initial Points: ")
        self.label_stat_limit.setText("Stat Limit: ")
        self.label_game_description.setText("Description: ")
        try:
            lurk.Leave.send_leave(self.socket)
        except:
            pass
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
        if not description:
            QMessageBox.warning(self, "Invalid Description", "Description must be a valid string.")
            return
        description_len = len(description)
        
        player = lurk.Character(name, flag, attack, defense, regen, health, gold, room, description_len, description)
        print(f"DEBUG: Sending CHARACTER: {player}")
        lurk.Character.send_character(self.socket, player)

class ReceiveMessagesThread(QThread):
    message_received = pyqtSignal(object)
    room_received = pyqtSignal(object)  # Testing
    connection_received = pyqtSignal(object) # Testing

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
                #self.message_received.emit(f"Room {room.number}: {room.description}")
                main_window.current_room.setPlainText(f"Room {room.number}: {room.name}\n{room.description}")
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
                main_window.label_init_points.setText(f"Initial Points: {game.initial_points}")
                main_window.label_stat_limit.setText(f"Stat Limit: {game.stat_limit}")
                main_window.label_game_description.setText(f"Description: {game.description}")
            elif lurk_type == lurk.LEAVE:
                print(f"{Fore.WHITE}DEBUG: Received LEAVE: {lurk_type}")
            elif lurk_type == lurk.CONNECTION:
                connection = lurk.Connection.recv_connection(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received CONNECTION: {connection}")
                main_window.connections.setPlainText(f"Room {connection.number}: {connection.name}\n{connection.description}")
            elif lurk_type == lurk.VERSION:
                version = lurk.Version.recv_version(self.socket_obj)
                print(f"{Fore.WHITE}DEBUG: Received VERSION: {version}")
                #self.message_received.emit(f"LURK Version {version.major}.{version.minor} with extensions: {version.extensions}")
                main_window.label_version.setText(f"LURK Version: {version.major}.{version.minor}")
                main_window.label_extensions.setText(f"Extensions: {version.extensions}")
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
