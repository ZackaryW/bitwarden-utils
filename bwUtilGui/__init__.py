"""
based on PySide6 (PyQt6)

current gui implementation is not flexible and maintainable enough to be justified for extensions
"""

def create_app(logging :bool = False):
    import sys
    import os

    if logging:
        import logging

        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        # disable urlib3 logging
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    
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


if __name__ == '__main__':
    create_app(True)
    
