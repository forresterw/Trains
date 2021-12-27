## Milestone 2

-   Added information about map dimensions to the visual.md design document.
    -   [Old Document](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/6f23881dcd7ffdbcb3d6583a3f6b8ded52e05866/Trains/Planning/visual.md)
    -   [New Document](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Planning/visual.md)

## Milestone 3

-   Helper method [`verify_city_names`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/6fdb26b06036d6cc95ee0835062ec7141c6ab06a/Trains/Editor/map_editor.py#L134) only verifies a single city name. Changed method name to [`verify_city_name`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/fe6e0b2dcbc11c7e7409582de7f0dcc4ad6975e6/Trains/Editor/map_editor.py#L134) and updated purpose statement.

## Milestone 4

-   [Updated player-interface.md design document](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/fe6e0b2dcbc11c7e7409582de7f0dcc4ad6975e6/Trains/Planning/player-interface.md). Changes made to [old document](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/6fdb26b06036d6cc95ee0835062ec7141c6ab06a/Trains/Planning/player-interface.md):
    -   Included information on the outcomes of calling Player's `play` method.
    -   Based on [Logical Interactions](https://www.ccs.neu.edu/home/matthias/4500-f21/local_protocol.html) spec and new implementation:
        -   Replaced `intialize_player` with `setup`.
        -   Added `pick` method for player choosing destinations.
        -   Replaced `get_player_move` with `play`.
        -   Added `more` method for Player receiving more cards.
        -   Replaced `end_game_for_player` with `win`.

## Milestone 5

-   PlayerGameState's `opponent_info` field previously was a dictionary that relied on player names to be unique. Converted this to a list of dictionaries (containing keys/values for opponents' acquired connections and number of cards in their hand).

    -   [Old Implementation](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/d2e1d05abf9cf95438caf1a65c8bf5548767a5e8/Trains/Common/player_game_state.py#L57)
    -   [New Implementation](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/fe6e0b2dcbc11c7e7409582de7f0dcc4ad6975e6/Trains/Common/player_game_state.py#L56-L61)

## Milestone 6

-   Fixed the player API to match the [logical interactions spec](https://www.ccs.neu.edu/home/matthias/4500-f21/local_protocol.html)

    -   Removed [`initialize_player`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/e032cbb192bd6984d5582c41e7a46de2ba5da0b2/Trains/Player/player.py#L95) Added method [`setup`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Player/player_interface.py#L11) to Player API.
    -   Removed picking destinations from [previous set up functionality](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/e032cbb192bd6984d5582c41e7a46de2ba5da0b2/Trains/Player/player.py#L108). Added method [`pick`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Player/player_interface.py#L40) to Player API.
    -   Method [`get_player_move`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/6f23881dcd7ffdbcb3d6583a3f6b8ded52e05866/Trains/Player/player.py#L39) renamed to [`play`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Player/player_interface.py#L30) and now takes in a game state.
    -   Method [`end_game_for_player`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/6f23881dcd7ffdbcb3d6583a3f6b8ded52e05866/Trains/Player/player.py#L65) renamed to [`win`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Player/player_interface.py#L68).

-   Added single-point of control functionality for calling a player's funtions/methods
    -   Added method [`call_player_method`](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/e22ceba46676a08e5048888cc87f38f8a5d4c9c1/Trains/Admin/referee.py#L213) to Referee.

<hr/>
<br/>

\*\*Other feedback from previous design inspections was fixed prior to Milestone 7.
