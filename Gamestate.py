import struct
from Player import Player

class Gamestate:
    def __init__( self ):
        self.lasttick = 0
        self.players = []
        self.local_player = 0

    def add_player( self, number ):
        self.players.append( Player( number, None ))

    def del_player( self, number ):
        for player in self.players:
            if number == player.number:
                self.players.remove( player )

    def handle_worldstate( self, packet ):
        n = Player.packet_size()
        packet = packet[1:]
        if len( packet ) % n != 0: return
        for player in self.players: player.valid = False
        for key, value in enumerate( \
            [packet[i:i + n] for i in range(0, len( packet ), n )] ):
            handled = False
            for player in self.players:
                handled = player.handle_packet( value ) or handled
            if not handled:
                number = struct.unpack( Player.packet_format, value )[0]
                self.add_player( number )
                for player in self.players: player.handle_packet( value )
        for player in self.players:
            if player.valid == False:
                self.del_player( player.number )
