import sys
sys.path.append("../../../")
from Trains.Common.map import Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.moves import DrawCardMove, PlayerMove
from Trains.Player.player import AbstractPlayer
from Trains.Player.buy_now import Buy_Now
from Trains.Player.hold_10 import Hold_10


class MockBadSetUpPlayer(AbstractPlayer):
    """
    Mock Player used for testing.  Always returns the given PlayerMove.
    """
    def __init__(self, name: str, age: int):
        """
        Initializes an instance of a mock player
            Parameters:
                name (str): Player name
                age (int): Player age
        """
        super().__init__(name, age)
        self.move = DrawCardMove()
        self.strategy = Hold_10()
        self.is_winner = None
        self.booted = False
    
    def setup(self, map: Map, rails: int, cards: dict):
        raise TimeoutError

    def play(self, game_state: PlayerGameState) -> PlayerMove:
        """
        The overriden play method for a mock player
            Parameters:
                game_state (PlayerGameState): the player game state
            Returns:
                (PlayerMove) the given move initialized in the constructor
        """
        return self.move

    def win(self, winner: bool):
        """
        Sets the is_winner field to given 'winner' boolean
            Parameters:
                winner (bool): Whether or not the player won (True) or lost (False)
        """
        self.is_winner = winner
    
    def boot_player_from_game(self, reason_for_boot: str):
        """
        Sets the booted field to true if this is called 
        """
        self.booted = True

    def pick(self, destination_options: set) -> set:
        """
        Picks the first two destinations.
        """
        return destination_options[:2]