#-*- encoding:UTF-8 -*-
__author__ = 'gzs2478'
import Server
from Service import Service
import Player

class Desk(object):
    def __init__(self):
        self.players = {}
        self.isPlaying = False
    def addPlayer(self,player):
        if(len(self.players)<2):
            if(not self.players.has_key(player.connectID)):
                print "---------------------------------------"
                print "Adding players:",player.connectID
                print self.players
                print "---------------------------------------"
                if(type(player) == type({})):
                    print "AddPlayer Dict"
                    self.players[player.connectID] = player
                else:
                    print "Adding Player Info"
                    playerInfo = {}
                    playerInfo["nickname"] = player.nickname
                    playerInfo['id'] = player.playerID
                    playerInfo['win_times'] = player.winTime
                    playerInfo['lose_times'] = player.loseTime
                    playerInfo['draw_times'] = player.drawTime
                    self.players[player.connectID] = playerInfo

                return True
            else:
                print "already has key!"
                return False
        else:
            return False

    def leave(self,connectID):
        print "leaving Desk ",connectID
        print self.players.keys()
        if self.players.has_key(connectID):
            print connectID," leaving!!!"
            del self.players[connectID]
            return True
        else:
            return False

    def play(self):
        if(len(self.players)==2 and self.isPlaying == False):
            self.isPlaying = True
            return True
        else:
            return False
    def end(self):
        if(self.isPlaying == True):
            self.isPlaying = False
            return True
        else:
            return False

class HallService(Service):
    serviceID = 1002
    def __init__(self,parent):
        Service.__init__(self,self.serviceID,parent)
        self.initData()

    def initData(self):
        self.registers({\
                        1001 : self.arriveHallHandler,\
                        1002 : self.sendMessageHandler,\
                        1003 : self.leaveHallHandler,\
                        1004 : self.chooseDeskHandler,\
                        1005 : self.leaveDeskHandler,\
                        1006 : self.startGameHandler,\
                        1007 : self.endGameHandler\
                        })
        self.playersInHall = {}
        self.chatMessage = []
        self.desks = []
        for rowNum in xrange(6):
            row = []
            for colNum in xrange(5):
                row.append(Desk())
            self.desks.append(row)
        self.server = self.parent.parent

    def leaveHall(self,connectID):
        if self.playersInHall.has_key(connectID):
            del self.playersInHall[connectID]

            for rowNum in xrange(len(self.desks)):
                row = self.desks[rowNum]
                for colNum in xrange(len(row)):
                    self.desks[rowNum][colNum].leave(connectID)

            self.broadcastOnlineList()
            self.broadcastDeskInfo()

    def arriveHallHandler(self,msg,player):
        self.playersInHall[player.connectID] = player
        self.broadcastOnlineList()
        deskInfos = self.getCurrentDeskInfos()
        players = self.getCurrentRankList()
        self.server.sendToClient(player.connectID,1002,1003,{"desk_infos":deskInfos})
        self.server.sendToClient(player.connectID,1002,1002,{"players":players})

    def sendMessageHandler(self,msg,player):
        data = msg['data']
        chatMessage = data['message']
        createTime = data['create_time']
        self.chatMessage.append({player.nickname:chatMessage})
        self.broadcastNewChat()

    def leaveHallHandler(self,msg,player):
        self.leaveHall(player.connectID)

    def startGameHandler(self,msg,player):
        data = msg["data"]
        deskRowNum = data['row_num']%6
        deskColNum = data['col_num']%5
        if self.desks[deskRowNum][deskColNum].play() == True:
            self.broadcastDeskInfo()

    def endGameHandler(self,msg,player):
        data = msg["data"]
        deskRowNum = data['row_num']%6
        deskColNum = data['col_num']%5
        if self.desks[deskRowNum][deskColNum].end() == False:
            self.broadcastDeskInfo()
            self.broadcastRankList()

    def chooseDeskHandler(self,msg,player):
        try:
            data = msg["data"]
            deskRowNum = int(data['row_num']%6)
            deskColNum = int(data['col_num']%5)

            info = {}
            info['row_num'] = deskRowNum
            info['col_num'] = deskColNum

            if self.desks[deskRowNum][deskColNum].addPlayer(player) == True:
                info['is_choose_desk_success'] = True
                info['player_num'] = len(self.desks[deskRowNum][deskColNum].players)
            else:
                info['is_choose_desk_success'] = False

            self.server.sendToClient(player.connectID,1002,1005,info)
            if info['is_choose_desk_success'] == True:
                self.broadcastDeskInfo()
        except BaseException,e:
            print "Error In Choose Desk Handler"
            print e
            print self.desks[deskRowNum][deskColNum]


    #todo leaving Desk Handler
    def leaveDeskHandler(self,msg,player):

        data = msg["data"]
        deskRowNum = data['row_num']%6
        deskColNum = data['col_num']%5
        print "LeaveDeskHandler:",deskRowNum,",",deskColNum
        info = {}
        if self.desks[deskRowNum][deskColNum].leave(player.connectID) == True:
            info['is_leave_desk_success'] = True
        else:
            info['is_leave_desk_success'] = False

        if info['is_leave_desk_success'] == True:
            self.broadcastDeskInfo()

    def broadcastNewChat(self):
        message = self.chatMessage[len(self.chatMessage)-1]
        for key in self.playersInHall:
            player = self.playersInHall[key]
            self.server.sendToClient(player.connectID,1002,1004,{"message":message})
    def broadcastOnlineList(self):
        players = []
        for key in self.playersInHall:
            player = self.playersInHall[key]
            players.append({
                'nickname':player.nickname,\
                'win_times':player.winTime,\
                'lose_times':player.loseTime,\
                'draw_times':player.drawTime\
            })

        for key in self.playersInHall:
            player = self.playersInHall[key]
            self.server.sendToClient(player.connectID,1002,1001,{"players":players})

    def getCurrentDeskInfos(self):
        deskInfos = []
        for row in xrange(len(self.desks)):
            for col in xrange(len(self.desks[row])):
                deskInfo = {}
                deskInfo["row_num"] = row
                deskInfo["col_num"] = col
                deskInfo["players"] = self.desks[row][col].players
                deskInfo["is_playing"] = self.desks[row][col].isPlaying
                deskInfos.append(deskInfo)
        return deskInfos

    def broadcastDeskInfo(self):
        try:
            deskInfos = self.getCurrentDeskInfos()

            for key in self.playersInHall:
                player = self.playersInHall[key]
                self.server.sendToClient(player.connectID,1002,1003,{"desk_infos":deskInfos})
        except BaseException,e:
            print "Error in broadcast Desk Info"
            print e
            print self.getCurrentRankList()
    def getCurrentRankList(self):
        connect = self.server.database.connect()
        cursor = connect.cursor()
        cursor.execute('SELECT nickname,win_times,draw_times,lose_times FROM player ORDER BY win_times DESC ')
        playerInfos = cursor.fetchall()
        players = []
        cursor.close()
        connect.close()
        print "Get Current Ranklist"
        for playerInfo in playerInfos:
            player = {}
            player['nickname'] = playerInfo[0]
            player['win_times'] = playerInfo[1]
            player['draw_times'] = playerInfo[2]
            player['lose_times'] = playerInfo[3]
            players.append(player)
        print players
        return players

    def broadcastRankList(self):
        players = self.getCurrentRankList()
        print "Broadcast Ranklist"
        print players
        for key in self.playersInHall:
            player = self.playersInHall[key]
            self.server.sendToClient(player.connectID,1002,1003,{"players":players})


