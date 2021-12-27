from copy import deepcopy
import json, os, sys
from collections import deque
from typing import List

sys.path.append("../../../")
from Trains.Other.Util.json_utils import convert_json_map_to_data_map
from Trains.Admin.manager import Manager
from Trains.Admin.referee import Referee, NotEnoughDestinations
from Trains.Common.map import Map
from Trains.Other.Types.trains_types import GameAssignment

class ConfigurableManager(Manager):

    def __init__(self, players: list, deck: deque = None, use_default: bool = False):
        """
        Constructor that initializes a ConfigurableManager. Takes in a list of players to be used normally (as a Manager would),
        and optionally a custom deck for use by the Referee.
            Parameters:
                players (list): List of players for a tournament.
                deck (deque): Custom deck for use during tournament games.
        """
        self.use_default = use_default
        super().__init__(players, deck)


    def run_tournament_round(self, game_assignments: List[GameAssignment]) -> None:
        """
        Starts games of Trains using the given game assignments of players and suggested maps.
        Gets the results of each game (rankings and banned players) and eliminates losing players 
        and banned players from the tournament.
            Parameters:
                game_assigments (list(list(Player))): list of a lists of players where each inner
                                              list represents the 2-8 players in a game of trains
        """
        for assignment in game_assignments:
            game_map = self.tournament_map
            if self.deck is not None:
                ref = Referee(game_map, assignment, deepcopy(self.deck))
            else:
                ref = Referee(game_map, assignment)
            game_rankings, cheaters = ref.play_game()
            # Eliminate losing players
            if len(game_rankings) >= 2:
                self.eliminate_losing_players(game_rankings[1:])
            # Eliminate banned players
            self.banned_players.extend(cheaters)
            self.remove_banned_players_from_active()

    def get_valid_map(self, number_of_players: int, suggested_maps: List[Map]) -> Map:
        """
        Gets a valid map from the given list of suggested maps and the number of players that
        will be playing in a game.
            Parameters:
                number_of_players (int): The number of players that will be playing in a game
                suggested_maps (list): A list of maps suggested by players
            Returns:
                game_map (Map): The first valid map found in the list of suggested maps or None if no
                                valid maps are found
        """
        for game_map in suggested_maps:
            if self.verify_suggested_map(game_map, number_of_players):
                return game_map
        if self.use_default:
            return self.load_default_map()
        else:
            raise NotEnoughDestinations()
    
    def load_default_map(self) -> Map:
        # REL_DEFAULT_MAP_PATH = "../../Trains/Other/Examples/Maps/default_map1.json"
        # TODO: Relative file path is only relative to unit test folder
        REL_DEFAULT_MAP_PATH = "../Examples/Maps/default_map1.json"
        ABS_DEFAULT_MAP_PATH = os.path.abspath(REL_DEFAULT_MAP_PATH)
        with open(ABS_DEFAULT_MAP_PATH) as map_file:
            json_game_map = json.load(map_file)
            game_map = convert_json_map_to_data_map(json_game_map)
            return game_map
