#!/usr/bin/env python

import socket, sys, signal, errno, time
import struct
import pygame
from gamestate import gamestate

class gameserver:
    def __init__( self ):
        self.gamestate = gamestate()
        self.runServerLoop = True
        self.connections = []
        self.clock = pygame.time.Clock()
        self.receivedstate = ( -1, False, False, False, False )
        signal.signal( signal.SIGTERM, self.handler )
        signal.signal( signal.SIGINT, self.handler )
        try:
            self.serveraddress = sys.argv[1]
            self.serverport = int( sys.argv[2] )
        except: self.printusage()
        try:
            self.serversocket = socket.socket( socket.AF_INET,
                                               socket.SOCK_DGRAM )
            self.serversocket.bind(( self.serveraddress, self.serverport ))
            self.serversocket.setblocking( 0 )
        except:
            print "[ERROR] Could not establish listening socket "
            exit( 1 )

    def handler( self, signum, frame ):
        self.runServerLoop = False

    def updateplayer( self ):
        if self.receivedstate[0] <= self.lasttick:
            return
        self.lasttick = self.receivedstate[0]
        if self.receivedstate[1]: self.player1y -= self.playerspeed
        if self.receivedstate[2]: self.player1y += self.playerspeed
        if self.receivedstate[3]: self.player1x -= self.playerspeed
        if self.receivedstate[4]: self.player1x += self.playerspeed
                
    def printusage( self ):
        print "Usage: server.py [address] [port]"
        print "  [address] is the adddress the server binds to, usually localhost"
        print "  [port] is the port to listen on for client connections"
        print "  server runs until killed or interrupted"
        exit( 1 )

    def loop( self ):
        while self.runServerLoop:
            self.clock.tick( 60 )
            try:
                self.receivedstate, self.clientaddress = \
                    self.serversocket.recvfrom( 256 )
            except: pass
            if self.receivedstate is not None:
                self.handlepacket( self.clientaddress, self.receivedstate )
            try:
                self.serversocket.sendto( struct.pack( 'iff',
                    pygame.time.get_ticks(), self.player1x, self.player1y ), self.clientaddress )
            except: pass

def main():
    pygame.init()
    server_object = gameserver()
    server_object.loop()
    pygame.quit()

main()
