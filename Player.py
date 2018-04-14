import struct

class Player:
    packet_format = "iiff"

    @staticmethod
    def packet_size():
        return struct.calcsize( Player.packet_format )

    def __init__( self, number, address ):
        print "creating a player with address %s and number %s" % \
            ( address, number )
        self.x_position = 100
        self.y_position = 100
        self.address = address
        self.last_tick = -1
        self.idle_time = 0
        self.number = number
        self.valid = True
        self.mode = 1

    def make_packet( self ):
        return struct.pack( self.packet_format, self.number, self.last_tick,
                            self.x_position, self.y_position )

    def handle_packet( self, packet ):
        state = struct.unpack( self.packet_format, packet )
        if self.number != state[0]: return False
        self.valid = True
        if self.last_tick < state[1]:
            self.last_tick = state[1]
            self.x_position = state[2]
            self.y_position = state[3]
        return True
