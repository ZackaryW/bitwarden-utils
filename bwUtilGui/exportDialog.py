import os
import tempfile
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout, QMessageBox, QPushButton,
    QFileDialog, QProgressBar
)
from bwUtil.caller import BwClient

class ExportProgress(QDialog):
    def __init__(self, *args, **kwargs):
        super(ExportProgress, self).__init__(*args, **kwargs)
        self.setWindowTitle("Attachments Export")
        self.resize(400, 200)
        self.setFixedSize(self.size())
        self.setLayout(self._create_layout())
        self._reset()
        self.client : BwClient = self.parent().bw_client

    def _create_layout(self):
        layout = QVBoxLayout()
        # parse button
        self.stage_1_label = QLabel("")
        self.stage_2_label = QLabel("")
        self.stage_3_label = QLabel("")

        self.stage_button = QPushButton("Parse Data")
        self.stage_button.clicked.connect(self._stage_event)
        
        # progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(True)

        layout.addWidget(self.stage_1_label)
        layout.addWidget(self.stage_2_label)
        layout.addWidget(self.stage_3_label)

        layout.addWidget(self.stage_button)
        layout.addWidget(self.progress_bar)

        return layout

    def _reset(self):
        self.stage_button.setEnabled(True)

        self.data = []
        self.current_stage = 1
        self.export_folder = None

        self.stage_1_label.setText("Parse Data ⛔")
        self.stage_1_label.setHidden(True)
        self.stage_2_label.setText("Select Output Directory ⛔")
        self.stage_2_label.setHidden(True)
        self.stage_3_label.setText("Export ⛔")
        self.stage_3_label.setHidden(True)

        self.progress_bar.setValue(0)
        self.progress_bar.setHidden(True)

    def _stage_event(self):
        match self.current_stage:
            case 1:
                self._parse_data()
            case 2:
                self._select_file()
            case 3:
                self._export()
        
        if self.current_stage == 0:
            self.stage_button.setEnabled(False)

    def _parse_data(self):
        if self.client.lastSynced is None and (syncSuccess := self.client.sync()):
            pass
        elif not syncSuccess:
            pass
        
        self.stage_1_label.setHidden(False)
        
        try:
            self.data = [x for x in self.client.export_items() if "attachments" in x]
        except:
            self.data = []
            self.current_stage = 0
            return

        if len(self.data) == 0:
            self.current_stage = 0
            return
        
        self.current_stage = 2
        self.stage_1_label.setText("Parse Data ✅: {} jobs".format(len(self.data)))
        self.stage_button.setText("Select Output Directory")
        
    def _select_file(self):
        self.stage_2_label.setHidden(False)
        
        # file selection dialog
        
        file_dialog = QFileDialog(self)
        
        # select folder
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setLabelText(QFileDialog.Accept, "Select")
        file_dialog.setLabelText(QFileDialog.Reject, "Cancel")
        file_dialog.setWindowTitle("Select Export Directory")
        file_dialog.setDirectory(os.getcwd())
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        # allow only 1 selection
        file_dialog.exec()
        select_folder = file_dialog.selectedFiles()
        if not select_folder:
            self.current_stage = 2
            return
        folder = select_folder[0]
        if os.path.isdir(folder) and os.path.exists(folder):
            self.export_folder = folder
            self.current_stage = 3
            self.stage_2_label.setText("Select Output Directory ✅: {}".format(folder))
            self.stage_button.setText("Export")

    def _export(self):
        self.stage_button.setEnabled(False)
        self.stage_3_label.setHidden(False)
        self.progress_bar.setHidden(False)
        self.progress_bar.setMaximum(len(self.data))
        for count in self.client.export_attachments(
            self.export_folder, 
            self.data
        ):
            self.progress_bar.setValue(count)
            self.stage_3_label.setText(f"Export ✅: {count}/{len(self.data)}")
        self.current_stage = 0
        self.stage_3_label.setText("Export ✅: {} jobs".format(len(self.data)))
        self.stage_button.setEnabled(False)
        # repaint
        self.repaint()

    def reject(self) -> None:
        self._reset()
        return super().reject()