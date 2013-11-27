#!/usr/bin/env python

# test for joystick
import pygame
from pygame.locals import *
from sys import exit

pygame.init()

#SCREEN_SIZE = (640,480)
#screen = pygame.display.set_mode(SCREEN_SIZE,0,32)

#font = pygame.font.SysFont("arial",16)
#font_height = font.get_linesize()
#event_text = []

print str(pygame.joystick.get_count())
stick = pygame.joystick.Joystick(0)
stick.init()

while True:
    for event in pygame.event.get():
        if event.type in (JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONUP, JOYBUTTONDOWN):      
            #event_text.append(str(event))
            print str(event)

        #event_text = event_text[-SCREEN_SIZE[1]/font_height:]
        if event.type == QUIT:  
            exit()

    #screen.fill((255,255,255))
    
    #y = SCREEN_SIZE[1] - font_height
    #for text in reversed(event_text):
    #    screen.blit( font.renderer(text
