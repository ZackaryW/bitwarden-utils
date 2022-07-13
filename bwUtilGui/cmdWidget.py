from PySide6.QtWidgets import (
    QWidget,QVBoxLayout, QLineEdit, QPushButton, QDialog, QTextEdit
)

class CmdDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(CmdDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Command")
        self.resize(800, 400)
        self.setFixedSize(self.size())
        self.setLayout(self._create_layout())

    def _create_layout(self):
        layout = QVBoxLayout()

        self.console = QTextEdit()
        self.console.setReadOnly(True)

        layout.addWidget(self.console)
        
        return layout

    @property
    def consoleText(self):
        return self.console.toPlainText()

    @consoleText.setter
    def consoleText(self, text):
        self.console.setPlainText(text)

class CmdWidget(QWidget):
    # a vertical box layout with a input field and a button

    def __init__(self, *args,console : CmdDialog = None, **kwargs):
        super(CmdWidget, self).__init__(*args, **kwargs)
        self.setLayout(self._create_layout())
        if console is None:
            self.consoleDialog = CmdDialog(self)
        else:
            self.consoleDialog = console

    def _create_layout(self):
        layout = QVBoxLayout()
        self.cmd = QLineEdit()
        layout.addWidget(self.cmd)

        self.button = QPushButton("Run Command")
        self.button.clicked.connect(self._run)

        layout.addWidget(self.button)
        
        return layout

    def run_cmd(self, *args):
        parent = self.parent().parent()
        result = parent.bw_client.simpleRun(*self.cmd.text().split(" "))
        self.consoleDialog.consoleText = result.raw
        self.consoleDialog.exec()
        self.consoleDialog.console.clear()
        self.cmd.clear()

    def _run(self):
        return self.run_cmd(self.cmd.text().split(" "))
