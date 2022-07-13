import sys
import os
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_path)

from PySide6 import QtWidgets
# from PySide2 import QtWidgets
# from PyQt5 import QtWidgets
from qt_material import apply_stylesheet
from bwUtil.caller import BwClient

from bwUtilGui.mainPanel import MainPanel
# create the application and the main window
app = QtWidgets.QApplication(sys.argv)
try:
    path=sys.argv[1]
except:
    path = None
bw_client = BwClient.resolve(path)
window = MainPanel(bw_client=bw_client)

# setup stylesheet
apply_stylesheet(app, theme='dark_teal.xml')

# run
window.show()
app.exec()