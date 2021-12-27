from dataclasses import dataclass
import sys
import json
sys.path.append('../../')
from Trains.Common.map import Color


@dataclass
class PlayerGameState:
    """
    Represents a player game state through the resources available to a player, their
    acquired connections, and destinations.  A player's resources includes their colored
    cards, the number of rails they have, game info (number of cards in the deck, unacquired connections),
    and opponent info (other player's connections).
        Parameters:
            connections (set): Set of a player's connections
            colored_cards (dict): Dictionary of a player's colored cards
            rails (int): The number of rail segments a player has
            destinations (set): A set of a player's 2 destinations
            game_info (dict): A dictionary that tracks unacquired connections, the number of cards left 
                              in the deck, and whether or not it is the final turn
            opponent_info (list): A list of dictionaries that tracks opponent's connections and
                                  the number of cards in their hand.
    """
    connections: set
    colored_cards: dict
    rails: int
    destinations: set
    game_info: dict
    opponent_info: list

    def __post_init__(self):
        """
        Checks the validity of the PlayerResources dataclass fields
            Throws:
                ValueError:
                    - Connections must be a set
                    - Colored cards must be a dictionary
                    - Player game state must have 0 or more of a certain colored card
                    - Player game state must have 0 or more rails
                    - Destination must be a set
                    - game info and opponent info must be a dictionary
        """
        if type(self.connections) != set:
            raise ValueError("Connections must be a set")
        if type(self.colored_cards) != dict:
            raise ValueError("Colored cards must be a dictionary")
        else:
            for num in self.colored_cards.values():
                if num < 0:
                    raise ValueError("The number of cards for a color cannot be negative")
        if self.rails < 0:
            raise ValueError("Player must have 0 or more rails")
        if type(self.destinations) != set:
            raise ValueError("Destinations must be a set")
        if type(self.game_info) != dict:
            raise ValueError("Game info field must be a dictionary")
        if type(self.opponent_info) != list:
            raise ValueError("Opponent info field must be a list")
        else:
            for opponent_entry in self.opponent_info:
                if type(opponent_entry) != dict:
                    raise TypeError("Entries in the opponent info list must be a dictionary.") 

    def get_number_of_colored_cards(self):
        """
        Gets the total number of colored cards the player game state has.
            Returns:
                total (int): The total number of colored cards in the player game state
        """
        total = 0
        for num in self.colored_cards.values():
            total += num
        return total

    def get_as_json(self):
        """
        Returns the JSON string of PlayerResources dataclass
        Will put alphanumerically first connection/destination first in JSON
        """
        player_game_state_json = {}
        player_game_state_json["this"] = self.get_this_player_as_json()
        player_game_state_json["game_info"] = self.get_game_info_as_json()
        player_game_state_json["opponent_info"] = self.get_opponent_info_as_json()

        return player_game_state_json
    
    def get_game_info_as_json(self) -> dict:
        """
        Converts this player game state's game information into a dictionary. Return this dictionary, later to be converted
        to a JSON.
            Returns: Dictionary containing the number of cards left in the deck, the availble connections on the map, and whether 
                     or not the player is on their final turn.
            game_info = dict:
                "unacquired_connections": List[Connections] # the connections available for purchase
                "cards_in_deck": int # the number of cards left in deck
                "last_turn": bool # whether or not the player is on their final turn

        """
        game_info_json = {}

        game_info_json["unacquired_connections"] = []
        for connection in self.game_info["unacquired_connections"]:
            game_info_json["unacquired_connections"].append(connection.get_as_json())
        
        game_info_json["cards_in_deck"] = self.game_info["cards_in_deck"]
        game_info_json["last_turn"] = self.game_info["last_turn"]
        return game_info_json

    def get_opponent_info_as_json(self) -> list:
        """
        Converts all opponent information into a list of dictionaries containing each opponent's acquired connections
        and number of cards in their hand. Returns this formatted data to be later converted to JSON.
            Returns: List of opponent info dictionaries.
            opponent_info = List[opponent_info_dict]:
                where opponent_info_dict = dict:
                    "connections": List[Connection] # connections owned by this opponent
                    "number_of_cards": int # number of color cards held by this player
        """
        opponent_info_json = []
        for entry in self.opponent_info:
            opponent_info_entry_json = {}
            opponent_info_entry_json["number_of_cards"] = entry["number_of_cards"]
            opponent_info_entry_json["connections"] = [connection.get_as_json() for connection in entry["connections"]]
            opponent_info_json.append(opponent_info_entry_json)
        return opponent_info_json

    def get_this_player_as_json(self) -> dict:
        """
        Converts all of the info specific to the player (i.e., cards, rails, destinations, acquired connections),
        to python data structures that can be converted to a JSON. Returns that formatted data.
            Returns:
                A dictionary containing the player's number of rails, cards (dict of color to natural), destinations, and 
                acquired connections.
        """
        this_player_json = {}

        current_destination = 1
        for destination in self.destinations:
            this_player_json[f"destination{current_destination}"] = destination.get_as_json()
            current_destination += 1

        colored_cards_dict = {}
        for color_key in self.colored_cards.keys():
            colored_cards_dict[color_key.__str__()] = self.colored_cards[color_key]
        this_player_json["cards"] = colored_cards_dict

        this_player_json["acquired"] = []
        for connection in self.connections:
            this_player_json["acquired"].append(connection.get_as_json())
        
        this_player_json["rails"] = self.rails

        return this_player_json
