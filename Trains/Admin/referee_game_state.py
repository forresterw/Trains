import sys
from copy import deepcopy, copy
from collections import deque
from typing import List, Set

sys.path.append('../../')
from Trains.Common.map import Color, Connection, Destination, Map
from Trains.Common.player_game_state import PlayerGameState


class RefereeGameState:
    """
    Represents a referee game state that keeps track of player game states (PlayerGameState) and
    which player's turn it is.  Also handles the verification of players acquiring connections, and
    determines what connections are available to the currently active player.
    """
    def __init__(self, map: Map, colored_card_deck: deque, player_game_states: list):
        """
        Constructor for RefereeGameState that verifies given fields and initializes class fields to setup a game.
            Parameters:
                map (Map): The game map
                colored_card_deck (deque): A deque of colored cards representing the deck of colored cards
                player_game_states (list): A list of PlayerGameState provided by the referee (in sorted order) 
            Throws:
                ValueError:
                    - The given map must be of type Map
                    - The deck of colored cards must be a deque
                    - The player game states must be a list and each one a PlayerGameState
        """
        if type(map) != Map:
            raise ValueError("The given map must be a Map")
        if type(colored_card_deck) != deque:
            raise ValueError("The colored card deck must be a deque")
        if type(player_game_states) != list:
            raise ValueError("The given player game states must be a list.")
        for entry in player_game_states:
            if type(entry) != PlayerGameState:
                raise ValueError("Entry in list of PlayerGameStates must be a PlayerGameState.")
        
        self.map = map
        self.player_game_states = player_game_states
        self.turn = 0

        self.free_connections = self.get_all_unacquired_connections()
        self.colored_card_deck = colored_card_deck

        self.no_change = False
        self.prev_state = None
        self.prev_num_connections = len(self.free_connections)
        self.prev_num_cards = len(self.colored_card_deck)
        self.turn_of_state_change = 0

    def __eq__(self, other) -> bool:
        return type(other) == RefereeGameState and self.map == other.map and \
            list(self.colored_card_deck) == list(other.colored_card_deck) and \
                self.player_game_states == other.player_game_states

    def get_current_active_player_index(self) -> int:
        """
        Returns the currently active player
        INTENDED CALLER: Referee
        """
        return self.turn

    def next_turn(self) -> None:
        """
        Increments the turn counter to the active player's index. This method also frees up any connections
        players no longer have (i.e., if they've been banned), as well as checks to see if the RefereeGameState
        changed last turn.
        """
        self.turn = (self.turn + 1) % len(self.player_game_states)
        self.free_connections = self.get_all_unacquired_connections()
        self.detect_state_change()

    def detect_state_change(self) -> None:
        """
        Detects if every player has gotten a turn and the game state has not changed.
        
        SIDE EFFECTS: This method mutates this object's fields for no_change, prev_state, 
        and turn_of_state_change
        """
        if self.was_state_change():
            self.no_change = self.turn == self.turn_of_state_change
        else:
            self.turn_of_state_change = self.turn
            self.prev_num_cards = len(self.colored_card_deck)
            self.prev_num_connections = len(self.free_connections)
    
    def was_state_change(self) -> bool:
        """
        Determines if the referee game state has changed. This is computed by comparing the previous number
        of available connections and the previous number of cards in the deck.
            Returns:
                (boolean) True if the state has changed, else false.
        """
        return self.prev_num_cards == len(self.colored_card_deck) \
            and len(self.free_connections) == self.prev_num_connections

    def get_player_game_state(self) -> PlayerGameState:
        """
        Gets the player game state (PlayerGameState) of the currently active player.
            Returns:
                The PlayerGameState of the currently active player.
        """
        current_game_state = self.player_game_states[self.turn]

        # Setup player's game info.
        game_info = {}
        game_info["unacquired_connections"] = self.get_all_unacquired_connections()
        game_info["cards_in_deck"] = len(self.colored_card_deck)
        game_info["last_turn"] = self.on_last_turn()

        # Set up opponent info.
        opponent_info = []
        for pgs_ind in range(len(self.player_game_states)):
            opponent_game_state = self.player_game_states[pgs_ind]
            entry = {}
            entry["number_of_cards"] = \
                opponent_game_state.get_number_of_colored_cards()
            entry["connections"] = opponent_game_state.connections
            opponent_info.append(entry)

        active_game_state = \
            PlayerGameState(current_game_state.connections, current_game_state.colored_cards, 
                current_game_state.rails, current_game_state.destinations, game_info, opponent_info)
        self.player_game_states[self.turn] = active_game_state
        
        return active_game_state

    def get_all_player_connections(self) -> Set[Connection]:
        """
        Gets all acquired connections.
            Returns:
                A set of connections that have been acquired by any player.
        """
        acquired_connections = set()
        for player_game_state in self.player_game_states:
            for connections in player_game_state.connections:
                acquired_connections.add(connections)
        return acquired_connections

    def verify_legal_connection_for_player(self, connection: Connection, player_game_state: PlayerGameState) -> bool:
        """
        Verifies if a given connection can be legally acquired by a given player
        according the Trains game rules.
            Parameters:
                connection (Connection): Connection that is being acquired
                player_game_state (PlayerGameState): The player game state of the player
                                                     acquiring the connection
            Returns:
                True if the player can acquire the connection,
                False otherwise:
                - The connection is already acquired
                - The player does not have enough rails
                - The player does not have enough of the corresponding colored cards
        """
        if connection not in self.free_connections:
            return False
        if player_game_state.rails < connection.length:
            return False
        if player_game_state.colored_cards[connection.color] < connection.length:
            return False
        return True

    def verify_legal_connection(self, connection: Connection) -> bool:
        """
        Verifies if a given connection can be legally acquired by the currently active player
        according the Trains game rules.
            Parameters:
                connection (Connection): Connection that is being acquired
            Returns:
                True if the currently active player can acquire the connection,
                False otherwise:
                - The connection is already acquired
                - The player does not have enough rails
                - The player does not have enough of the corresponding colored cards
        """
        player_resources = self.player_game_states[self.turn]
        return self.verify_legal_connection_for_player(connection, player_resources)

    def get_all_acquirable_connections(self, player_game_state: PlayerGameState) -> Set[Connection]:
        """
        Determines all connections that can be acquired by a given player.
            Parameters:
                player_game_state (PlayerGameState): The player to determines acquireable connections for
            Returns:
                Set of acquireable connections
        """
        acquirable_connections = set()
        for connection in self.free_connections:
            if self.verify_legal_connection_for_player(connection, player_game_state):
                acquirable_connections.add(connection)
        return acquirable_connections

    def get_all_unacquired_connections(self) -> Set[Connection]:
        """
        Determines all connections that have not been acquired by a player.
            Returns:
                Set of unacquired connections
        """
        all_connections = self.map.get_all_connections()
        unacquired_connections = all_connections - self.get_all_player_connections()
        return unacquired_connections

    def get_cards_from_deck(self, number_of_cards) -> List[Color]:
        """
        Gets the specified number of cards from the deck,
        or as many as possible ([] if none).

        SIDE EFFECT: Changes the number of cards in the deck by removing an amount greater than
        or equal to two cards.
        """
        cards = []
        for _ in range(number_of_cards):
            if len(self.colored_card_deck) > 0:
                cards.append(self.colored_card_deck.pop())
        return cards

    def give_cards_to_active_player(self, cards_to_give: List[Color]) -> None:
        """
        Given a list of colored cards to be given to the active player, adds these cards
        to the player's hand.

        SIDE EFFECT: Mutates the colored_card field (dict[Color, int]) by adding 1 to each value at the key of
        the corresponding color of each card.
        """
        active_player_game_state = self.player_game_states[self.turn]
        for card in cards_to_give:
            if card in active_player_game_state.colored_cards.keys():
                active_player_game_state.colored_cards[card] += 1
            else:
                active_player_game_state.colored_cards[card] = 1
    
    def add_connection_to_active_player(self, connection: Connection) -> None:
        """
        Given a connection that the active player if legally acquiring, add it to their player 
        game state's set of connections.
        
        SIDE EFFECT: Mutates the connections, rails, and colored_card (specifically removes given 
        value of rails from that color key in the dictionary) fields of the active player's PlayerGameState.
        """
        self.player_game_states[self.turn].connections.add(connection)
        self.player_game_states[self.turn].rails -= connection.length
        self.player_game_states[self.turn].colored_cards[connection.color] -= connection.length

    def give_player_destinations(self, player_index: int, destinations: Set[Destination]) -> None:
        """
        Given the index of a player (corresponding to their PlayerGameState in this object) and 
        a set of destinations, give the player those destinations.

        SIDE EFFECT: Mutates the PlayerGameState by adding each destination in the given set of destinations
        to its saved destinations.
        """
        game_state = self.player_game_states[player_index]
        for destination in destinations:
            game_state.destinations.add(destination)
    
    def clear_player_connections(self, player_index: int) -> None:
        """
        Given the index of a player (used when player is banned), free all of their acquired
        connections by setting its game state's connections to an empty set.

        SIDE EFFECT: Mutates the connections field of the PlayerGameState corresponding to the given index.
        """
        self.player_game_states[player_index].connections = set()

    def on_last_turn(self) -> bool:
        """
        Determines if any player has less than 3 rails and a game
        is entering its last round.
            Returns:
                True if end_game detected, else False
        """
        for game_state in self.player_game_states:
            if game_state.rails < 3:
                return True
        return False

    def no_change_after_cycle(self) -> bool:
        """
        Determines if no changes have been made after every player's turn
        INTENDED CALLER: Referee of the game
        """
        return self.no_change
