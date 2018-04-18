import struct
import pygame
from Player import Player

class Serverstate:
    def __init__( self ):
        self.lasttick = 0
        self.player_speed = 0.2
        self.player_max_speed = 5
        self.gravity = 0.2
        self.jump_power = 12
        self.players = []
        self.connections = []
        self.idle_limit = 60
        self.id_counter = 1
        self.tagback_cooldown_value = 60
        self.tagback_cooldown = 0
        self.level_image = pygame.image.load( "level.png" )
        self.LEVEL_WIDTH = self.level_image.get_width()
        self.LEVEL_HEIGHT = self.level_image.get_height()
        self.player_image = pygame.image.load( "hero0.png" )
        self.PLAYER_HEIGHT = self.player_image.get_height()
        self.PLAYER_WIDTH = self.player_image.get_width()
        self.PLAYER_HWIDTH = self.PLAYER_WIDTH / 2

    def update( self ):
        for player in self.players:
            # move player sideways
            player.x_position += player.x_velocity
            # check sideways boundary
            if player.x_position < self.PLAYER_HWIDTH:
                player.x_position = self.PLAYER_HWIDTH
            elif player.x_position > self.LEVEL_WIDTH - self.PLAYER_HWIDTH:
                player.x_position = self.LEVEL_WIDTH - self.PLAYER_HWIDTH
            # fall
            if player.y_velocity < 0:
                player.y_position += player.y_velocity
                player.y_velocity += self.gravity
                continue
            player.y_velocity += self.gravity
            fall_distance = player.y_velocity
            for i in range( 0, int( fall_distance )):
                if int( player.y_position ) == self.LEVEL_HEIGHT - 1:
                    player.y_velocity = 0
                    player.standing = True
                    break
                if player.y_position < 0:
                    player.y_position += 1
                    continue
                pcolor = self.level_image.get_at((
                    int( player.x_position ), int( player.y_position )))
                bcolor = self.level_image.get_at((
                    int( player.x_position ), int( player.y_position + 1 )))
                if pcolor.r < bcolor.r:
                    player.standing = True
                    player.y_velocity = 0
                    break
                # move them each pixel down as needed checking as you go
                player.y_position += 1
            if player.mode == 1:
                if self.tagback_cooldown != 0:
                    self.tagback_cooldown -= 1
                else: player.mode = 2
            if player.mode == 2:
                for otherplayer in self.players:
                    if player == otherplayer: continue
                    xdelta = player.x_position - otherplayer.x_position
                    ydelta = player.y_position - otherplayer.y_position
                    if xdelta < 0: xdelta *= -1
                    if ydelta < 0: ydelta *= -1
                    if xdelta < self.PLAYER_WIDTH and \
                        ydelta < self.PLAYER_HEIGHT:
                        player.mode = 0
                        otherplayer.mode = 1
                        self.tagback_cooldown = self.tagback_cooldown_value
                        break

    def add_client( self, address ):
        self.connections.append( address )
        self.players.append( Player( self.id_counter, address ))
        if len( self.players ) == 1:
            self.players[0].mode = 2
        print "player %s joined" % str( address )
        self.id_counter += 1
        return self.id_counter - 1

    def del_client( self, address ):
        for player in self.players:
            if address == player.address:
                print "Removing player %s" % str( address )
                if player.mode == 2:
                    if len( self.players ) > 0:
                        for player in self.players:
                            player.mode = 2
                            break
                try:
                    self.connections.remove( address )
                    self.players.remove( player )
                except:
                    print "Error removing player %s" % str( address )

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
                if state[2] and player.standing and player.mode != 1:
                    player.y_velocity -= self.jump_power
                    player.standing = False
                if state[3] and player.mode != 1:
                    if player.standing and \
                        int( player.y_position ) < self.LEVEL_HEIGHT - 1:
                        player.y_position += 1
                        player.standing = False
                if state[4] and player.mode != 1:
                    player.x_velocity -= self.player_speed
                elif player.x_velocity < 0:
                    player.x_velocity *= 0.9
                if state[5] and player.mode != 1:
                    player.x_velocity += self.player_speed
                elif player.x_velocity > 0:
                    player.x_velocity *= 0.9
                if player.x_velocity > self.player_max_speed:
                    player.x_velocity = self.player_max_speed
                if player.x_velocity < self.player_max_speed * -1:
                    player.x_velocity = self.player_max_speed * -1

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
