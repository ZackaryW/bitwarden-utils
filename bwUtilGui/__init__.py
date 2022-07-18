"""
based on PySide6 (PyQt6)

current gui implementation is not flexible and maintainable enough to be justified for extensions
"""

if __name__ == '__main__':
    import logging
    import sys
    import os

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    # disable urlib3 logging
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_path)
    import bwUtilGui.__main__
