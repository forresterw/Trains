
import sys

sys.path.append('../../')

from Trains.Player.hold_10 import Hold_10
from Trains.Player.player import AbstractPlayer

class Hold_10_Player(AbstractPlayer):
    """
    Represents a player with the following strategy:
    - Draw colored cards if the player contains 10 or fewer colored cards
    - If the player has more than 10 colored cards, then attempt to acquire a connection
    - If there are no acquireable connections for the player, then draw colored cards
    """
    def __init__(self, name: str, age: int):
        """
        Constructor for the Hold_10 player strategy that takes in player name and player age.
        Uses the AbstractPlayer class constructor.
            Parameters:
                name (str): player name
                age (int): player age
        """
        super().__init__(name, age)
        self.strategy = Hold_10()


