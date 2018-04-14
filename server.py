#!/usr/bin/env python

import socket, sys, signal, errno, time
import struct
import pygame
from Serverstate import Serverstate
from Player import Player

class gameserver:
    def __init__( self ):
        self.state = Serverstate()
        self.runloop = True
        self.clock = pygame.time.Clock()
        self.receivedstate = None
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
        self.runloop = False

    def printusage( self ):
        print "Usage: server.py address port"
        print "  address is the adddress the server binds to, usually localhost"
        print "  port is the port to listen on for client connections"
        print "  server runs until killed or interrupted"
        exit( 1 )

    def loop( self ):
        while self.runloop:
            self.clock.tick( 60 )
            self.clientaddress = None
            self.state.idle_time()
            while True:
                try:
                    self.receivedstate, self.clientaddress = \
                        self.serversocket.recvfrom( 256 )
                except socket.error, e:
                    if e.args[0] == errno.EWOULDBLOCK: break
                    else: print "Socket Error: %s" % e
                if self.receivedstate is not None:
                    if self.receivedstate[0] == 'k':
                        self.state.handle_keystate( self.clientaddress,
                                                    self.receivedstate )
                    elif self.receivedstate[0] == 'j':
                        playerid = self.state.handle_join( self.clientaddress,
                                                self.receivedstate )
                        if playerid != 0:
                            self.serversocket.sendto(
                                struct.pack( 'ci', 'j', playerid),
                                self.clientaddress )
            worldstate = self.state.make_packet( pygame.time.get_ticks() )
            for connection in self.state.connections:
                try: self.serversocket.sendto( worldstate, connection )
                except: pass
            self.state.prune_clients()

def main():
    pygame.init()
    server_object = gameserver()
    server_object.loop()
    pygame.quit()

main()
