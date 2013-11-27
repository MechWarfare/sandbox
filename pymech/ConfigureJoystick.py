#!/usr/bin/env python

"""
PyMech Controller Ver A.0

  Copyright (c) 2009 Michael E. Ferguson.  All right reserved.

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software Foundation,
  Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

http://www.blunderingbotics.com/

This file automatically creates pyMechConf.py. Be sure
to plug in your joystick before running this file.
"""

# test for joystick
import pygame
from pygame.locals import *
from sys import exit

pygame.init()
print "*** ConfigureJoystick ***"
#print "# of joysticks found:" ,str(pygame.joystick.get_count())
try:
    stick = pygame.joystick.Joystick(0)
    stick.init()
    print "Found joystick 0"
else:
    print "Could not find joystick!"
    sys.exit(0)
# clean out any events
for event in pygame.event.get():
    pass
# now configure joystick buttons
print "Please push stick forward..."
event = pygame.event.get()
if event.type == JOYAXISMOTION:
    
for event in pygame.event.get()
    pass
print "Please push stick to the right..."

print "Please push the button you want to use for trigger..."

print "Please push the Torso Rotate button -- you will..." 

print "Please push a button to use for Torso Left Adjust -- or press enter"

print "Please push a button to use for Torso Right Adjust -- or press enter"

print "Please move the turn adjust joystick if you have one -- or press enter"



while True:
    for event in pygame.event.get():
        if event.type in (JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONUP, JOYBUTTONDOWN):      
            #event_text.append(str(event))
            print str(event)

        #event_text = event_text[-SCREEN_SIZE[1]/font_height:]
        if event.type == QUIT:  
            exit()

