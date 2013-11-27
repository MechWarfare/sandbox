#!/usr/bin/env python

""" 
Mech-Warfare Scoring System 
Michael E. Ferguson

This program is the port handler
for the Mech Warfare scoring 
system. 

Usage: scorePort.py <port> <baud>
"""

import sys
import time
import serial

class scorePort():  
    """ This is the port handler for the Mech-Warfare Scoring System """
    def __init__(self, port="/dev/ttyUSB1", baud=38400):
        print "Mech Warfare Scoring System V1.0"    
        print "Server started, port: " + port
        # important variables
        self.ser = serial.Serial(port,baud)
        self.scores = dict()    
        self.exitcond = False   
        self.match = False #True

    def run(self):
        try:
            while not self.exitcond:
                while self.ser.inWaiting() == 0:
                    if self.exitcond:
                        return
                # 0x55 ID 255-ID HIT
                while ord(self.blockRead()) != 0x55:
                    print "No good"
                mechId = ord(self.blockRead())
                invMechId = ord(self.blockRead())
                mechHit = ord(self.blockRead())
                if (mechId + invMechId) != 0xff:
                    print time.strftime("%I.%M.%S") + ": Failed packet!", mechId, invMechId
                if self.match:
                    try:
                        self.scores[mechId] = self.scores[mechId] -1
                        print time.strftime("%I.%M.%S") + ": Hit Assessed against Mech ID ",mechId, "score=", self.scores[mechId]
                    except:
                        # first hit against this bot!
                        self.scores[mechId] = -1 
                        print time.strftime("%I.%M.%S") + ": Hit Assessed against Mech ID ",mechId, "score=", self.scores[mechId]
                else:
                    print time.strftime("%I.%M.%S") + ": Hit on Mech ID ",mechId, " ignored (No match in progess)", mechHit

        except KeyboardInterrupt:
            print "Mech-Warfare Scoring System: Exiting..."

    def doPenalty(self, ID):
        try:
            self.scores[ID] = self.scores[ID] -1
            print time.strftime("%I.%M.%S") + ": Penalty Assessed agaisnt Mech ID ",ID, "score=", self.scores[ID]
        except:
            pass 

    def blockRead(self):    
        """ A blocking read. """
        while self.ser.inWaiting() == 0:
            pass
        return self.ser.read()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        score = scorePort(sys.argv[1],sys.argv[2])
        score.run()
    elif len(sys.argv) == 2:
        score = scorePort(sys.argv[1])
        score.run()
    else:
        print __doc__

