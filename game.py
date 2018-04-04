#!/usr/bin/env python

import pygame
import sys
import socket
import struct
import errno
from Player import Player

class game:
    def __init__( self ):
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.quit = False
        self.clock = pygame.time.Clock()
        self.lasttick = -1
        self.serveraddress = ( "192.168.1.106", 6112 )
        self.receivedstate = ""
        self.screen = pygame.display.set_mode(( self.SCREEN_WIDTH, self.SCREEN_HEIGHT ))
        self.ballimage = pygame.image.load( "ball.gif" )
        self.players = []
        self.keystate = ""
        try:
            self.clientsocket = socket.socket( socket.AF_INET,
                                               socket.SOCK_DGRAM )
            self.clientsocket.setblocking( 0 )
        except:
            print "[ERROR] Could not connect to server"
            exit( 1 )

    def draw( self ):
        self.screen.fill(( 0, 0, 0 ))
        for player in self.players:
            self.screen.blit( self.ballimage, ( player.x_position,
                                                player.y_position ))
        pygame.display.flip()
        
    def handle_input( self, buttons ):
        self.keystate = struct.pack( 'i????',
            pygame.time.get_ticks(),
            buttons[pygame.K_UP],
            buttons[pygame.K_DOWN],
            buttons[pygame.K_LEFT],
            buttons[pygame.K_RIGHT] )

    def handle_keydown( self, key ):
        if key == pygame.K_q or key == pygame.K_ESCAPE:
            pygame.event.post( pygame.event.Event( pygame.QUIT ))
        
    def updatestate( self, state ):
        if len( state ) % 12 != 0:
            return
        n = 12
        for key, value in enumerate( \
            [state[i:i + n] for i in range(0, len(state), n)] ):
            this_state = struct.unpack( 'iff', value )
            if this_state[0] < self.lasttick:
                print "ignoring old tick"
                continue
            self.lasttick = this_state[0]
            if len( self.players ) < key + 1:
                print "adding player %s" % str( key + 1 )
                self.players.append( Player( str( key + 1 )))
            self.players[key].x_position = this_state[1]
            self.players[key].y_position = this_state[2]

    def loop(self):
        while not self.quit:
            self.clock.tick( 60 )
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.quit = True
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown( event.key )
            self.handle_input( pygame.key.get_pressed() )
            self.clientsocket.sendto( self.keystate, self.serveraddress )
            try:
                self.receivedstate, self.serveraddress = \
                    self.clientsocket.recvfrom( 256 )
            except socket.error, e:
                if e.args[0] == errno.EWOULDBLOCK: pass
                else: print "Socket Error: %s" % e
            self.updatestate( self.receivedstate )
            self.draw()
        pygame.quit()
        sys.exit()

def main():
    pygame.init()
    game_object = game()
    game_object.loop()

main()
