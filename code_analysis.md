Code Analysis

==Pygame Clock==
Both the server and the client use the pygame clock object to manage their time. Both run at 60 updates per second.

==Client Initialization==
The client starts by loading and initializing all of its variables and data. Currently the client uses the same level image that the server does, but all it does is draw it to the screen, so technically a different level image could be used. The apparent collision of the level would ideally match the actual collision used by the server, of course. Also, currently the client uses the size of the level image to dictate the size of the game window. If this were developed into a real game, that would need to be fixed.

The client accepts a server ip and port, using localhost and 6112 as defaults if not provided, as these are ideal for testing. The client sets up a UDP socket to use.

==Client Loop==
The client loops until the 'q' key is pressed, which is handled through the pygame event library. When the loop starts, the local_player variable in the client state object is 0, meaning it has not been initialized. The client sends join requests, just a packet with the character 'j', to the server until a join response is sent back, which is a packet with the letter character 'j' followed by an int representing the local player id. One the client has an id for the local player it enters normal behavior, in which it does three things:

1. poll the state of the arrow keys, pack them up, and send them to the server
2. check for world state packets from the server, and update the local state correspondingly
3. draw the game world

==Client Keystate==
The client sends packets to the server that contain information about the current state of the clients arrow keys, called keystate packets. The handle_input function does this, just packing up four booleans reflecting the press versus not pressed state of the four arrow keys. This packet starts with a 'k' character to indicate it is a keystate, followed by an integer that reflects the current tick count of the client, and then the four booleans.

==Client Worldstate Update==
When the client receives a worldstate packet from the server, which it can identify by the packet starting with a 'w' character, this packet is sent to the client state object to be handled. The handle_worldstate function checks the size of the packet, ensuring that it contains the correct amount of information for the number of players that it detects. The packet is divided into one section per player, each section having data on that players state. If the player is not in the local game state, they are added, and if a player in the local game state is missing from the worldstate, they are removed. Each player's data is passed to their object in the local state to be handled, where their position and mode (runner, tagged, it) is updated. If the player object detects, based on the tick in the packet, that it is older than or a duplicate of, the state that they already have, it ignores the packet.

==Client Rendering==
The client clears the rendering surface, draws the level to it, and then draws each player to it in their position as reflected in the local game state. If they are tagged or it, they are drawn with a different image to reflect this. The whole surface is then flipped to the screen.

==Server Initialization==
The server initializes its values, and binds to a UDP port to listen to. Much more of the heavy lifting for the server is done in the server state object, the server object itself mostly does the network side of things.

==Server Loop==
The server loop does four things:

1. listens for incoming packets, and based on their header character, handles them appropriately
2. updates the world state based on player velocities set by keystates from packets
3. packs up the worldstate and sends it to all known connections
4. removes idle players

==Server Packet Handling==
Whenever a packet is received, if that connection is not already in the known connection list for the server, it is added. When the server receives a packet, it checks the leading character. If it is a 'j', it is a join request, and that player's id is send back to that connection. If it is a 'k', that packet is a keystate, and is passed into the server state object for handling. If the keystate is older than or a duplicate of the state the server already has, the packet is ignored. The handle_keystate function is responsible for updating the velocities of the players. Some of the game rules start to come into play here: players cannot jump or drop if they are not standing on the ground, they can't drop off the bottom of the map, and if the character is moving to the side but the player is no longer pressing that key, they have to slow down. In this function the server state also updates the server player object to indicate that that player is not idle.

==Server Worldstate Update==
The server state update function is the core of the rules for the game. While the handle_keystate function does implement some of the movement rules, the udpate function enforces the rest. Players are moved based on their velocity, and bumped back if they collide with the sides or bottom of the map. As players are falling, the server checks each pixel, pixel by pixel, as they fall to see if the value of the pixel they are falling onto is higher than the value of the one they are currently on. This value is literally the color of the pixel. The game currently only uses the red channel, but since greys have equal values in all channels, a monochrome image serves for collision purposes. If the player falls onto a pixel with a higher value, they collide and stop falling. This loop also loops through the players to find who is "it", and checks to see if they are touching another player. If they are, this player is marked as "tagged", and after a duration, set to "it".

==Server Worldstate Propogation==
The make_packet function in the server state object makes a packet with a 'w' character header, and then contcatenates onto it a data string for each player. This is sent to every connection that the server is tracking, see the "Client Worldstate Update" section.

==Idle Player Pruning==
Each loop, the server increments each player's idle time, and checks to see if any players have reached the idle limit. The idle time for a player is reset if the server receives a packet from them: if it does not receive one, it keeps increasing. Once the idle time limit is reached, that player is pruned. Note that currently clients do not know when they have been pruned! Ideally they would send a new join request when they realize they are not receiving packets, but this is not implemented yet.

==Lessons Learned==
- Making different packet types was surprisingly easy: becauase every packet is a string, as a result of using the struct.pack implementation, prepending a control character on each packet was an easy way to switch handling on received packets.
- Both client and server had to listen for all incoming packets each tick- early implementations of each would only listen for one packet each tick. Because packets would sometimes pile up on the connection, this resulted in stuttery and slow updates, but if all received packets were handled every tick, only moving on when no more packets were waiting, the server and client ran smoothly.
- No interpolation was done. Interpolation may have been much easier to implement that we imagined, but getting the state to sync was an acheivement enough, and anything further was beyond the scope of this project.

==Conclusion==
This was a lot of fun, and a really good learning experience. Getting what amounts to two different programs to communicate and sync with each other was a big challenge. The server/client structure we chose really helped us here, we can't imagine how difficult p2p gaming logic is, at least for real-time games. Working to establish a presentation layer protocol that worked for our game rules was interesting and very informative. We hope you enjoy playing!