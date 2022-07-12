from PySide6.QtWidgets import (
    QWidget,QVBoxLayout, QLineEdit, QPushButton, QDialog, QTextEdit
)


class CmdDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(CmdDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Command")
        self.resize(400, 200)
        self.setFixedSize(self.size())
        self.setLayout(self._create_layout())

    def _create_layout(self):
        layout = QVBoxLayout()

        self.console = QTextEdit()
        self.console.setReadOnly(True)

        layout.addWidget(self.console)
        
        return layout


class CmdWidget(QWidget):
    # a vertical box layout with a input field and a button

    def __init__(self, *args, **kwargs):
        super(CmdWidget, self).__init__(*args, **kwargs)
        self.setLayout(self._create_layout())

    def _create_layout(self):
        layout = QVBoxLayout()
        self.cmd = QLineEdit()
        layout.addWidget(self.cmd)

        self.button = QPushButton("Run")
        layout.addWidget(self.button)
        
        return layout

    def run_cmd(self, *args):
        pass
