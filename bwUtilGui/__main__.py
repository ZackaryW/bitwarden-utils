if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    # disable urlib3 logging
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    import os
    parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    sys.path.append(parent_path)

    from PySide6 import QtWidgets
    # from PySide2 import QtWidgets
    # from PyQt5 import QtWidgets
    from qt_material import apply_stylesheet
    import sys
    from bwUtil.caller import BwClient

    from bwUtilGui.mainPanel import MainPanel
    # create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    bw_client = BwClient.resolve(path=sys.argv[1])
    window = MainPanel(bw_client=bw_client)

    # setup stylesheet
    apply_stylesheet(app, theme='dark_teal.xml')

    # run
    window.show()
    app.exec_()