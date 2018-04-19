# cs576-group3
CS576 Group 3 Project - Spring 2018

## Requirements
* Python 2.x
* Pygame `pip install pygame`

## Installation
`git clone https://github.com/mickeylyle/cs576-group3.git`

## Running Server
* Open a terminal window in installation directory
* `./server.py <address> <port>` where <address> is local IP and <port> is any you choose
* to stop enter ctrl+c on keyboard

## Running as Player
* Open a terminal window in installation directory
* `./game.py <address> <port>` where <address> is __server__ IP and <port> is any you choose

## Game Play
* Use keyboard arrows to move your player on the screen
* Red player is __"IT"__, and should persue other players
* Other players try to avoid being touched by the red player
* If you are touched by red player you will be __"IT"__
