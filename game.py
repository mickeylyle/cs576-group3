#!/usr/bin/env python

import pygame
import sys
import socket
import struct
import errno
from Player import Player
from Gamestate import Gamestate

class game:
    def __init__( self ):
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 1000
        self.quit = False
        self.clock = pygame.time.Clock()
        self.lasttick = -1
        self.receivedstate = ""
        self.screen = pygame.display.set_mode(( self.SCREEN_WIDTH,
                                                self.SCREEN_HEIGHT ))
        self.hero1_image = pygame.image.load( "hero1.png" )
        self.hero2_image = pygame.image.load( "hero2.png" )
        self.PLAYER_HEIGHT = self.hero1_image.get_height()
        self.level_image = pygame.image.load( "level.png" )
        #self.players = []
        self.keystate = ""
        self.state = Gamestate()
        try: self.serveraddress = sys.argv[1]
        except:
            print "using localhost for server address"
            self.serveraddress = "localhost"
        try: self.serverport = int( sys.argv[2] )
        except:
            print "using 6112 for server port"
            self.serverport = 6112
        try:
            self.clientsocket = socket.socket( socket.AF_INET,
                                               socket.SOCK_DGRAM )
            self.clientsocket.setblocking( 0 )
        except:
            print "[ERROR] Could not connect to server"
            exit( 1 )

    def printusage( self ):
        print "Usage: game.py address port"
        print "  address is the location of the server"
        print "  port is the port to connect to"
        exit( 1 )

    def draw( self ):
        self.screen.fill(( 0, 0, 0 ))
        self.screen.blit( self.level_image, ( 0, 0) )
        for player in self.state.players:
            if player.mode == 1: image = self.hero1_image
            if player.mode == 2: image = self.hero2_image

            self.screen.blit( image, ( player.x_position,
                                       player.y_position - self.PLAYER_HEIGHT ))
        pygame.display.flip()
        
    def handle_input( self, buttons ):
        self.keystate = struct.pack( 'ci????',
            'k',
            pygame.time.get_ticks(),
            buttons[pygame.K_UP],
            buttons[pygame.K_DOWN],
            buttons[pygame.K_LEFT],
            buttons[pygame.K_RIGHT] )

    def handle_keydown( self, key ):
        if key == pygame.K_q or key == pygame.K_ESCAPE:
            pygame.event.post( pygame.event.Event( pygame.QUIT ))
        
    def loop(self):
        while not self.quit:
            self.clock.tick( 60 )
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.quit = True
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown( event.key )
            if self.state.local_player == 0:
                self.clientsocket.sendto( "j",
                    ( self.serveraddress, self.serverport ))
                # send join packet
                # listen for join packet
                try:
                    self.receivedstate, self.server = \
                        self.clientsocket.recvfrom( 256 )
                except socket.error, e:
                    if e.args[0] == errno.EWOULDBLOCK: pass
                    else: print "Socket Error: %s" % e
                if len( self.receivedstate ) == 0: continue
                if self.receivedstate[0] == 'j':
                    packet = struct.unpack( 'ci', self.receivedstate )
                    self.state.local_player = packet[1]
                continue
            self.handle_input( pygame.key.get_pressed() )
            self.clientsocket.sendto( self.keystate,
                ( self.serveraddress, self.serverport ))
            try:
                self.receivedstate, self.server = \
                    self.clientsocket.recvfrom( 256 )
            except socket.error, e:
                if e.args[0] == errno.EWOULDBLOCK: pass
                else: print "Socket Error: %s" % e
            if len( self.receivedstate ) == 0: continue 
            if self.receivedstate[0] == 'w':
                self.state.handle_worldstate( self.receivedstate )
            self.draw()
        pygame.quit()
        sys.exit()

def main():
    pygame.init()
    game_object = game()
    game_object.loop()

main()
