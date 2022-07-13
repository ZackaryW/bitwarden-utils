import logging
import os
from PySide6.QtWidgets import QMainWindow, QToolBar, QStatusBar, QVBoxLayout, QPushButton, QWidget
from PySide6.QtGui import QAction, QIcon, Qt, QFont
from bwUtil.caller import BwClient
from bwUtilGui.clientDialog import ClientResolveDialog
from bwUtilGui.cmdWidget import CmdWidget, CmdDialog
from bwUtilGui.exportDialog import ExportProgress
import bwUtilGui.styler as styler
from bwUtilGui.loginDialog import LoginDialog

class MainPanel(QMainWindow):
    def __init__(self, bw_client : BwClient, *args, **kwargs):
        super(MainPanel, self).__init__(*args, **kwargs)
        self.bw_client : BwClient = bw_client
        self._bw_temp_path = None
        self.consoleDialog = CmdDialog(self)
        self.loginDialog = LoginDialog(self)
        self.exportDialog = ExportProgress(self)

        self.setWindowTitle("Bitwarden-Utils")

        self.resize(500, 400)

        self.show()
        self._initButtons()
        self._createStatusBar()
        self._resolveVisuals()

    def _initButtons(self):
        self._button_font = QFont("Arial", 30)
        widget = QWidget(self)
        # button box vertical layout
        self.button_grid = QVBoxLayout()
        # set button size
        self.button_grid.setContentsMargins(2, 2, 2,2)
        self.button_grid.setSpacing(10)

        self.button_cli_client = QPushButton("CLI Client")
        self.button_cli_client.setStatusTip("Resolve CLI Client")
        self.button_cli_client.clicked.connect(self._clientResolveDialog)
        self.button_cli_client.setFont(self._button_font)
        self.button_cli_client_toggle = False
        styler.set_button_incomplete(self.button_cli_client)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self._usrAndPassDialog)
        self.button_login.setDisabled(True)
        self.button_login.setFont(self._button_font)

        self.button_batch_attchment = QPushButton("Export All Attachments")
        self.button_batch_attchment.setDisabled(True)
        self.button_batch_attchment.setFont(self._button_font)
        self.button_batch_attchment.clicked.connect(self.exportDialog.exec)

        self.widget_run_command = CmdWidget(self,console=self.consoleDialog)
        self.widget_run_command.setEnabled(False)

        self.button_logout = QPushButton("Logout")
        self.button_logout.clicked.connect(self._logoutBw)
        self.button_logout.setFont(self._button_font)

        self.button_exit = QPushButton("Exit")
        self.button_exit.setStatusTip("Exit Bitwarden-Utils")
        self.button_exit.clicked.connect(self.close)
        self.button_exit.setFont(self._button_font)

        self.button_grid.addWidget(self.button_cli_client)
        self.button_grid.addWidget(self.button_login)
        self.button_grid.addWidget(self.button_batch_attchment)        
        self.button_grid.addWidget(self.widget_run_command)
        self.button_grid.addWidget(self.button_logout)
        self.button_grid.addWidget(self.button_exit)
        
        self.button_grid.setAlignment(Qt.AlignTop)

        # add
        
        widget.setLayout(self.button_grid);
        self.setCentralWidget(widget)

    def _logoutBw(self):
        self.bw_client.logout()
        self._resolveVisuals()

    def _resolveVisuals(self):
        if self.bw_client is None:
            return

        if not self.button_cli_client_toggle:
            styler.set_button_complete(self.button_cli_client, disable=False)
            self.button_cli_client.setText("CLI Client: " + self.bw_client.version)
            self.button_cli_client.setStatusTip("Resolved CLI Client: " + self.bw_client.version)
            self.button_cli_client_toggle = True

        if self.bw_client.session is not None and self.bw_client.isLoggedIn is not None:
            styler.set_button_complete(self.button_login)
            self.button_login.setText("Logged In as " + self.bw_client.isLoggedIn)
            self.button_login.setStatusTip("Logged In as " + self.bw_client.isLoggedIn)
            self.widget_run_command.setEnabled(True)
        elif self.bw_client.session is None and self.bw_client.isLoggedIn is not None: 
            styler.set_button_incomplete(self.button_login)
            self.button_login.setText("(Need Unlock) Logged In as " + self.bw_client.isLoggedIn)
            self.button_login.setStatusTip("(Need Unlock) Logged In as " + self.bw_client.isLoggedIn)
            self.widget_run_command.setEnabled(False)
        else:
            styler.set_button_incomplete(self.button_login)
            self.button_login.setText("Login")
            self.button_login.setStatusTip("Login to Bitwarden")
            self.widget_run_command.setEnabled(False)
     
        if self.bw_client.session is None:
            self.button_batch_attchment.setDisabled(True)
        else:
            self.button_batch_attchment.setDisabled(False)
            

    def _openBwLocation(self):
        if self.bw_client is None:
            return
        # open bitwarden location
        os.startfile(os.path.dirname(self.bw_client.path))

    def _usrAndPassDialog(self):
        if self.bw_client.isLoggedIn is not None:
            self.loginDialog.username.setText(self.bw_client.isLoggedIn)
            self.loginDialog.username.setEnabled(False)

        self.loginDialog.exec()
        # if rejected
        if not self.loginDialog.result():
            return
        usrname = self.loginDialog.get_username()
        password = self.loginDialog.get_password()
        totp = self.loginDialog.get_totp()

        if self.bw_client.isLoggedIn is not None:
            res = self.bw_client.unlock(password)
        else:
            self.bw_client.login(usrname, password, totp)
        
        self._resolveVisuals()
    
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