# TODO List Items

[x] Fix player API to match the [logical interactions spec](https://www.ccs.neu.edu/home/matthias/4500-f21/local_protocol.html)

[x] RefereeGameState's list of player game states currently relies on player names, which are not unique.
Change referee 'game_state' from dictionary to the given list (from referee) of player game states in the turn order of the players.

[x] Create a data representation for opponent information that a player can see

[x] Change 'opponent_info' in the player state from a dictionary mapping player names (not again, not unique) to a list of opponent information (the data representation mentioned above) in the turn order of the players

[x] Change how the map is given to players by giving the map directly to each player.

[x] Move cheating catch blocks into single point of control/functionality

[x] Add/Fix PlayerGameState unit tests

[x] Add/Fix RefereeGameState unit tests

[x] Add/Fix referee unit tests

[x] Update design documents based on design-inspection feedback

[x] Move classes into separate files

[ ] Change ValueErrors to TypeErrors when appropriate
