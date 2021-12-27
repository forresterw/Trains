import sys
sys.path.append('../../')

from Trains.Common.map import Connection
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.moves import PlayerMove, DrawCardMove, AcquireConnectionMove
from Trains.Player.strategy import AbstractPlayerStrategy

class Hold_10(AbstractPlayerStrategy):
    def select_destinations(self, destinations: set, num_destinations: int) -> set:
        """
        Hold_10 player strategy for selecting their 2 destinations during the setup of the game.
        Selects the two destinations that come first in the lexicographic ordering of the destinations
        they have to choose from (given by Referee).
            Parameters:
                destinations (set(Destination)): Destinations to choose 2 from according to the strategy above.
                num_destinations (int): number of destinations to pick, num_destinations <= len(destination)
            Returns:
                set(Destination): The set of destinations selected
            Throws:
                ValueError: num_destinations must be less than set size
        """
        if num_destinations > len(destinations):
            raise ValueError("num_destinations must be <= len(destinations)")

        sorted_destinations = self.get_lexicographic_order_of_destinations(list(destinations))
        return set(sorted_destinations[0:num_destinations])

    def select_connection(self, game_state: PlayerGameState) -> Connection or None:
        """
        Hold_10 player strategy for selecting the connection to acquire when attempting to make a connection on their turn.
        Selects the first connection from the lexicographically sorted list of given connections (unacquired connections)
        that the player has the necessary resources to acquire.
            Parameters:
                game_state (PlayerGameState): the game state of the player implementing this strategy
            Returns:
                Connection to acquire if possible, None otherwise
        """
        unacquired_connections = game_state.game_info["unacquired_connections"]
        sorted_connections = self.get_lexicographic_order_of_connections(list(unacquired_connections))

        for connection in sorted_connections:
            if self.can_acquire_connection(game_state, connection):
                return connection
        return None

    def get_player_move(self, game_state: PlayerGameState) -> PlayerMove:
        """
        Polls the Hold_10 player strategy for a move.  The logic here follows the strategy described
        above in the Hold_10 Class purpose statement.
            Parameters:
                game_state (PlayerGameState): the game state of the player implementing this strategy
            Return:
                A PlayerMove indicating a player's intended move
        """
        # Draw cards if player has 10 or fewer colored cards
        if game_state.get_number_of_colored_cards() <= 10:
            return DrawCardMove()
        # Otherwise attempt to acquire a connection
        else:
            desired_connection = self.select_connection(game_state)
            # Draw cards if there is no acquireable connection
            if desired_connection is None:
                return DrawCardMove()
            # Otherwise make the connection
            else:
                return AcquireConnectionMove(desired_connection)

