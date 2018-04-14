import struct
import pygame
from Player import Player

class Serverstate:
    def __init__( self ):
        self.lasttick = 0
        self.player_speed = 0.1
        self.player_max_speed = 1
        self.players = []
        self.connections = []
        self.idle_limit = 60
        self.id_counter = 1
        self.level_image = pygame.image.load( "level.png" )

    def update( self ):
        for player in self.players:
            # move player
            player.x_position += player.x_velocity
            if player.y_velocity < 0:
                player.y_position += player.y_velocity
                player.y_velocity *= 0.9
            # boundary collision
            if player.x_position < 1: player.x_position = 1
            if player.x_position > 949: player.x_position = 949
            if player.y_position > 998:
                player.y_position = 998
                player.standing = True
            if player.standing == False:
                pcolor = self.level_image.get_at(( int( player.x_position ),
                                                   int( player.y_position ) ))
                bcolor = self.level_image.get_at(( int( player.x_position ),
                   int( player.y_position ) + 1 ))
                if pcolor.r >= bcolor.r:
                    player.y_position += player.y_velocity
                    player.y_velocity += self.player_speed
                    if player.y_velocity > self.player_max_speed:
                        player.y_velocity = self.player_max_speed
                else:
                    player.standing = True
                    player.y_velocity = 0

    def add_client( self, address ):
        self.connections.append( address )
        self.players.append( Player( self.id_counter, address ))
        print "player %s joined" % str( address )
        self.id_counter += 1
        return self.id_counter - 1

    def del_client( self, address ):
        for player in self.players:
            if address == player.address:
                print "Removing player %s" % str( address )
                self.connections.remove( address )
                self.players.remove( player )

    def handle_join( self, address, packet ):
        if address not in self.connections and address is not None:
            return self.add_client( address )
        elif address is not None:
            for player in self.players:
                if player.address == address:
                    return player.number
        return 0

    def handle_keystate( self, address, packet ):
        if address not in self.connections and address is not None:
            self.add_client( address )
            self.connections.append( address )
            print "player %s joined" % str( address )
        state = struct.unpack( 'ci????', packet )
        last_tick = state[1]
        for player in self.players:
            if player.address == address and last_tick > player.last_tick:
                player.last_tick = last_tick
                player.idle_time = 0
                if state[2] and player.standing:
                    player.y_velocity -= self.player_speed * 100
                    player.standing = False
                # TODO: implement dropping using down key
                #if state[3]: player.y_velocity += self.player_speed
                if state[4]: player.x_velocity -= self.player_speed
                elif player.x_velocity < 0:
                    player.x_velocity *= 0.9
                if state[5]: player.x_velocity += self.player_speed
                elif player.x_velocity > 0:
                    player.x_velocity *= 0.9
                if player.x_velocity > self.player_max_speed:
                    player.x_velocity = self.player_max_speed
                if player.x_velocity < self.player_max_speed * -1:
                    player.x_velocity = self.player_max_speed * -1
                if player.y_velocity > self.player_max_speed:
                    player.y_velocity = self.player_max_speed
                if player.y_velocity < self.player_max_speed * -1:
                    player.y_velocity = self.player_max_speed * -1

    def idle_time( self ):
        for player in self.players:
            player.idle_time += 1

    def prune_clients( self ):
        for player in self.players:
            if player.idle_time > self.idle_limit:
                self.del_client( player.address )

    def make_packet( self, tick ):
        packet = "w"
        for player in self.players:
            packet += player.make_packet()
        return packet
