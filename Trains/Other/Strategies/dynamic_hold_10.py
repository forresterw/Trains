import sys
sys.path.append("../../../")
from Trains.Player.strategy import AbstractPlayerStrategy
from Trains.Player.moves import DrawCardMove, AcquireConnectionMove

class Dynamic_Hold_10(AbstractPlayerStrategy):
    
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

    def select_connection(self, resources):
        """
        Hold_10 player strategy for selecting the connection to acquire when attempting to make a connection on their turn.
        Selects the first connection from the lexicographically sorted list of given connections (unacquired connections)
        that the player has the necessary resources to acquire.
            Parameters:
                resources (PlayerResources): the resources the player implementing this strategy has
            Returns:
                Connection to acquire if possible, None otherwise
        """
        unacquired_connections = resources.game_info["unacquired_connections"]
        sorted_connections = self.get_lexicographic_order_of_connections(list(unacquired_connections))

        for connection in sorted_connections:
            if self.can_acquire_connection(resources, connection):
                return connection
        return None

    def get_player_move(self, resources):
        """
        Polls the Hold_10 player strategy for a move.  The logic here follows the strategy described
        above in the Hold_10 Class purpose statement.
            Parameters:
                resources (PlayerResources): Player resources to inform decision making
            Return:
                A PlayerMove indicating a player's intended move
        """
        # Draw cards if player has 10 or fewer colored cards
        if resources.get_number_of_colored_cards() <= 10:
            return DrawCardMove
        # Otherwise attempt to acquire a connection
        else:
            desired_connection = self.select_connection(resources)
            # Draw cards if there is no acquireable connection
            if desired_connection is None:
                return DrawCardMove
            # Otherwise make the connection
            else:
                return AcquireConnectionMove(desired_connection)
