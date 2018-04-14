import struct
from Player import Player

class Serverstate:
    def __init__( self ):
        self.lasttick = 0
        self.player_speed = 1
        self.players = []
        self.connections = []
        self.idle_limit = 60
        self.id_counter = 0

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
                if state[2]: player.y_position -= self.player_speed
                if state[3]: player.y_position += self.player_speed
                if state[4]: player.x_position -= self.player_speed
                if state[5]: player.x_position += self.player_speed

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
