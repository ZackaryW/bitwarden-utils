from asyncio.subprocess import Process
import os
import unittest
from bwUtil.caller import BwClient, BwCommunication, BwResponse
from pprint import pprint

class t_caller(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.client = BwClient("tests/src/bw.exe")
        except:
            self.client = BwClient("tests/src/bw")

    def test_caller(self):
        with self.client.createCommunication("--help") as proc:
            proc : BwCommunication
            print(proc.commuicateObj())

    @unittest.skip("skipping")
    def test_logout(self):
        with self.client.createCommunication("logout") as proc:
            proc : BwCommunication
            res = proc.commuicateObj()
            print(res.login_not_logged_in)
            pass

    def test_login_is_logged_in(self):
        print(self.client.isLoggedIn)
        pass