import asyncio
from copy import deepcopy
from collections import deque
from random import randint
import sys
from typing import Callable, Deque, Dict, List, Set
import networkx as nx

sys.path.append('../../')
from Trains.Common.map import City, Destination, Map, Color, Connection
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.player import PlayerInterface
from Trains.Player.moves import MoveType
from Trains.Admin.referee_game_state import RefereeGameState
from Trains.Other.Types.trains_types import Cheaters, Edge, GameRankings, GameResult

class Cheating(Exception):
    """
    An error class that represents cheating by the player.
    This can be used to distinguish between runtime errors/exceptions
    caused by player implementation and detection of cheating.
    """
    pass

class NotEnoughDestinations(ValueError):
    """
    An error class that represents when there are not enough destinations 
    in a given map for the number of players in the game.
    """
    pass

class Referee():
    """
    Represents a referee that setups, facilitates, and ends a game of Trains.
    Should call play_game() right after __init__() to begin game and assume
    game has ended after play_game() returns. No other methods should be called
    The referee should catch Cheating in the form of:
        - Data tampering during initialization
        - Illegal moves from players
        - Errors raised from player code
        - Exceptions raised from player code
        - Type mismatch returned from player code
    and boots them from the game.
    The following will be handled after networking is implemented:
        - Unresponsive players (timeouts)
        - Incorrectly formatted/invalid input (likely json)
    """
    INITIAL_RAIL_COUNT = 45
    CARDS_ON_DRAW = 2
    INITIAL_HAND_SIZE = 4
    NUM_DESTINATIONS = 2
    NUM_DESTINATION_OPTIONS = 5
    BANNED_PLAYER_SCORE_REPRESENTATION = -21

    def __init__(self, game_map: Map, players: List[PlayerInterface], deck: Deque[Color] = None):
        """
        Constructor for the Referee that initializes fields for the setup of a game of Trains.
            Parameters:
                game_map (Map): The game map
                players (list(PlayerInterface)): The list of players in descending order of player age
            Throws:
                ValueError:
                    - The game map must be a Map
                    - The players list must be a list of 2 to 8 players
        """
        if type(game_map) != Map:
            raise ValueError("Referee must be given a valid map")
        if type(players) != list or len(players) < 2 or len(players) > 8:
            raise ValueError("Referee must get a list of [2, 8] players")

        # Constants for the setup of a game of Trains
        self.INITIAL_DECK_SIZE = 250
        
        # Used to keep track of players eliminated for cheating
        self.banned_player_indices = set()
        # Used on the last turn of the game to keep track of which players took their last turn
        self.took_last_turn = set()
        self.players = players
        # Make sure given map has enough destinations for the players.
        if  len(game_map.get_feasible_destinations(game_map.get_all_connections())) \
            < self.NUM_DESTINATION_OPTIONS + (self.NUM_DESTINATIONS * (len(self.players) - 1)):
            raise NotEnoughDestinations("Not enough destinations to give each player 5 to choose from.")
        
        self.game_map = game_map
        self.ref_game_state = None

        # If the deck is not given, then create one
        if deck is None:
            self.deck = self.initialize_deck(self.INITIAL_DECK_SIZE)
        else:
            self.deck = deck
            self.INITIAL_DECK_SIZE = len(deck)

    ###################################
    # Set Up/Pick Destination Methods #
    ###################################

    def set_up_game_states(self) -> None:
        """
        Sets up the Referee with a RefereeGameState. To do this, the Referee gives each player an initial hand of cards
        and a number of rails (as well as a map) by calling each player's setup method. It keeps track of what each
        player was giving it by creating a PlayerGameState with this information. Cards are pulled from the deck
        handed to the referee on construction. 

        Finally, after these PlayerGameStates are created, the Referee creates a RefereeGameState with these PlayerGameStates, along
        with the map and the deck and its remaining cards.

        SIDE EFFECTS:
            - Mutates the self.deck field by removing cards (Color's) from the deque.
            - Sets the self.ref_game_state (initialized to None in __init__)
        """
        player_game_states = []
        for player_index in range(len(self.players)):
            player = self.players[player_index]
            initial_hand = self.create_initial_player_hand(self.deck, self.INITIAL_HAND_SIZE)
            self.call_player_method(player_index, player.setup, self.game_map, 
                self.INITIAL_RAIL_COUNT, initial_hand)
            initial_player_state = PlayerGameState(set(), initial_hand, self.INITIAL_RAIL_COUNT, set(), dict(), list())
            player_game_states.append(initial_player_state)
        self.ref_game_state = RefereeGameState(self.game_map, self.deck, player_game_states)
    
    def players_pick_destinations(self) -> None:
        """
        For each Player inside this Referee's list of players, have the player choose some number of destinations
        from a set of destinations and give the player's PlayerGameState (inside this referee's RefereeGameState)
        those chosen destiantions.

        SIDE EFFECT: Adds each destination the player chooses to their corresponding PlayerGameState's (inside
        self.ref_game_state) destinations.
        """
        map_connections = self.game_map.get_all_connections()
        feasible_destinations = \
            self.game_map.get_feasible_destinations(map_connections)
            
        for player_index in range(len(self.players)):
            chosen_destinations = self.get_player_chosen_destinations(player_index, feasible_destinations)
            self.ref_game_state.give_player_destinations(player_index, chosen_destinations)

    def get_player_chosen_destinations(self, player_index: int, feasible_destinations: Set[Destination]) -> Set[Destination]:
        """
        Given the index of a player and the set of a map's feasible destinations that have not been chosen, 
        call the player's pick method, removes their chosen destination from feasible destinations, and 
        returns the destinations they've chosen.
        """
        player = self.players[player_index]

        # Give each player their initial destinations
        inital_player_feasible_destinations = \
            self.get_destination_selection(feasible_destinations, self.NUM_DESTINATION_OPTIONS)
        destinations_not_chosen = \
            self.call_player_method(player_index, player.pick, inital_player_feasible_destinations)
        if destinations_not_chosen is None:
            destinations_not_chosen = set()
        destinations_chosen = inital_player_feasible_destinations - destinations_not_chosen
        
        # Verify destinations chosen by the player
        if not self.verify_player_destinations(inital_player_feasible_destinations, destinations_chosen):
            self.boot_player(player_index, "Referee did not get a valid set of destinations.")
            return set()
        # Remove the destinations that this player chose from the set of feasible destinations offered to players
        else:
            feasible_destinations -= destinations_chosen
            return destinations_chosen

    def initialize_deck(self, number_of_cards: int) -> Deque[Color]:
        """
        Initializes the deck of colored cards for a game of Trains.  
        Randomly generates 'number_of_cards' colored cards.
            Parameters:
                number_of_cards (int): The initial number of cards in the deck
            Returns:
                (deque) The deck of cards
        """
        deck = deque()
        for _ in range(number_of_cards):
            next_card = Color(randint(1, Color.number_of_colors()))
            deck.append(next_card)

        return deck

    def create_initial_player_hand(self, deck: Deque[Color], initial_player_cards: int) -> Dict[Color, int]:
        """
        Creates the initial hand of colored cards for a player using cards from a given deck.
            Parameters:
                deck (deque[Color]): The deck of cards
                initial_player_cards (int): The initial number of cards in a player hand
            Returns:
                (dict[Color, int]) The player hand of colored cards as a dictionary keyed by each enum
                    defined by Color with integer values representing the amount of cards
        """
        hand = dict()
        for _ in range(initial_player_cards):
            next_card = deck.pop()
            if next_card in hand.keys():
                hand[next_card] += 1
            else:
                hand[next_card] = 1

        for i in range(1, Color.number_of_colors() + 1):
            if Color(i) not in hand.keys():
                hand[Color(i)] = 0
        
        return hand

    def get_destination_selection(self, feasible_destinations: Set[Destination], 
        number_of_destinations: int) -> Set[Destination]:
        """
        Gets the subset of feasible destinations that a player will choose their destinations from on setup.
            Parameters:
                feasible_destinations (set(Destination)): Set of all feasible destinations on a game map
                number_of_destinations (int): The number of destinations that a player can select from
            Returns:
                (set(Destination)) The set of destinations that a player will select from
        """
        destination_options = set()
        destination_list = list(feasible_destinations)
        for _ in range(min(number_of_destinations, len(destination_list))):
            random_destination = destination_list[randint(0, len(destination_list) - 1)]
            destination_options.add(random_destination)
            destination_list.remove(random_destination)

        return destination_options

    def verify_player_destinations(self, destinations_given: Set[Destination], 
        destinations_chosen: Set[Destination]) -> bool:
        """
        Verifies that a player's chosen destinations agree with the game rules (number of destinations chosen) and
        the destinations options provided.
        ONLY CALLED AFTER A PLAYER IS INITIALIZED (Once per player)
            Parameters:
                destinations_given (set(Destination)): The destinations given to a player to select from
                destinations_chosen (set(Destination)): The destinations chosen by the player
            Returns:
                True is the destinations are valid, False otherwise
        """
        if len(destinations_chosen) != self.NUM_DESTINATIONS:
            return False
        for destination in destinations_chosen:
            if destination not in destinations_given:
                return False
        return True

    ####################
    # Gameplay Methods #
    ####################

    def play_game(self) -> GameResult:
        """
        The main game functionality of a referee.
        Player states must be updated because this method is called
        right after __init__(). Then the main loop is run.
        Finally, the scores are calculated when the game ends.
        Players are notified if they won or lost, and rankings are
        calculated based on scores.
            Returns:
                Rankings as a list of lists (first place to last place) where the
                outer list represents placement and the inner lists represent players 
                who finished at a given rank (sorted by player name),
                List of banned players sorted by player name.
        """
        # Set up players with the resources they need.
        self.set_up_game_states()
        self.players_pick_destinations()

        # Main game loop
        self.main_game_loop()

        # Score the game and notify players of win status
        scores = self.score_game()
        self.notify_players(scores)
        # Return rankings and list of banned players
        return self.get_ranking_of_players(scores), self.get_banned_players()

    def main_game_loop(self) -> None:
        """
        The main gameplay loop for a game of trains.
        This handles getting player moves, taking turns,
        and booting players that cheat.
        THIS METHOD SHOULD ONLY BE CALLED ONCE BY play_game
        """
        while not self.is_game_over():
            active_player_index = self.ref_game_state.get_current_active_player_index()
            active_player = self.players[active_player_index]
            
            # Skip booted players
            if active_player_index in self.banned_player_indices:
                self.ref_game_state.next_turn()
                continue

            self.execute_active_player_move()

            # Check if game has ended
            if self.ref_game_state.on_last_turn():
                self.took_last_turn.add(active_player)

            if self.is_game_over():
                break  # ends the game

            # Get next turn
            self.ref_game_state.next_turn()

    def is_game_over(self) -> bool:
        """
        Determines if the game is over
        This implementation checks that game_state changes and all players
        have taken their last turn (after the rails of any player drop below 3)
        """
        return self.ref_game_state.no_change_after_cycle() or self.all_last_turns_taken() or (len(self.players) - len(self.banned_player_indices) == 0)

    # TODO: Add more method to player?
    def execute_draw_move(self) -> None:
        """
        Executes the draw cards move for the active player.
        THIS MUTATES THE REFEREE GAME STATE FOR THE ACITVE PLAYER
        """
        new_cards = self.ref_game_state.get_cards_from_deck(self.CARDS_ON_DRAW)
        self.ref_game_state.give_cards_to_active_player(new_cards)
        self.call_player_method(self.ref_game_state.turn, self.get_active_player().more, new_cards)

    def execute_acquire_connection_move(self, connection: Connection) -> None:
        """
        Executes the acquire connection move for the active player. Boots the player if their acquisition request is 
        not legal.

        SIDE EFFECT: THIS MUTATES THE REFEREE GAME STATE FOR THE CORRESPONDING PLAYER BY GIVING THEM THE CONNECTION IF 
        IT IS A LEGAL ACQUIISTION. The field self.ref_game_state.free_connections updated when the next player takes
        their turn and next_turn() is called.

            Parameters:
                connection (Connection): The connection that the currently active player is attempting to acquire
        """
        valid = self.ref_game_state.verify_legal_connection(connection)
        if valid:
            self.ref_game_state.add_connection_to_active_player(connection)
        else:
            self.boot_player(self.ref_game_state.turn, "Connection given is not able to be acquired.")
    
    def execute_active_player_move(self) -> None:
        """
        Executes the player active player's move if it is legal, otherwise boots the player.

        SIDE EFFECT: Mutates the referee game state by doing one of the following:
            - Giving a player a connection they legally acquire. The field self.ref_game_state.free_connections updated when the next player takes
              their turn and next_turn() is called.
            - Removing cards from the deck and giving them to a player (changes self.ref_game_state.colored_card_deck).
        """
        # Get move
        active_player_index = self.ref_game_state.turn
        active_player_state = self.ref_game_state.get_player_game_state()
        move = self.call_player_method(active_player_index, self.get_active_player().play, active_player_state)

        # Execute move
        if move is None:
            self.boot_player(active_player_index, "Given action was not valid.")
        elif move.move_type == MoveType.DRAW_CARDS:
            self.execute_draw_move()
        elif move.move_type == MoveType.ACQUIRE_CONNECTION:
            self.execute_acquire_connection_move(move.connection)
        else:
            self.boot_player(active_player_index, "Given action was not valid.")
            
    def get_active_player(self) -> PlayerInterface:
        """
        Returns the Player who is currently taking their turn.
            Return: Player object for the active player.
        """
        return self.players[self.ref_game_state.turn]

    def all_last_turns_taken(self) -> bool:
        """
        Determines if all players have taken their last turn
            Return:
                bool: True if all players took their last turn, else False
        """
        return len(self.took_last_turn) == (len(self.players) - len(self.banned_player_indices))

    ##########################
    # Scoring/Result Methods #
    ##########################

    def score_game(self) -> List[int]:
        """
        Calculates the score of the game for each player and returns as a list
        This list corresponds to the player_list held by this referee
            Return:
                player_scores (list(int)): list of scores corresponding to players
        """
        player_scores = list()
        longest_path = dict()

        for player_index in range(len(self.players)):
            if player_index not in self.banned_player_indices:
                longest_path[player_index] = self.find_longest_continuous_path_for_player(player_index)

        for player_index in range(len(self.players)):
            if player_index not in self.banned_player_indices:
                longest_path_flag = False
                if longest_path[player_index] == max(longest_path.values()):
                    longest_path_flag = True
                player_scores.append(self.score_game_for_player(player_index, longest_path_flag))
            else:
                player_scores.append(self.BANNED_PLAYER_SCORE_REPRESENTATION)

        return player_scores

    def score_game_for_player(self, player_index: int, longest_path: bool) -> int:
        """
        Gets the score that this PlayerInterface has earned overall
            Parameters:
                player_index (int): Index of the player to score
                longest_path (bool): True if this player has the longest path, False otherwise
            Return:
                score (int): score for destinations owned by this player
        """
        RAIL_SEGMENT_POINT_VALUE = 1
        LONGEST_CONTINUOUS_PATH_VALUE = 20
        DESTINATION_COMPLETE_VALUE = 10

        player_game_state = self.ref_game_state.player_game_states[player_index]
        score = 0

        score += self.get_connection_score(player_game_state, RAIL_SEGMENT_POINT_VALUE)

        score += self.get_destination_score(player_game_state, DESTINATION_COMPLETE_VALUE)

        if longest_path:
            score += LONGEST_CONTINUOUS_PATH_VALUE

        return score

    def notify_players(self, scores: list) -> None:
        """
        Notifies player whether or not they won based on scores.
        Banned players will not be notified.
            Parameters:
                scores (list): scores corresponding to players
        """
        highest_score = max(scores)

        for player, score in zip(self.players, scores):
            did_win = False
            player_index = self.players.index(player)
            if player_index not in self.banned_player_indices:
                if score == highest_score:
                    did_win = True
                self.call_player_method(player_index, player.win, did_win)

    def find_longest_continuous_path_for_player(self, player_index: int) -> int:
        """
        Finds the longest continuous path that each player can create with
        the connections that they posess.
        SOURCE: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html#networkx.algorithms.simple_paths.all_simple_paths
            Parameters:
                player (int): The index of the player to find a connection for
            Return:
                connection_length (int): Length of player's longest connection
        """
        trains_graph = nx.MultiGraph()
        player_cities = set()
        # Create a graph using the game map
        for connection in self.ref_game_state.player_game_states[player_index].connections:
            for city in connection.cities:
                player_cities.add(city)
        for city in player_cities:
            trains_graph.add_node(city)
        for connection in self.ref_game_state.player_game_states[player_index].connections:
            city1 = list(connection.cities)[0]
            city2 = list(connection.cities)[1]
            weight = connection.length
            trains_graph.add_edge(city1, city2, weight=weight)

        # Get all simple paths in the graph between all cities connected via some path
        simple_paths = []
        for source_city in player_cities:
            for dest_city in player_cities:
                simple_paths += nx.all_simple_paths(trains_graph, source_city, dest_city)

        # Get the weight (length) of the longest path out of all the simple paths
        max_weight = 0
        for path in map(nx.utils.pairwise, simple_paths):
            path_weight = self.max_weight_of_simple_path(trains_graph, list(path))
            if path_weight > max_weight:
                max_weight = path_weight

        return max_weight

    def max_weight_of_simple_path(self, graph: nx.MultiGraph, path: List[Edge]) -> int:
        """
        Gets the max weight path from a set of graphs
        THIS METHOD SHOULD ONLY BE CALLED BY get_longest_path
        SOURCE: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html#networkx.algorithms.simple_paths.all_simple_paths
            Parameters:
                graph (nx.MultiGraph): the graph that paths belong to
                path (list(edge)): paths to compare | edge is a tuple of two nodes
            Return:
                weight (int): max weight of the given path
        """
        weight = 0
        for edge in path:
            edge_weight_options = []
            # get_edge_data creates a dictionary of edge attributes (weights) for all edges in the given path  
            for edge_weight_index in graph.get_edge_data(*edge).keys():
                edge_weight_options.append(graph.get_edge_data(*edge)[edge_weight_index]['weight'])
            weight += max(edge_weight_options)

        return weight

    def get_connection_score(self, player_resources: PlayerGameState, score_value: int) -> int:
        """
        Gets the score that this player resources is worth for connections
            Parameters:
                player_resources (PlayerGameState): given PlayerGameState to score
                score_value (int): value of a segment
            Return:
                score (int): score for connections owned by this player
        """
        score = 0
        for connection in player_resources.connections:
            score += connection.length * score_value

        return score

    def get_destination_score(self, player_resources: PlayerGameState, score_value: int) -> int:
        """
        Gets the score that this player resources is worth for destinations
            Parameters:
                player_resources (PlayerGameState): given PlayerGameState to score
                score_value (int): value of a segment
            Return:
                score (int): score for destinations owned by this player
        """
        score = 0
        for destination in player_resources.destinations:
            city1, city2 = list(destination)
            if city2 in self.ref_game_state.map.get_all_terminal_cities_from_city(city1, player_resources.connections):
                score += score_value
            else:
                score -= score_value
        return score

    ##########################
    # Player-related Methods #
    ##########################

    def boot_player(self, player_index: int, reason: str = ""):
        """
        Boots players that are caught cheating.  Booted players no longer take turns, their connections become
        available again, and their resources (rails and colored cards) are discarded.
            Parameters:
                player_index (int): The index of the player being booted
                reason (str): The reason why they are being booted
        """
        if self.ref_game_state is not None:
            self.ref_game_state.clear_player_connections(player_index)

        try:
            if player_index not in self.banned_player_indices:
                self.banned_player_indices.add(player_index)
                self.players[player_index].boot_player_from_game(reason)
        except:
            # Indicates error from booting player
            # This will not cause any problems to the existing system
            # as players are given a reason for booting as a courtesy
            pass

    def call_player_method(self, player_index: int, player_method: Callable, *args):
        """
        Given a player method and arugments, return the result of calling that method.  
        Single point of control for calling a player's methods.
            Parameters:
                player_index (int): The index of the player executing the method
                player_method (Callable): The player method to execute
                *args: The arguments for the given method
            Returns:
                The result of the given player method
        """
        try:

            method = getattr(self.players[player_index], player_method.__name__)
            result = method(*args)
            return result
        except Exception as e:
            self.boot_player(player_index, "Game held up due to a logic error. Player booted.")

    def get_ranking_of_players(self, scores:list) -> GameRankings:
        """
        Given the final scores of the game's players in the turn order during the game,
        return a list of the players in the order of highest to lowest score.
            Parameters:
                scores: List of players' scores in the original turn order of the game.
            Returns:
                The ranking of the players by order of highest to lowest score.  Players who have
                the same score are sorted within their rank by name.
        """
        # Create tuples of player and their scores and sort them descending based on score
        player_scores = [(self.players[i], scores[i]) for i in range(len(scores))]
        player_scores.sort(key=lambda x: x[1], reverse=True)

        rankings = []

        prev_score = self.BANNED_PLAYER_SCORE_REPRESENTATION
        current_index = -1
        for player_score in player_scores:
            # Do not rank banned players
            if player_score[1] == self.BANNED_PLAYER_SCORE_REPRESENTATION:
                continue
            # Handles players who tied (have the same score)
            if current_index == -1 or prev_score != player_score[1]:
                rankings.append([])
                current_index += 1
                rankings[current_index].append(player_score)
                prev_score = player_score[1]
            else:
                rankings[current_index].append(player_score)
        
        # Sort tied players by their names
        for rank in rankings:
            rank.sort(key=lambda ps: ps[0].name)
                
        return rankings

    def get_banned_players(self) -> List[PlayerInterface]:
        """
        Gets the list of banned players sorted by player name
            Returns:
                List of banned players sorted by name
        """
        banned_players = [self.players[i] for i in self.banned_player_indices]
        banned_players.sort(key=lambda player: player.name)
        return banned_players

    ######################
    # Deprecated Methods #
    ######################

    def update_player_states(self):
        """
        Updates all playes with the state they should have at a given point
        MUTATES player_game_state of each player
        """
        for player_index in range(len(self.players)):
            if player_index not in self.banned_player_indices:
                self.update_specific_player_state(player_index)

        # Here would be where observers are updated
        # However that is to be implemented

    def update_specific_player_state(self, specific_player_index: int):
        """
        Updates the state of each player to reflect what shouold be visible
        to them
            Parameters:
                specific_player_index(int): Index of the player to compute state for
        """
        # Referee needs to get the new state for the Player and update their internal
        # state for that player.
        updated_state = self.generate_updated_state_for_player(specific_player_index)
        self.ref_game_state.player_game_states[specific_player_index] = updated_state

        self.call_player_method(specific_player_index, self.players[specific_player_index].update_player_game_state, updated_state)

    def generate_updated_state_for_player(self, player_index: int):
        """
        Create a PlayerGameState object that accurately reflects a player's
        knowledge at the time of this method call.
            Parameters:
                player_index(int): Index of player to generate state for
            Return:
                PlayerGameState: A resource representing given players state
        """
        player_resources = self.ref_game_state.player_game_states[player_index]
        hand = player_resources.colored_cards
        rails = player_resources.rails
        connections = player_resources.connections
        destinations = player_resources.destinations

        # Game info dict
        game_info = {}
        game_info["unacquired_connections"] = self.ref_game_state.get_all_unacquired_connections()
        game_info["cards_in_deck"] = len(self.ref_game_state.colored_card_deck)
        game_info["last_turn"] = self.ref_game_state.on_last_turn()

        # List of opponent information dictionaries.
        opponent_info = []

        for opponent_index in range(len(self.players)):
            opponent_entry = {}
            if opponent_index == player_index:
                continue

            # If player is opponent, add information about their acquired connections and the number of cards
            # that they have.
            opponent_entry["connections"] = self.ref_game_state.player_game_states[opponent_index].connections
            opponent_entry["number_of_cards"] = self.ref_game_state.player_game_states[opponent_index].get_number_of_colored_cards()
            opponent_info.append(opponent_entry)

        return deepcopy(PlayerGameState(connections, hand, rails, destinations, game_info, opponent_info))

