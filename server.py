#!/usr/bin/env python

import socket, sys, signal, errno, time
import struct

class gameserver:
    def __init__( self ):
        self.runServerLoop = True
        self.connection = None
        self.receivedstate = struct.pack( '????', False, False, False, False )
        self.player1x = 100
        self.player1y = 100
        self.playerspeed = 3
        signal.signal( signal.SIGTERM, self.handler )
        signal.signal( signal.SIGINT, self.handler )
        try:
            self.serveraddress = sys.argv[1]
            self.serverport = int( sys.argv[2] )
        except: printusage()
        try:
            self.serversocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.serversocket.bind(( self.serveraddress, self.serverport ))
            self.serversocket.setblocking( 0 )
            self.serversocket.listen( 2 )
        except:
            print "[ERROR] Could not establish listening socket "
            exit( 1 )

    def handler( self, signum, frame ):
        self.runServerLoop = False

    def updateplayer( self ):
        if self.receivedstate[0]: self.player1y -= self.playerspeed
        if self.receivedstate[1]: self.player1y += self.playerspeed
        if self.receivedstate[2]: self.player1x -= self.playerspeed
        if self.receivedstate[3]: self.player1x += self.playerspeed
        print "player position: " + str( self.player1x) + " "  + str( self.player1y )
                
    def printusage( self ):
        print "Usage: server.py [address] [port]"
        print "  [address] is the adddress the server binds to, usually localhost"
        print "  [port] is the port to listen on for client connections"
        print "  server runs until killed or interrupted"
        exit( 1 )

    def loop( self ):
        while self.runServerLoop:
            try: self.connection, clientaddress = self.serversocket.accept()
            except: pass
            if self.connection is None: continue
            try:
                self.receivedstate = struct.unpack('????',
                    self.connection.recv( 256 ) )
            except: pass
            self.updateplayer()
            try:
                self.connection.send( struct.pack( 'ff',
                    self.player1x, self.player1y ))
            except: pass
        self.serversocket.close()

def main():
    server_object = gameserver()
    server_object.loop()

main()
