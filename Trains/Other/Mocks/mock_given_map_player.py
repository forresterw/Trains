import sys, json
sys.path.append("../../../")

from Trains.Common.map import Map
from Trains.Player.dynamic_player import DynamicPlayer


class MockGivenMapPlayer(DynamicPlayer):
    """Implementation of player that takes in a map object in the constructor."""

    def __init__(self, name: str, age: int, path: str, map: Map):
        """Constructs a Player with a given map"""
        super().__init__(name, age, path)
        self.map = map

    def start(self) -> Map:
        return self.map

