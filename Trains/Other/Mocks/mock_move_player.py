import sys


sys.path.append("../../../")
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.moves import PlayerMove
from Trains.Player.player import AbstractPlayer
from Trains.Player.buy_now import Buy_Now
from Trains.Player.hold_10 import Hold_10


class BadMove(PlayerMove):
    """
    An invalid player move that is used for creating a cheating player
    """
    def __init__(self):
        self.move_type = None

class MockConfigurablePlayer(AbstractPlayer):
    """
    Mock Player used for testing.  Always returns the given PlayerMove.
    """
    def __init__(self, name: str, age: int, move: PlayerMove):
        """
        Initializes an instance of a mock player
            Parameters:
                name (str): Player name
                age (int): Player age
        """
        super().__init__(name, age)
        self.move = move
        self.strategy = Hold_10()
        self.is_winner = None
        self.booted = False

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

    # def pick(self, destination_options: set) -> set:
    #     """
    #     Picks all of the destinations options given
    #     """
    #     return destination_options


class MockBuyNowPlayer(AbstractPlayer):
    """
    Represents a player with the following strategy:
    - Always attempt to acquire a connection first
    - If there are no acquireable connections, then draw cards
    """
    def __init__(self, name: str, age: int):
        """
        Constructor for the Buy_Now player strategy that takes in player name and player age.
        Uses the AbstractPlayer class constructor.
            Parameters:
                name (str): player name
                age (int): player age
        """
        super().__init__(name, age)
        self.strategy = Buy_Now()
        self.is_winner = None
        self.booted = False
    
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