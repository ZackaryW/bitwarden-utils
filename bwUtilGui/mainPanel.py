import logging
import os
from PySide6.QtWidgets import QMainWindow, QToolBar, QStatusBar, QVBoxLayout, QPushButton, QWidget
from PySide6.QtGui import QAction, QIcon, Qt, QFont
from bwUtil.caller import BwClient
from bwUtilGui.clientDialog import ClientResolveDialog
from bwUtilGui.cmdWidget import CmdWidget
import bwUtilGui.styler as styler
from bwUtilGui.loginDialog import LoginDialog

class MainPanel(QMainWindow):
    def __init__(self, bw_client : BwClient, *args, **kwargs):
        super(MainPanel, self).__init__(*args, **kwargs)
        self.bw_client = bw_client
        self._bw_temp_path = None

        self.setWindowTitle("Bitwarden-Utils")

        self.resize(400, 300)

        self.show()
        self._initButtons()
        self._createStatusBar()
        self._resolveVisuals()

    def _initButtons(self):
        self._button_font = QFont("Arial", 30)

        # button box vertical layout
        self.button_grid = QVBoxLayout(self)
        # set button size
        self.button_grid.setContentsMargins(2, 2, 2, 2)
        self.button_grid.setSpacing(10)

        self.button_cli_client = QPushButton("CLI Client")
        self.button_cli_client.setStatusTip("Resolve CLI Client")
        self.button_cli_client.clicked.connect(self._clientResolveDialog)
        self.button_cli_client.setFont(self._button_font)
        self.button_cli_client_toggle = False
        styler.set_button_incomplete(self.button_cli_client)

        self.button_login = QPushButton("Login")
        self.button_login.setStatusTip("Login to Bitwarden")
        self.button_login.clicked.connect(self._createLoginDialog)
        self.button_login.setFont(self._button_font)
        styler.set_button_incomplete(self.button_login)

        self.widget_run_command = CmdWidget(self)
        self.widget_run_command.setEnabled(False)

        self.button_exit = QPushButton("Exit")
        self.button_exit.setStatusTip("Exit Bitwarden-Utils")
        self.button_exit.clicked.connect(self.close)
        self.button_exit.setFont(self._button_font)

        self.button_grid.addWidget(self.button_cli_client)
        self.button_grid.addWidget(self.button_login)
        self.button_grid.addWidget(self.widget_run_command)
        self.button_grid.addWidget(self.button_exit)
        
        self.button_grid.setAlignment(Qt.AlignTop)

        # add
        widget = QWidget()
        widget.setLayout(self.button_grid);
        self.setCentralWidget(widget)
    
    def _resolveVisuals(self):
        if self.bw_client is None:
            return

        if not self.widget_run_command.isEnabled():
            self.widget_run_command.setEnabled(True)

        if not self.button_cli_client_toggle:
            styler.set_button_complete(self.button_cli_client, disable=False)
            self.button_cli_client.setText("CLI Client: " + self.bw_client.version)
            self.button_cli_client.setStatusTip("Resolved CLI Client: " + self.bw_client.version)
            self.button_cli_client_toggle = True

        if self.button_login.isEnabled() and self.bw_client.isLoggedIn is not None:
            styler.set_button_complete(self.button_login)
            self.button_login.setText("Logged In as " + self.bw_client.isLoggedIn)
            self.button_login.setStatusTip("Logged In as " + self.bw_client.isLoggedIn)
     
    def _openBwLocation(self):
        if self.bw_client is None:
            return
        # open bitwarden location
        os.startfile(os.path.dirname(self.bw_client.path))

    def _createLoginDialog(self):
        dialog = LoginDialog(self)
        dialog.exec()
        # if rejected
        if not dialog.result():
            return
        usrname, password = dialog.get_username(), dialog.get_password()
        print(usrname, password)
    
    def _clientResolveDialog(self):
        if self.button_cli_client_toggle:
            return self._openBwLocation()
            
        dialog = ClientResolveDialog(self)
        dialog.exec()
        self._bw_temp_path = dialog.temppath
        
        self.bw_client = BwClient.resolve(dialog.file_path)
        
        self._resolveVisuals()

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("I'm the Status Bar")
        self.setStatusBar(status)

    # on exit
    def closeEvent(self, event) -> None:
        del self.bw_client
        if self._bw_temp_path is not None:
            self._bw_temp_path.cleanup()
            logging.info("Cleaned up temporary directory")
        return super().closeEvent(event)