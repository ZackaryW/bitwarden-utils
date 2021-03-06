from PySide6.QtWidgets import QPushButton

def set_button_complete(button : QPushButton, disable : bool = True):
    if disable:
        button.setEnabled(False)
    button.setStyleSheet("border:5px solid #00ff00; color: #FFFFFF;")

def set_button_incomplete(button : QPushButton):
    button.setEnabled(True)
    button.setStyleSheet("border:5px solid #ff0000;")
