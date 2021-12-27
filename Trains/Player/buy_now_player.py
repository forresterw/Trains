
import sys


sys.path.append('../../')
from Trains.Player.buy_now import Buy_Now
from Trains.Player.player import AbstractPlayer



class Buy_Now_Player(AbstractPlayer):
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
