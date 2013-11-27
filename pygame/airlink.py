#!/usr/bin/env python

# Test file to try out Airlink IP CAM -- 2/4/09 MEF

import sys, time, pygame, httplib
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((640,480),0,32)

h=httplib.HTTP('192.168.1.7')
h.putrequest('GET','VIDEO.CGI')
h.putheader('Accept','text/html')
h.putheader('Accept','image/jpeg')
h.endheaders()
errcode,errmsg,headers=h.getreply()
#f = h.getresponse()
f=h.getfile()
#<if errcode is 200 go on the the next part>

while 1:
    for event in pygame.event.get():
        if event.type == QUIT:  
            sys.exit(0)
    data=f.readline()
    if data[0:15]=='Content-length:':
        count=int(data[16:])
        n=f.readline()  # skip over Content-type: image/jpeg\n'
        n=f.readline()  # skip over \n'
        s = f.read(count)
        p=file('tempfile','wb')
        p.write(s)
        p.close()
        background = pygame.image.load('tempfile').convert()
        screen.blit(background, (0,0))
        pygame.display.update()
        #<trigger main thread to display image from tempfile>

