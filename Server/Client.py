#-*- encoding:UTF-8 -*-
__author__ = 'gzs2478'

import time

class Client(object):
    def __init__(self,connectID,server):
        object.__init__(self)
        try:
            self.initData(connectID,server)
        except BaseException,e:
            print time.ctime()," Error in Client InitData"
            print e
    def initData(self,connectID,server):
        self.connectID = connectID
        self.server = server
