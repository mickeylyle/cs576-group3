#!/usr/bin/env python

import socket, sys, signal, errno, time
import struct
import pygame
from Gamestate import Gamestate
from Player import Player

class gameserver:
    def __init__( self ):
        self.gamestate = Gamestate()
        self.runServerLoop = True
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
        self.runServerLoop = False

    def printusage( self ):
        print "Usage: server.py [address] [port]"
        print "  [address] is the adddress the server binds to, usually localhost"
        print "  [port] is the port to listen on for client connections"
        print "  server runs until killed or interrupted"
        exit( 1 )

    def loop( self ):
        while self.runServerLoop:
            self.clock.tick( 60 )
            self.clientaddress = None
            while True:
                try:
                    self.receivedstate, self.clientaddress = \
                        self.serversocket.recvfrom( 256 )
                except socket.error, e:
                    if e.args[0] == errno.EWOULDBLOCK: break
                    else: print "Socket Error: %s" % e
                if self.receivedstate is not None:
                    self.gamestate.handle_packet( self.clientaddress,
                                                  self.receivedstate )
            for connection in self.gamestate.connections:
                try:
                    self.serversocket.sendto( self.gamestate.make_packet(
                        pygame.time.get_ticks() ), connection )
                except: pass

def main():
    pygame.init()
    server_object = gameserver()
    server_object.loop()
    pygame.quit()

main()
