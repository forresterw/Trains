import functools
import sys
sys.path.append('../../')
from Trains.Common.map import Connection, Destination
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.moves import PlayerMove

class PlayerStrategyInterface:
    def get_player_move(self) -> PlayerMove:
        """
        Returns move according to strategy.
            Return:
                A PlayerMove indicating a player's intended move
        """
        pass

    def select_destinations(self, destinations: set, num_destinations: int) -> set:
        """
        Strategy for selecting their 2 destinations during the setup of the game.
            Parameters:
                destinations (set(Destination)): Destinations to choose 2 from according to the strategy above.
                num_destinations (int): number of destinations to pick, num_destinations <= len(destination)
            Returns:
                set(Destination): The set of destinations selected
            Throws:
                ValueError: num_destinations must be less than set size
        """
        pass

    def select_connection(self, resources: PlayerGameState) -> Connection or None:
        """
        Strategy for selecting the connection to acquire when attempting to make a connection on their turn.
        Selects the first connection from the lexicographically sorted list of given connections (unacquired connections)
        that the player has the necessary resources to acquire.
            Parameters:
                resources (PlayerGameState): the resources the player implementing this strategy has
            Returns:
                Connection to acquire if possible, None otherwise
        """
        pass

class AbstractPlayerStrategy(PlayerStrategyInterface):
    # This is maybe necessary depending on loading dynamic classes if we want to pass PlayerGameState to to function call, or have the strategy maintain it
    # def __init__(self):
    #     pass

    def get_lexicographic_order_of_destinations(self, destinations: list) -> list:
        """
        Gets the lexicographic order of a given list of destinations.  Initially sorts by the first city in each destination, and resorts
        to the second city name in each destination if the first city names are equal.
            Parameters:
                destinations (list(Destination)): The list of destinations to sort in lexicographic order
            Returns:
                The lexicographically sorted list of given destinations
        """
        # Uses the special method __lt__ (less than) written in the Destination dataclass to sort
        destinations.sort(key=functools.cmp_to_key(Destination.__lt__))
        return destinations

    def get_lexicographic_order_of_connections(self, connections: list) -> list:
        """
        Gets the lexicographic order of a given list of connections.  Initially sorts by the first city in each connection, and resorts
        to the second city name in each connection if the first city names are equal.  If both pairs of city names are equal, then the order is 
        determined by ascending order of number of segments (length of the connections), and finally the lexicographic order of the string
        representations of the connection color ("red", "green", "white", and "blue") if a tie-breaker for number of segments is required.
            Parameters:
                connections (list(Connection)): The list of connections to sort in lexicographic order
            Returns:
                The lexicographically sorted list of given connections
        """
        # Uses the special method __lt__ (less than) written in the Connection dataclass to sort
        connections.sort(key=functools.cmp_to_key(Connection.__lt__))
        return connections

    def can_acquire_connection(self, resources: PlayerGameState, unacquired_connection: Connection) -> bool:
        """
        Determines whether or not a player has enough resources (rails and corresponding colored cards) to acquire a given connection.
            Parameters:
                resources (PlayerGameState): the resources the player implementing this strategy has
                unacquired_connection (Connection): The connection being checked to see if the player has the resources to acquire it.
            Returns:
                True if the player has the necessary resources to acquire the connection, False otherwise
        """
        return resources.rails >= unacquired_connection.length and resources.colored_cards[unacquired_connection.color] >= unacquired_connection.length
