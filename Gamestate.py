import struct
from Player import Player

class Gamestate:
    def __init__( self ):
        self.lasttick = 0
        self.player_speed = 1
        self.players = []
        self.connections = []

    def add_player( self, address ):
        self.players.append( Player( address ))

    def handle_packet( self, address, packet ):
        if address not in self.connections and address is not None:
            self.add_player( address )
            self.connections.append( address )
            print "player %s joined" % str( address )
        state = struct.unpack( 'i????', packet )
        lasttick = state[0]
        for player in self.players:
            if player.address == address and lasttick > player.lasttick:
                player.lasttick = lasttick
                if state[1]: player.y_position -= self.player_speed
                if state[2]: player.y_position += self.player_speed
                if state[3]: player.x_position -= self.player_speed
                if state[4]: player.x_position += self.player_speed

    def make_packet( self, tick ):
        packet = ""
        for player in self.players:
            packet += struct.pack( 'iff', tick, player.x_position,
                player.y_position )
        return packet
