import asyncio
from copy import copy
from typing import Any, Callable, Deque, List
import sys, json, os

sys.path.append('../../')
from Trains.Other.Types.trains_types import GameAssignment, GameRankings, TournmentResult
from Trains.Common.map import Color, Map
from Trains.Other.Util.json_utils import convert_json_map_to_data_map
from Trains.Admin.referee import Referee, NotEnoughDestinations
from Trains.Player.player import PlayerInterface

class Manager:
    """
    Represents a tournament manager that sets up and runs a tournament for games of Trains.
    The active players list will represent the tournament winners at the end of the 
    tournament, since it is a knock-out elimination system.
    """

    MAXPLAYERS_IN_A_GAME = 8

    def __init__(self, players: List[PlayerInterface], deck: Deque[Color] = None):
        """
        Constructor for the tournament manager that sets up a tournament with the given players.
        Players are notified of the start of the tournament upon Manager initialization.
        An initialized Manager can simply call 'run_tournament' to run a tournament.
            Parameters:
                players (list): List of players to setup for a tournament
            Raises:
                ValueError:
                - The given players is not a list
                - The given players list has less than the minimum number of players to play a game of Trains (2)
        """
        if type(players) != list:
            raise ValueError("Manager must get a list of players")

        self.MIN_PLAYERS_IN_A_GAME = 2
        if len(players) < self.MIN_PLAYERS_IN_A_GAME:
            raise ValueError(f"Manager must get a list of at least {self.MIN_PLAYERS_IN_A_GAME} players")

        # Represents players who have not eliminated for losing or for misbehaving.
        self.active_players = players
        # Players who were eliminated for misbehaving.
        self.banned_players = []

        self.deck = deck
        self.tournament_map = None

        self.num_active_players = len(self.active_players)
        self.prev_num_active_players = self.num_active_players
        self.round_without_change = 0

    ####################
    # Tournament Setup #
    ####################

    def set_up_tournament(self) -> Map:
        """
        Sets up a tournament by getting game maps from all the players. It then returns 
        the first valid map submitted.

            Returns:
                A game map to be used during the tournament.

            Raises:
                NotEnoughDestinations if none of the maps given by players are valid for
                the maximum number of players a game assignment could get.            
        """
        suggested_maps = self.get_player_maps()
        max_players_in_game_assignment = min(len(self.active_players), self.MAXPLAYERS_IN_A_GAME)
        game_map = self.get_valid_map(max_players_in_game_assignment, suggested_maps)
        return game_map

    def get_valid_map(self, number_of_players: int, suggested_maps: List[Map]) -> Map:
        """
        Gets a valid map from the given list of suggested maps and the number of players that
        will be playing in a game.
            Parameters:
                number_of_players: The number of players that will be playing in a game
                suggested_maps: A list of maps suggested by players
            Returns:
                The first valid map found in the list of suggested maps.
            Raises:
                A NotEnoughDestinations exception if there are no valid maps.
        """
        for game_map in suggested_maps:
                if self.verify_suggested_map(game_map, number_of_players):
                    return game_map
        raise NotEnoughDestinations()

    def get_player_maps(self) -> List[Map]:
        """
        For all players given to the manager, asks them for a map to be considered
        for use tournmnament games. Assuming the player submits a valid map and is not 
        booted, their map will be added to a list to be returned at the end of the method.

            Returns: List of maps received from players.
        """
        suggested_maps = []
        for player in self.active_players:
            suggested_map = self.call_player_method(player, player.start)
            if suggested_map is not None and suggested_map not in suggested_maps:
                suggested_maps.append(suggested_map)
            elif suggested_map is None and player not in self.banned_players:
                self.boot_player(player, "Player booted for submitting a null Map.")
        self.remove_banned_players_from_active()
        return suggested_maps   

    def verify_suggested_map(self, game_map: Map, number_of_players: int) -> bool:
        """
        Verifies whether or not a given map can be used by a given number of players.
            Parameters:
                game_map (Map): the game map that is being verified
                number_of_players (int): The number of players that would be using the given map
            Returns:
                True if the map can be used with the given number of players. False Otherwise.
        """
        num_destination_options = 5
        num_destination_per_player = 2
        return len(game_map.get_feasible_destinations(game_map.get_all_connections())) \
            >= num_destination_options + (num_destination_per_player * (number_of_players - 1))

    ###################
    # Tournament Play #
    ###################

    def run_tournament(self) -> TournmentResult:
        """
        The main tournament functionality a of manager.  Runs the main tournament loop to get the
        winners and notify all non-misbehaving participants of the tournament results.
            Returns:
                tournament_winners (list): List of winners of the last game in the tournament (sorted by name),
                banned_players (list): List of players that were caught misbehaving in games/tournament
        """
        self.tournament_map = self.set_up_tournament()
        self.main_tournament_loop()

        # Save winners and cheaters to local variable since
        # an error communicating with the winners does not
        # change the fact that they won.
        winners = copy(self.active_players)
        winners.sort(key=lambda player: player.name)

        misbehaved = copy(self.banned_players)
        misbehaved.sort(key=lambda player: player.name)
        
        self.notify_players_with_results()
        return self.active_players, self.banned_players

    def main_tournament_loop(self) -> None:
        """
        The main loop for running a knock-out elimination tournament.
            Returns:
                tournament_winners (list): list of winners of the last game in the tournament (sorted by name)
        """
        while True:
            game_assignments = self.assign_players_to_games()
            self.run_tournament_round(game_assignments)
            if len(game_assignments) <= 1 or self.no_change_in_winners():
                break

    def run_tournament_round(self, game_assignments: List[GameAssignment]) -> None:
        """
        Starts games of Trains using the given game assignments of players, given game map,
        .
        Gets the results of each game (rankings and banned players) and eliminates losing players 
        and banned players from the tournament.
            Parameters:
                game_assigments (list(list(Player))): list of a lists of players where each inner
                                              list represents the 2-8 players in a game of trains
        """
        for assignment in game_assignments:
            ref = Referee(self.tournament_map, assignment, self.deck)
            game_rankings, cheaters = ref.play_game()
            # Eliminate losing players
            multiple_ranks = len(game_rankings) >= 2
            if multiple_ranks:
                second_place_index = 1
                self.eliminate_losing_players(game_rankings[second_place_index:])
            # Eliminate banned players
            self.banned_players.extend(cheaters)
            self.remove_banned_players_from_active()

    def assign_players_to_games(self) -> List[GameAssignment]:
        """
        Break up players list into smaller lists of 2-8 players to be given to a Referee
        to start a game of Trains.

            Returns:
                game_assignments: list of a lists of players where 
                    each inner list represents the 2-8 players in a game of trains
        """ 
        game_assignments = []
        if len(self.active_players) < self.MIN_PLAYERS_IN_A_GAME:
            return game_assignments
        
        curr_assignment = []
        for player in self.active_players:
            curr_assignment.append(player)
            if len(curr_assignment) == self.MAXPLAYERS_IN_A_GAME:
                game_assignments.append(curr_assignment)
                curr_assignment = []

        # Need to backtrack to assign additional player to game with too few players
        if len(curr_assignment) == (self.MIN_PLAYERS_IN_A_GAME - 1):
            last_assigned_index = len(game_assignments[-1]) - 1
            last_player_assigned = game_assignments[-1].pop(last_assigned_index)
            curr_assignment.insert(0, last_player_assigned)

        # Sort and append the last assignment if the number of players isn't divisible
        # by the max number of players in a game
        if len(curr_assignment) >= self.MIN_PLAYERS_IN_A_GAME:
            game_assignments.append(curr_assignment)

        return game_assignments

        """
        Verifies whether or not a given map can be used by a given number of players.
            Parameters:
                game_map (Map): the game map that is being verified
                number_of_players (int): The number of players that would be using the given map
            Returns:
                True if the map can be used with the given number of players. False Otherwise.
        """
        num_destination_options = 5
        num_destination_per_player = 2
        return len(game_map.get_feasible_destinations(game_map.get_all_connections())) \
            >= num_destination_options + (num_destination_per_player * (number_of_players - 1))

    def eliminate_losing_players(self, losing_player_rankings: GameRankings) -> None:
        """
        Handles the elimination of players who lost in the game of trains.
            Parameters:
                losing_player_rankings (list(list(tuple(Player, int)))): The rankings of the  losing players
                                                                         from a game of trains
        """
        for ranking in losing_player_rankings:
            for player_results in ranking:
                self.active_players.remove(player_results[0])

    def no_change_in_winners(self) -> bool:
        """
        Detects if two rounds of the tournament have played with the same results each time.

        SIDE EFFECT: 
            - If no players are knocked out after tournament round completion, the 
            self.round_without_change field is incremented by 1.
            - If some number of players are knocked out after the tournament, self.round_without_change
            is set to 0. 


            Returns:
                True if two rounds have passed without change, Otherwise False
        """
        self.num_active_players = len(self.active_players)
        if self.num_active_players == self.prev_num_active_players:
            self.round_without_change += 1
            return self.round_without_change == 2
        self.prev_num_active_players = self.num_active_players
        self.round_without_change = 0
        return False

    #######################
    # Ending a Tournament #
    #######################

    def notify_players_with_results(self) -> None:
        """
        Notifies all remaining active players, who are the winners of the tournament,
        that the tournament has ended and that they have won.
        """
        # Notify winners
        for player in self.active_players:
            self.call_player_method(player, player.end, True)

    #################################
    # Useful Player-related Methods #
    #################################
    
    def call_player_method(self, player: PlayerInterface, player_method: Callable, *args) -> Any:
        """
        Given a player method and arugments, return the result of calling that method.  
        Single point of control for calling a player's methods.
            Parameters:
                player (PlayerInterface): The player executing the method
                player_method (Callable): The player method to execute
                *args: The arguments for the given method
            Returns:
                The result of the given player method
        """

        try:
            method = getattr(player, player_method.__name__)
            method_output = method(*args)
            return method_output
        except Exception as e:
            print(e)
            self.boot_player(player, "Tournament held up due to a logic error. Player booted.")

    def remove_banned_players_from_active(self) ->  None:
        """
        Removes all players stored in the banned_players internal list from active_players internal list
        if they are in active_players.

        SIDE EFFECT: Mutates self.active_players through removal players.
        """
        for banned_player in self.banned_players:
            if banned_player in self.active_players:
                self.active_players.remove(banned_player)

    def boot_player(self, player: PlayerInterface, reason: str = "") -> None:
        """
        Boots players that are holding up the tournament.  Booted players are not entered into tournaments.
            Parameters:
                player: The player being booted
                reason: The reason why they are being booted
        
        SIDE EFFECT: Player is appended to the self.banned_players list.
        """
        print(reason)

        self.banned_players.append(player)
        try:
            player.boot_player_from_tournament(reason)
        except:
            # Indicates error from booting player
            # This will not cause any problems to the existing system
            # as players are given a reason for booting as a courtesy
            pass