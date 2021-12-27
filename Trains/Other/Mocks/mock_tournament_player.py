import sys, json

sys.path.append("../../../")
from Trains.Common.player_game_state import PlayerGameState
from Trains.Common.map import Map
from Trains.Player.strategy import PlayerStrategyInterface
from Trains.Player.moves import PlayerMove
from Trains.Player.player import AbstractPlayer
from Trains.Player.hold_10 import Hold_10
from Trains.Other.Util.json_utils import convert_json_map_to_data_map

class MockTournamentPlayer(AbstractPlayer):
    """
    Mock Player used for testing.  Always returns the given PlayerMove.
    """
    def __init__(self, name: str, age: int, move: PlayerMove = None, game_map_file_path: str = None, strategy: PlayerStrategyInterface = Hold_10()):
        """
        Initializes an instance of a mock player
            Parameters:
                name (str): Player name
                age (int): Player age
        """
        super().__init__(name, age)
        self.started = False
        self.move = move
        self.game_map_file_path = game_map_file_path
        self.strategy = strategy
        self.is_game_winner = None
        self.booted = False
        self.is_tournament_winner = None

    def play(self, game_state: PlayerGameState) -> PlayerMove:
        """
        The overriden play method for a mock player
            Parameters:
                game_state (PlayerGameState): the player game state
            Returns:
                (PlayerMove) the given move initialized in the constructor
        """
        if self.move is None:
            return self.strategy.get_player_move(game_state)
        return self.move

    def win(self, winner: bool):
        """
        Sets the is_winner field to given 'winner' boolean
            Parameters:
                winner (bool): Whether or not the player won (True) or lost (False)
        """
        self.is_game_winner = winner
    
    def boot_player_from_game(self, reason_for_boot: str):
        """
        Sets the booted field to true if this is called 
        """
        self.booted = True
    
    def boot_player_from_tournament(self, reason_for_boot: str):
        """
        Sets the booted field to true if called.
        """
        self.booted = True

    def start(self):
        if self.game_map_file_path is None:
            self.game_map_file_path = "../../../Trains/Other/Examples/Maps/example_map1.json"

        with open(self.game_map_file_path) as map_file:
            json_game_map = json.load(map_file)
            game_map = convert_json_map_to_data_map(json_game_map)
            return game_map

    def end(self, winner: bool):
        self.is_tournament_winner = winner

class MockTournamentPlayerNoMap(MockTournamentPlayer):
    def start(self):
        return None

class MockTournamentCheaterStart(MockTournamentPlayer):
    def start(self):
        raise TimeoutError

class MockTournamentCheaterEnd(MockTournamentPlayer):
    def end(self, winner: bool):
        raise TimeoutError