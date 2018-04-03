import struct

class gamestate:
    def __init__( self ):
        print "made game state"
        self.lasttick = 0
        self.player_speed = 1
        self.players = []

    def add_player( self, address ):
        self.players.append( player( address ))

    def handle_packet( self, address, packet ):
        if address not in self.connections:
            self.add_player( address )
        state = struct.unpack( 'i????', packet )
        lasttick = state[0]
        up = state[1]
        down = state[2]
        left = state[3]
        right = state[4]
        for player in players:
            if player.address == address and lasttick > player.lasttick:
                player.y_position -= state[1] ? self.payer_speed
                player.y_position += state[2] ? self.payer_speed
                player.x_position -= state[3] ? self.payer_speed
                player.x_position += state[4] ? self.payer_speed
    
