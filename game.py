#!/usr/bin/env python

import pygame
import sys
import socket
import struct
import errno

class game:
    def __init__( self ):
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.quit = False
        self.clock = pygame.time.Clock()
        self.serveraddress = "localhost"
        self.serverport = 6112
        self.screen = pygame.display.set_mode(( self.SCREEN_WIDTH, self.SCREEN_HEIGHT ))
        self.ballimage = pygame.image.load( "ball.gif" )
        self.player1x = 0
        self.player1y = 0
        self.keystate = struct.pack( '????', False, False, False, False )
        try:
            self.clientsocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.clientsocket.connect(( self.serveraddress, self.serverport ))
            self.clientsocket.setblocking( 0 )
        except:
            print "[ERROR] Could not connect to server"
            exit( 1 )

    def draw( self ):
        self.screen.fill(( 0, 0, 0 ))
        self.screen.blit( self.ballimage, ( self.player1x, self.player1y ))
        pygame.display.flip()
        
    def handle_input( self, buttons ):
        self.keystate = struct.pack( '????',
            buttons[pygame.K_UP],
            buttons[pygame.K_DOWN],
            buttons[pygame.K_LEFT],
            buttons[pygame.K_RIGHT] )
        output = ""
        if buttons[pygame.K_UP]: output += "UP "
        if buttons[pygame.K_DOWN]: output += "DOWN "
        if buttons[pygame.K_LEFT]: output += "LEFT "
        if buttons[pygame.K_RIGHT]: output += "RIGHT "
        print "sent: " + output

    def handle_keydown( self, key ):
        if key == pygame.K_q or key == pygame.K_ESCAPE:
            pygame.event.post( pygame.event.Event( pygame.QUIT ))
        
    def updatestate( self ):
        pass

    def loop(self):
        while not self.quit:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.quit = True
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown( event.key )
            self.handle_input( pygame.key.get_pressed() )
            self.clientsocket.send( self.keystate )
            try:
                self.player1x, self.player1y = struct.unpack( 'ff',
                    self.clientsocket.recv( 256 ))
            except socket.error, e:
                if e.args[0] == errno.EWOULDBLOCK: pass
            except: pass
            self.updatestate()
            self.draw()
        pygame.quit()
        sys.exit()

def main():
    pygame.init()
    game_object = game()
    game_object.loop()

main()