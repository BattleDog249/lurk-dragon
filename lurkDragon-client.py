"""Logan's LURK Client"""
#!/usr/bin/env python3

import lurk
import socket
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLineEdit
)

from colorama import Fore

class Window(QMainWindow):
    pass

# Variables defining host address & port of server to connect to
#HOST = 'localhost'
#PORT = 5010

# Connect to the server
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST, PORT))

app = QApplication([])
window = QWidget()
window.setWindowTitle("LurkDragon")

layout = QVBoxLayout()
layout.addWidget(QPushButton("Connect to Server"))
layout.ipTextBox = QLineEdit()
layout.addWidget(QPushButton("Center"))
layout.addWidget(QPushButton("Bottom"))
window.setLayout(layout)

window.show()
sys.exit(app.exec())