import os
import tempfile
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout, QMessageBox, QPushButton,
    
)
# login dialog
class ClientResolveDialog(QDialog):
    def __init__(self, *args, **kwargs):
        self.file_path = None
        self.temppath : tempfile.TemporaryDirectory = None

        super(ClientResolveDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Resolve Client")
        self.resize(400, 200)
        self.setFixedSize(self.size())
        self.setLayout(self._create_layout())
        
        self.show()

    def _create_layout(self):
        layout = QVBoxLayout()
        # file selection button
        self.file_selection_button = QPushButton("Select File")
        self.file_selection_button.clicked.connect(self._select_file)

        self.download_file_button = QPushButton("Download File to temp")
        self.download_file_button.clicked.connect(self._download_file)
        
        layout.addWidget(self.file_selection_button)
        layout.addWidget(self.download_file_button)

        return layout

    