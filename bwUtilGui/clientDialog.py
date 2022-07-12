import os
import tempfile
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout, QMessageBox, QPushButton,
    QFileDialog
)
from bwUtil.download import secureDownloadMethod
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

    def _download_file(self):
        self.temppath = secureDownloadMethod()
        self.file_path = None
        for file in os.listdir(self.temppath.name):
            file_path = os.path.join(self.temppath.name, file)
            if file.startswith("bw") and os.path.isfile(file_path):
                self.file_path = file_path
                self.accept()

    def _select_file(self):
        # file selection dialog
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        # name start with bw
        file_dialog.setNameFilter("bw*")
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setLabelText(QFileDialog.Accept, "Select")
        file_dialog.setLabelText(QFileDialog.Reject, "Cancel")
        file_dialog.setWindowTitle("Select Bitwarden Client")
        file_dialog.setDirectory(os.getcwd())
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        # allow only 1 selection
        file_dialog.exec_()
        self.file_path = file_dialog.selectedFiles()[0]
        if self.file_path and os.path.isfile(self.file_path) and os.path.exists(self.file_path):
            self.accept()
            