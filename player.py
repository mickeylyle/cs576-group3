class player:
    def __init__( self, address ):
        print "creating player %s object" % address
        self.x_position = 100
        self.y_position = 100
        self.address = address
        self.lasttick = -1
