import os
import unittest
from bwUtil.download import downloadCli

class t_download(unittest.TestCase):
    def test_download(self):
        if os.path.exists("tests/src/bw") or os.path.exists("tests/src/bw.exe"):
            self.assertTrue(True)
            return 

        downloadCli("windows", "tests/src/")
