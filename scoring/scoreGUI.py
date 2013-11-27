#!/usr/bin/env python

""" 
Mech-Warfare Scoring System 
Michael E. Ferguson

This program is the main GUI
of the Mech Warfare scoring
system. 

Usage: scoreGUI.py <port>
"""

import sys, time, threading
import serial
import wx
import scorePort

MATCH_TIME = 12
MECH_HP = 20

###############################################################################
# Main window
class scoreGUI(wx.Frame):
    BT_SETUP = wx.NewId()
    BT_START = wx.NewId()
    BT_A = wx.NewId()
    BT_B = wx.NewId()
    BT_RES_A = wx.NewId()
    BT_RES_B = wx.NewId()
    BT_PAUSE = wx.NewId()
    TIMER_ID = wx.NewId()

    def __init__(self, port, baud=38400):  
        wx.Frame.__init__(self, None, -1, "Mech Warfare 2010", style = wx.DEFAULT_FRAME_STYLE)
        
        # start the port
        self.port = scorePort.scorePort(port, baud)
        self.port.match = False
        self.portThread = threading.Thread(target=self.port.run)
        self.portThread.start()        

        # get settings addresses|mechs|builders
        self.mechs = dict()
        try:
            confFile = open('mechs.conf','r').readlines()
        except:
            print "Unable to load mechs.conf"
            sys.exit(1)
        for line in confFile:   # should be addr:mech:builder:\n
            if line[0] = "#":
                continue
            v = line.split(":")
            self.mechs[v[1]] = [v[0],v[1],v[2]] # addr, mech, builder
        #print self.mechs              
    
        # window setup
        sizer = wx.GridBagSizer(5,5)

        self.clock = wx.StaticText(self, -1, "Time Remaining: " + str(MATCH_TIME) + "m 00s")
        self.clock.SetFont(wx.Font(25, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer.Add(self.clock,(0,0),wx.GBSpan(1,2),wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM,20)

        #self.A = wx.StaticText(self, -1, '20')
        self.A = wx.Button(self, self.BT_A, str(MECH_HP),size=(400,350))
        self.A.SetFont(wx.Font(150, wx.DEFAULT, wx.NORMAL, wx.BOLD))  #200
        sizer.Add(self.A, (1,0),wx.GBSpan(1,1),wx.LEFT|wx.RIGHT,50)
        self.A.mech = wx.StaticText(self, -1, 'None')
        self.A.mech.SetFont(wx.Font(30, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer.Add(self.A.mech, (2,0),wx.GBSpan(1,1),wx.ALIGN_CENTER)

        #self.B = wx.StaticText(self, -1, '20')
        self.B = wx.Button(self, self.BT_B, str(MECH_HP),size=(400,350))
        self.B.SetFont(wx.Font(150, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer.Add(self.B, (1,1),wx.GBSpan(1,1),wx.LEFT|wx.RIGHT,50)
        self.B.mech = wx.StaticText(self, -1, 'None')
        self.B.mech.SetFont(wx.Font(30, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer.Add(self.B.mech, (2,1),wx.GBSpan(1,1),wx.ALIGN_CENTER)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.pause_but = wx.Button(self, self.BT_PAUSE, 'pause')
        hbox.Add(self.pause_but)
        self.reset_a = wx.Button(self, self.BT_RES_A, 'reset A')
        hbox.Add(self.reset_a)
        self.reset_b = wx.Button(self, self.BT_RES_B, 'reset B')
        hbox.Add(self.reset_b)
        hbox.Add(wx.Button(self, self.BT_START, 'start match'))
        hbox.Add(wx.Button(self, self.BT_SETUP, 'setup'))
        sizer.Add(hbox,(3,1),wx.GBSpan(1,1),wx.ALIGN_RIGHT|wx.ALL,25) 

        # variables
        self.A.name = ""
        self.B.name = ""
        self.match = False  # is a match in progress
        self.matchStart = 0
        self.matchEnd = 0
        self.ready = False  # setup and ready to start?
        self.paused = False

        # timer for output
        self.timer = wx.Timer(self, self.TIMER_ID)
        self.timer.Start(100)
        wx.EVT_TIMER(self, self.TIMER_ID, self.onTimer)

        wx.EVT_CLOSE(self, self.onClose)        
        wx.EVT_BUTTON(self, self.BT_SETUP, self.doSetup)  
        wx.EVT_BUTTON(self, self.BT_START, self.doStart)  
        wx.EVT_BUTTON(self, self.BT_A, self.doButA)
        wx.EVT_BUTTON(self, self.BT_B, self.doButB)
        wx.EVT_BUTTON(self, self.BT_RES_A, self.doResetA)
        wx.EVT_BUTTON(self, self.BT_RES_B, self.doResetB)
        wx.EVT_BUTTON(self, self.BT_PAUSE, self.doPause)
        #wx.EVT_SIZE(self, self.OnResize)          

        self.SetSizerAndFit(sizer)
        self.Show(True)

    def doPause(self, event=None):
        if self.paused == True:
            self.matchEnd = self.matchEnd + (time.time() - self.p_time)
            self.pause_but.SetLabel("pause")
            self.paused = False
        else:
            self.p_time = time.time()
            self.pause_but.SetLabel("un-pause")
            self.paused = True

    def onClose(self, event=None):
        self.port.exitcond = True
        self.Destroy()

    def onTimer(self, event=None):
        if self.match == True and self.paused == False:
            try:
                # get scores
                A = self.port.scores[int(self.mechs[self.A.name][0])]
                if A <= 0:
                    A = 0
                    self.match = False
                B = self.port.scores[int(self.mechs[self.B.name][0])] 
                if B <= 0:
                    B = 0
                    self.match = False  
                # print scores
                self.A.SetLabel(str(A).rjust(2,"0"))
                self.B.SetLabel(str(B).rjust(2,"0"))
                # get time
                t = self.matchEnd - time.time()
                if t > 0: 
                    # update output               
                    m = int(t/60)
                    s = int(t)%60
                    self.clock.SetLabel("Time Remaining: " + str(m) + "m " + str(s).rjust(2,"0") + "s")
                else:
                    self.match = False               
            except:
                pass                
            if self.match == False: # match has ended, declare winner   
                if A > B:   
                    self.clock.SetLabel("Match Winner: " + self.A.name)
                else:
                    self.clock.SetLabel("Match Winner: " + self.B.name)  
                print time.strftime("%I.%M.%S") + ": Match Ended"
                print self.A.name, A, self.B.name, B 
                self.SendSizeEvent()        
                self.port.match = False                            

    def doSetup(self, event=None):
        dlg = SetupDialog(self, -1, "Match Setup")
        if dlg.ShowModal() == wx.ID_OK:
            self.A.name = dlg.A.GetString(dlg.A.GetSelection())
            self.B.name = dlg.B.GetString(dlg.B.GetSelection())
            print time.strftime("%I.%M.%S") + ": Match Setup between ", self.A.name, ",", self.B.name
            self.port.scores[int(self.mechs[self.A.name][0])] = MECH_HP
            self.port.scores[int(self.mechs[self.B.name][0])] = MECH_HP
            self.A.mech.SetLabel(self.A.name)
            self.B.mech.SetLabel(self.B.name)
            self.reset_a.SetLabel("reset "+self.A.name)
            self.reset_b.SetLabel("reset "+self.B.name)
        dlg.Destroy()   
        self.clock.SetLabel("Time Remaining: " + str(MATCH_TIME) + "m 00s")
        self.SendSizeEvent()    
        self.ready = True

    def doResetA(self, event=None):
        self.port.scores[int(self.mechs[self.A.name][0])] = MECH_HP

    def doResetB(self, event=None):
        self.port.scores[int(self.mechs[self.B.name][0])] = MECH_HP  

    def doStart(self, event=None):
        if self.ready == False:
            return
        # reset scores to MECH_HP
        self.port.scores[int(self.mechs[self.A.name][0])] = MECH_HP
        self.port.scores[int(self.mechs[self.B.name][0])] = MECH_HP
        # start clock
        self.matchStart = time.time()        
        self.matchEnd = self.matchStart + 60*MATCH_TIME
        self.clock.SetLabel("Time Remaining: " + str(MATCH_TIME) + "m 00s")
        self.SendSizeEvent()    
        self.match = True
        self.port.match = True
        print time.strftime("%I.%M.%S") + ": Match Started" 
    
    def doButA(self, event=None):
        if self.match == True:
            self.port.doPenalty(int(self.mechs[self.A.name][0]))
    def doButB(self, event=None):
        if self.match == True:
            self.port.doPenalty(int(self.mechs[self.B.name][0]))

    #def onResize(self, event=None):
        

###############################################################################
# the setup dialog
class SetupDialog(wx.Dialog):
    ID_COMP_BOX = wx.NewId()

    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)  

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, -1, 'Select Competitors for Match:'),0,wx.ALL, 10)
        
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.A = wx.ListBox(self, self.ID_COMP_BOX,choices=parent.mechs.keys())
        hbox1.Add(self.A)
        self.B = wx.ListBox(self, self.ID_COMP_BOX,choices=parent.mechs.keys())
        hbox1.Add(self.B,0,wx.LEFT,10)            
        vbox.Add(hbox1,0,wx.EXPAND | wx.LEFT|wx.RIGHT, 10)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, 'Ok', size=(70, 30))
        closeButton = wx.Button(self, wx.ID_CANCEL, 'Close', size=(70, 30))
        hbox.Add(okButton, 1)
        hbox.Add(closeButton, 1, wx.LEFT, 5)
        vbox.Add(hbox, 1, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
    
        self.SetSizerAndFit(vbox)


if __name__ == "__main__":
    # scoreGUI <port>
    #if len(sys.argv) < 2:
    #    print __doc__
    #else:
    app = wx.PySimpleApp()
    frame = scoreGUI('/dev/ttyUSB0') #'COM5')
    app.MainLoop()

