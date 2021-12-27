import sys

sys.path.append('../../')
from Trains.Player.buy_now import Buy_Now
from Trains.Common.map import Color, Connection, City
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.moves import PlayerMove, AcquireConnectionMove

class Cheat(Buy_Now):
    """
    Bogus strategy that attempts to acquire a non-existent connection -- an illegal action in Trains.
    """

    def select_connection(self, resources: PlayerGameState) -> Connection or None:
        """
        Returns a bogus connection that does not exist on a Map. This is considered an illegal move by the Referee.
            Returns:
                Connection that does not exist.
        """
        city1 = City("Asgard", 5, 5)
        city2 = City("Hades", 6, 6)
        return Connection(frozenset({city1, city2}), Color.BLUE, 5)

    def get_player_move(self, resources: PlayerGameState) -> PlayerMove:
        """
        Attempts to acquire non-existent connection returned from the select_connection method
            Return:
                A PlayerMove indicating a player's intended move
        """
        # Always attempt to acquire a connection
        desired_connection = self.select_connection(resources)
        return AcquireConnectionMove(desired_connection)

    def select_destinations(self, destinations: set, num_destinations: int) -> set:
        """
        Uses the Buy_Now strategy for selecting their 2 destinations during the setup of the game.
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