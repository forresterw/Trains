import sys
sys.path.append('../../')

from Trains.Common.map import Connection
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.moves import PlayerMove, DrawCardMove, AcquireConnectionMove
from Trains.Player.strategy import AbstractPlayerStrategy

class Buy_Now(AbstractPlayerStrategy):
    
    def select_destinations(self, destinations: set, num_destinations: int) -> set:
        """
        Buy_Now player strategy for selecting their 2 destinations during the setup of the game.
        Selects the two destinations that come last in the lexicographic ordering of the destinations
        they have to choose from (given by Referee).
            Parameters:
                destinations (set(Destination)): Destinations to choose 2 from according to the strategy above.
                num_destinations (int): number of destinations to pick, num_destinations <= len(destination)
            Returns:
                set(Destination): The two destinations selected
            Throws:
                ValueError: num_destinations must be less than set size
        """
        if num_destinations > len(destinations):
            raise ValueError("num_destinations must be <= len(destinations)")

        sorted_destinations = self.get_lexicographic_order_of_destinations(list(destinations))
        return set(sorted_destinations[-1*num_destinations:])

    def select_connection(self, resources: PlayerGameState) -> Connection or None:
        """
        Buy_Now player strategy for selecting the connection to acquire when attempting to make a connection on their turn.
        Selects the first connection from the lexicographically sorted list of given connections (unacquired connections)
        that the player has the necessary resources to acquire.
            Parameters:
                resources (PlayerGameState): the resources the player implementing this strategy has
            Returns:
                Connection to acquire if possible, None otherwise
        """
        unacquired_connections = resources.game_info["unacquired_connections"]
        sorted_connections = self.get_lexicographic_order_of_connections(list(unacquired_connections))

        for connection in sorted_connections:
            if self.can_acquire_connection(resources, connection):
                return connection
        return None

    def get_player_move(self, resources: PlayerGameState) -> PlayerMove:
        """
        Polls the Buy_Now player strategy for a move.  The logic here follows the strategy described
        above in the Hold_10 Class purpose statement.
            Return:
                A PlayerMove indicating a player's intended move
        """
        # Always attempt to acquire a connection
        desired_connection = self.select_connection(resources)
        # If there are no acquireable connections then draw cards
        if desired_connection is None:
            return DrawCardMove()
        # Otherwise acquire the connection
        else:
            return AcquireConnectionMove(desired_connection)