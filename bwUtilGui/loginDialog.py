from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout, QMessageBox

# login dialog
class LoginDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(LoginDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Login")
        self.resize(400, 200)
        # no resize
        self.setFixedSize(self.size())
        self.setLayout(self._create_layout())

    def _create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Username"))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Password"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        layout.addWidget(QLabel("TOTP"))
        self.totp = QLineEdit()
        layout.addWidget(self.totp)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.buttons)
        self.buttons.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.buttons.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        return layout

    def get_username(self):
        return self.username.text()

    def get_password(self):
        return self.password.text()

    def get_totp(self):
        text = self.totp.text()
        if not text:
            return None
        return text

    def reject(self):
        self.password.clear()
        self.username.clear()
        return super(LoginDialog, self).reject()

    def clear(self):
        self.password.clear()
        self.username.clear()
        self.totp.clear()

    def accept(self, *args, **kwargs):
        
        password = self.get_password()
        username = self.get_username()

        # if empty
        if not username or not password:
            # make a popup
            QMessageBox.warning(self, "Error", "Missing username or password")
            return self.clear()

        if "@" not in username:
            # make a popup
            QMessageBox.warning(self, "Error", "Invalid username, must be an email address")
            return self.clear()
        
        # if valid
        return super(LoginDialog, self).accept(*args, **kwargs)
