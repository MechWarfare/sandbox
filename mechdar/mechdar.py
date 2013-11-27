#!/usr/bin/env python
""" MechDAR Ver A.0

Copyright (c) 2009, Michael E. Ferguson
All rights reserved.
 
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 
 - Redistributions of source code must retain the above copyright notice, 
   this list of conditions and the following disclaimer.
 - Redistributions in binary form must reproduce the above copyright notice, 
   this list of conditions and the following disclaimer in the documentation 
   and/or other materials provided with the distribution.
 - Neither the name of MechDAR nor the names of its contributors 
   may be used to endorse or promote products derived from this software 
   without specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
THE POSSIBILITY OF SUCH DAMAGE.

Provides mechDAR interface, frame builder & map builder.
Can be loaded as main window, or used within any pygame surface.

http://www.vanadiumlabs.com/mechdar"""

__author__ = "Michael Ferguson <mfergs7 at gmail.com>"
__date__ = "7 February 2009"
__version__ = "$Revision: A.0 $"
__copyright__ = "Copyright 2009 Michael E. Ferguson"

import sys, time, serial, numpy, pygame, threading
from math import sin, cos, radians
from pygame.locals import *

# Robot Configuration
ROBOT_SIDE_OFFSET = 2
ROBOT_BACK_OFFSET = 1
ROBOT_FRONT_OFFSET = 1

# Map Configuration
FRAME_SIZE_X = 36           # boxes for x direction
FRAME_SIZE_Y = 36           # boxes for y direction 
FRAME_RESOLUTION = 2        # inches per box

MAX_DISTANCE = 60           # 60 inches = max distance

# a map
class mapFrame:
    def __init__(self):
        """ Initialize the map frame, all to zero. """
        self.data = numpy.zeros( (FRAME_SIZE_X, FRAME_SIZE_Y) , dtype=numpy.int16 ) 
        self.mech = pygame.image.load("mechSM.gif").convert()

    def test(self, x, y, rotation, distance):
        """ reverse of touch, returns a value """
        x = int(distance * sin(radians(rotation))/FRAME_RESOLUTION + x)
        y = int(distance * cos(radians(rotation))/FRAME_RESOLUTION + y)
        try: 
            return self.data[x][y]
        except:
            return -1

    def touch(self, rotation, distance):
        x = int(distance * sin(radians(rotation))/FRAME_RESOLUTION + (FRAME_SIZE_X/2))
        y = int(distance * cos(radians(rotation))/FRAME_RESOLUTION + (FRAME_SIZE_Y/2))
        try:
            print x, y
            if self.data[x][y] < 9:
                self.data[x][y] = self.data[x][y] + 1
        except:
            print "Boundary may be out of bounds..."
    
    def touchIR(self, rotation, distance):
        """ Register a hit at rotation and distance from robot location. """
        if distance < MAX_DISTANCE:
            self.touch(rotation-5, distance*1.05)
            self.touch(rotation, distance)
            self.touch(rotation+5, distance*1.05)           

    def untouch(self, rotation, distance):
        pass

    def printMap(self):
        print "MAP"
        irange = range(0,FRAME_SIZE_Y)
        irange.reverse()
        # send map out    
        for i in irange:
            for j in range(0,FRAME_SIZE_X):
                if j == FRAME_SIZE_X/2 and i == FRAME_SIZE_Y/2:
                    print "R",
                elif self.data[j][i] == 0:
                    print " ",                
                else:
                    print self.data[j][i],                
            print ""
        print "END MAP"
    
    def drawMap(self, surface):
        """ Draws the map on a pygame surface. """
        x = surface.get_width()
        y = surface.get_height()  
        offset = y-(y/FRAME_SIZE_Y)
        for i in range(0,FRAME_SIZE_Y): 
            for j in range(0,FRAME_SIZE_X): 
                if self.data[j][i] == 0:
                    color = (210,210,210)
                elif self.data[j][i] < 3:
                    color = (50,50,50)  
                else:   
                    color = (0,0,0)
                pygame.draw.rect(surface, color, Rect(((x/FRAME_SIZE_X)*j,offset-(y/FRAME_SIZE_Y)*i), (x/FRAME_SIZE_X,y/FRAME_SIZE_Y)))                
                self.data[j][i]       
        # draw little mech character     
        surface.blit(self.mech, (x/2 - 8,y/2 - 8)) 

