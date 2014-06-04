#-*- encoding:UTF-8 -*-
__author__ = 'gzs2478'
import Server
from Service import Service
class LoginService(Service):
    serviceID = 1001
    def __init__(self,parent = None):
        Service.__init__(self,self.serviceID,parent)
        self.initData()

    def initData(self):
        self.registers({\
                        1001 : self.loginHandler\
                        })

    def loginHandler(self,msg,player):
        try:
            print "Login Handler!!"
            print msg,player
            server = self.parent.parent
            data = msg['data']
            if self.server.hasNicknameInConnectedClients(data['nickname']):
                server.sendToClient(player.connectID,1001,1002,{})
                return
            player.nickname = data['nickname']

            password = player.getPasswordByNickname(player.nickname,server)

            if password == False:
                self.signUpPlayer(data,player)
                server.sendToClient(player.connectID,1001,1001,{'is_first_login':True,'table_col_num':5,'table_row_num':6})
            else:
                if password == data['password']:
                    player.updatePlayerInfoWithNicknameFromDatabase()
                    server.sendToClient(player.connectID,1001,1001,{'is_first_login':False,'table_col_num':5,'table_row_num':6})
                else:
                    server.sendToClient(player.connectID,1001,1002,{})
        except BaseException,e:
            print "LoginHandler Error"
            print e
            print data


    def signUpPlayer(self,playerInfo,player):
        try:
            #print "SignUpPlayer!!",playerInfo['nickname'],playerInfo['password']

            server = self.parent.parent
            connect = server.database.connect()
            cursor = connect.cursor()
            sqlCommand = 'INSERT INTO player(nickname,password) VALUES("%s","%s")'%(playerInfo['nickname'],playerInfo['password'])
            print sqlCommand
            cursor.execute(sqlCommand)
            print "Cursor Execute!"
            connect.commit()
            cursor.close()
            connect.close()

            player.updatePlayerInfoWithNicknameFromDatabase()
        except BaseException,e:
            self.parent.parent.log("Error while signup Player!")
            print e
            print playerInfo
            #print sqlCommand



