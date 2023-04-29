"""Logan's LURK Client"""
#!/usr/bin/env python3

import lurk
import socket
import sys
import threading
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QLabel,
    QMessageBox,
    QTextEdit
)

from colorama import Fore

class ConnectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set some main window's properties
        self.setWindowTitle("Connect to Server")
        self.setFixedSize(QSize(400, 200))
        
        # Create server IP label and input box
        self.server_ip_label = QLabel(self)
        self.server_ip_label.setText("Server IP:")
        self.server_ip_label.move(50, 50)
        self.server_ip_input = QLineEdit(self)
        self.server_ip_input.move(150, 50)
        self.server_ip_input.resize(200, 30)
        
        # Create server port label and input box
        self.server_port_label = QLabel(self)
        self.server_port_label.setText("Server Port:")
        self.server_port_label.move(50, 100)
        self.server_port_input = QLineEdit(self)
        self.server_port_input.move(150, 100)
        self.server_port_input.resize(200, 30)
        
        # Create cancel button
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText("Cancel")
        self.cancel_button.move(50, 150)
        self.cancel_button.clicked.connect(self.close)
        
        # Create connect button
        self.connect_button = QPushButton(self)
        self.connect_button.setText("Connect")
        self.connect_button.move(250, 150)
        self.connect_button.clicked.connect(self.connect_to_server)

    def connect_to_server(self):
        # Isoptera IP: 74.118.22.194
        server_ip = str(self.server_ip_input.text())
        server_port = int(self.server_port_input.text())
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_skt:
                client_skt.connect((server_ip, server_port))
        except:
            QMessageBox.critical(self, "Error", "Failed to connect to server!")
            return
        
        # Connection successful, close the server window and open a new window
        self.open_new_window()
        
        return server_ip, server_port
    
    def open_new_window(self):
        # Close the server window
        self.close()

        # Open a new window
        self.new_window = MainWindow()
        self.new_window.setGeometry(100, 100, 400, 200)
        self.new_window.show()

class MainWindow(QMainWindow):
    def __init__(self, skt):
        super().__init__()
        
        self.setWindowTitle("Lurk Dragon")
        self.setGeometry(100, 100, 400, 400)
        
        # Create text box to display incoming messages
        self.incoming_messages_textbox = QTextEdit(self)
        self.incoming_messages_textbox.setReadOnly(True)
        self.incoming_messages_textbox.setGeometry(10, 10, 380, 250)
        
        # Create text box and send button to send messages
        self.send_message_textbox = QTextEdit(self)
        self.send_message_textbox.setGeometry(10, 280, 290, 100)
        self.send_message_button = QPushButton("Send", self)
        self.send_message_button.setGeometry(310, 280, 80, 100)
        self.send_message_button.clicked.connect(self.send_message)
        
        # Socket to receive messages
        self.skt = skt
        
        # Start a thread to receive messages
        self.running = True
        threading.Thread(target=self.receive_messages, daemon=True).start()
        
    def receive_messages(self, skt):
        # Connect to the server and receive messages

        while self.running:
            lurk_type = lurk.recv(skt, 1)
            if not lurk_type:
                break
            self.incoming_messages_textbox.append(lurk_type.decode())

    def send_message(self):
        # Send a message to the server
        message = self.send_message_textbox.toPlainText()
        if message:
            self.socket.sendall(message.encode())
            self.send_message_textbox.clear()

# You need one (and only one) QApplication instance per application.
app = QApplication([])

# Create a Qt widget, which will be our window.
connect_window = ConnectWindow()

connect_window.show()
sys.exit(app.exec())