class mechdar:
    """ Main class for mechdar. Converts serial port data into new frames. """
    NEW_FRAME = 0
    REG_LEFT_IR = 1
    REG_RIGHT_IR = 2
    REG_L_REAR_IR = 3
    REG_R_REAR_IR = 4
    REG_PAN_BASE = 5
    REG_SNR_BASE = 15
    END_FRAME = 25       

    def __init__(self, ser=None, port="/dev/ttyUSB0", baud=115200, invert=1, mapHook=None, threatHook=None):          
        self.invert = invert       # invert is used for whether the servo is upside down (1) or right side up (-1). 
        self.map = mapFrame()
        self.frame = mapFrame()
        self.frameCnt = 0
        # user hooks
        self.threatHook = threatHook
        self.mapHook = mapHook
        # prepare serial port
        if ser != None:
            self.ser = ser
        else:
            try:
                self.ser = serial.Serial()
                self.ser.baudrate = baud
                self.ser.port = port
                self.ser.timeout = 3
                self.ser.open()     
            except:
                print "Cannot open port", port
                sys.exit(0)   
        self.exitcond = False
        
    def readPort(self):
        """ Returns the address and value of a recieved packet. """
        while self.ser.inWaiting() == 0:
            time.sleep(0.05)
        xff = self.ser.read()   
        # make sure we really are at beginning of a packet
        if xff != "\xff":
            return self.readPort()
        while self.ser.inWaiting() == 0:
            time.sleep(0.05)
        addr = ord(self.ser.read())
        while self.ser.inWaiting() == 0:
            time.sleep(0.05)
        value = ord(self.ser.read())
        while self.ser.inWaiting() == 0:
            time.sleep(0.05)
        checksum = ord(self.ser.read())
        if (addr + value + checksum)%255 == 0:
            return (addr,value)
        else:       
            return (-1,-1)    

    def thread(self):
        """ This thread handles the serial comms. """    
        while not self.exitcond:      
            addr, reading = self.readPort()
            if addr == self.NEW_FRAME:
                print "New Frame"        
            elif addr == self.END_FRAME:
                print time.time()
                self.frame.printMap() 
                self.map = self.frame 
                self.frame = mapFrame()
                #self.map.drawMap(self.screen) 
                if self.mapHook != None:
                    self.mapHook()
                print time.time()                   
                #post_frame(thisframe)
            elif addr == self.REG_LEFT_IR:
                print "LEFTIR: -90 "+str(reading), time.time()
                self.frame.touchIR(-90,reading + ROBOT_SIDE_OFFSET)
            elif addr == self.REG_RIGHT_IR:
                print "RIGHT IR: 90 "+str(reading)
                self.frame.touchIR(90,reading + ROBOT_SIDE_OFFSET)
            elif addr == self.REG_L_REAR_IR:
                print "LEFT REAR: 190 "+str(reading)
                self.frame.touchIR(190,reading + ROBOT_BACK_OFFSET)
            elif addr == self.REG_R_REAR_IR:
                print "RIGHT REAR: 170 "+str(reading)
                self.frame.touchIR(170,reading + ROBOT_BACK_OFFSET)
            elif addr >= self.REG_PAN_BASE and addr < self.REG_SNR_BASE:
                print "PAN: " + str(-90 + (addr -self.REG_PAN_BASE)*20*self.invert) + " " + str(reading)
                self.frame.touchIR(-90 + (addr - self.REG_PAN_BASE)*20*self.invert,reading + ROBOT_FRONT_OFFSET)
            else:
                print "Bad Packet"      # added 2/02 MEF

if __name__ == "__main__":
    try:
        conf = open('mechdar.conf','r').readlines()
    except:
        print 'MechDAR: Cannot open mechdar.conf file.'
        sys.exit(0)
    pygame.init()
    pygame.display.set_caption("MechDAR A.0")
    size = 288,288
    screen = pygame.display.set_mode(size)
    if conf[1] == "True":
        window = mechdar(port=conf[0].rstrip(), invert=True)
    else:
        window = mechdar(port=conf[0].rstrip())  
    t = threading.Thread(target=window.thread)
    t.start()
    # standard PyGame event loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
                window.exitcond = True
        window.map.drawMap(screen)
        pygame.display.flip()
        #print "pygame updated", time.time()
        time.sleep(1/30)

