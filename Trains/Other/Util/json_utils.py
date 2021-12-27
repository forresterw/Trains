import sys, math

from Trains.Other.Mocks.mock_given_map_player import MockGivenMapPlayer
from Trains.Player.moves import PlayerMove, DrawCardMove, AcquireConnectionMove

sys.path.append('../../')
from Trains.Common.player_game_state import PlayerGameState
from Trains.Common.map import Color, City, Connection, Map, Destination
from Trains.Player.dynamic_player import DynamicPlayer

COLORS = {
    "red": Color.RED,
    "blue": Color.BLUE,
    "green": Color.GREEN,
    "white": Color.WHITE
}

STRATEGY_FILE_PATH = "../Trains/Player/"

class MalformedJson(Exception):
    """The Json that was passed in is not well formed and does not follow the specified format."""
    pass


def seperate_json_inputs(input: str):
    """
    Separates JSON values from given input source.
        Parameters:
            input (str): Series of JSON values
        Returns:
            List of JSON values
    """
    open_objects = 0
    open_lists = 0
    starting_place = 0
    in_string = False
    outputs = []

    for i in range(len(input)):
        if input[i] == "\"":
            in_string = not in_string
        elif input[i] == "{" and not in_string:
            open_objects += 1
        elif input[i] == "}" and not in_string:
            open_objects -= 1
        elif input[i] == "[" and not in_string:
            open_lists += 1
        elif input[i] == "]" and not in_string:
            open_lists -= 1
        elif input[i] == " " and not in_string and open_lists == 0 and open_objects == 0:
            outputs.append(input[starting_place:i])
            starting_place = i + 1

    outputs.append(input[starting_place:])
    return outputs

def convert_json_map_to_data_map(json_map: dict):
    """
    Parses the given map into existing internal data definitions.
        Parameters:
            json_map (dict): Map from given input
        Returns:
            Internal Map data definition of given_map
    """
    # if set(json_map.keys()) is not {"width", "height", "cities", "connections"}:
    #     raise MalformedJson("Map json is not properly formatted.")

    width = json_map["width"]
    height = json_map["height"]

    cities = set()
    cities_dict = {}
    for city in json_map["cities"]:
        city_struct = City(city[0], city[1][0], city[1][1])
        cities.add(city_struct)
        cities_dict[city[0]] = city_struct

    connections = set()
    for connection, target in json_map["connections"].items():
        city1 = cities_dict[connection]
        for city in target.keys():
            city2 = cities_dict[city]
            for color in target[city].keys():
                connections.add(Connection(frozenset({city1, city2}), COLORS[color], target[city][color]))

    return Map(cities, connections, height, width)

def convert_json_city_to_data(city_name: str, game_map: Map):
    """
    Uses a given city name and a given map to create a City object representation of the city name and it's corresponding information (position).
        Parameters:
            city_name (str): The name of the city being converted to a City object
            game_map (Map): The Map that the city_name is from
        Returns:
            The City object representation of the given city name
        Throws:
            ValueError when the city name is no associated with the given map
    """

    for city in game_map.get_all_cities():
        if city.name == city_name:
            return city
    raise ValueError("City not on map")

def convert_json_destinations_to_data(json_player_state: dict, game_map: Map):
    """
    Uses a given dictionary representation of a player state and the corresponding Map to create an internal data representation of a player's destinations
        Parameters:
            json_player_state (dict): The dictionary representation of a player game state being using to create a set of the player's destinations
            game_map (Map): The Map that the given player game state is associated with
        Returns:
            Set of Destinations from the given player game state
    """
    possible_destinations = game_map.get_feasible_destinations(game_map.connections)
    player_destinations = set()
    dest1_names = set(json_player_state["destination1"])
    dest2_names = set(json_player_state["destination2"])
    for destination in possible_destinations:
        destination_name_set = {city.name for city in destination}
        if dest1_names == destination_name_set or dest2_names == destination_name_set:
            player_destinations.add(destination)
    return player_destinations

def convert_json_connection_to_data(json_connection, game_map: Map):
    """
    Creates an internal data representation of a Connection using a given representation of a connection and the Map it is associated with
        Parameters:
            json_connection (list): The list representation of a connection [Name, Name, Color, Length]
            game_map (Map): The Map that the given connection is associated with
        Returns:
            Connection representation of the given json_connection
    """
    city1, city2, color, length = json_connection
    city1 = convert_json_city_to_data(city1, game_map)
    city2 = convert_json_city_to_data(city2, game_map)
    return Connection(frozenset({city1, city2}), COLORS[color], length)

def convert_data_connection_to_acquired(data_connection):
    city1, city2 = list(data_connection.cities)

    if city1.name < city2.name:
        name1 = city1.name
        name2 = city2.name
    else:
        name1 = city2.name
        name2 = city1.name

    color = str(data_connection.color)
    length = data_connection.length

    return f"[\"{name1}\", \"{name2}\", \"{color}\", {length}]"

def convert_json_player_state_to_data(json_player_state: dict, game_map: Map):
    """
    Uses a given dictionary representation of a player state and the corresponding Map to create 
    an internal data representation of a player game state (PlayerGameState)
        Parameters:
            json_player_state (dict): The dictionary representation of a player game state being using to create a PlayerGameState object
            game_map (Map): The Map that the given player game state is associated with
        Returns:
            PlayerGameState representation of the given json_player_state
    """
    destinations = convert_json_destinations_to_data(json_player_state["this"], game_map)
    rails = json_player_state["this"]["rails"]
    colored_cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
    for key, value in json_player_state["this"]["cards"].items():
        colored_cards[COLORS[key]] = value
    connections = {convert_json_connection_to_data(json_connection, game_map) for json_connection in json_player_state["this"]["acquired"]}
    available_connections = game_map.get_all_connections() - connections
    for opponent in json_player_state["acquired"]:
        for sub_connection in opponent:
            connection = convert_json_connection_to_data(sub_connection, game_map)
            available_connections = available_connections - set({connection})
    game_info = {"unacquired_connections": available_connections}
    opponent_info = []
    return PlayerGameState(connections, colored_cards, rails, destinations, game_info, opponent_info)

def convert_from_json_to_player_game_state(json_player_game_state: dict):
    destinations = set()
    destinations.add(convert_from_json_to_destination(json_player_game_state["this"]["destination1"]))
    destinations.add(convert_from_json_to_destination(json_player_game_state["this"]["destination2"]))

    rails = json_player_game_state["this"]["rails"]

    colored_cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
    for key, value in json_player_game_state["this"]["cards"].items():
        colored_cards[COLORS[key]] = value

    connections = set()
    for conn in json_player_game_state["this"]["acquired"]:
        connections.add(convert_from_json_to_connection(conn))

    game_info = dict()
    available_connections = []
    for conn in json_player_game_state["game_info"]["unacquired_connections"]:
        available_connections.append(convert_from_json_to_connection(conn))
    game_info["unacquired_connections"] = available_connections
    game_info["cards_in_deck"] = json_player_game_state["game_info"]["cards_in_deck"]
    game_info["last_turn"] = json_player_game_state["game_info"]["last_turn"]

    opponent_info = []
    for opponent in json_player_game_state["opponent_info"]:
        individual_opponent_info = dict()
        individual_opponent_connections = set()
        for conn in opponent["connections"]:
            individual_opponent_connections.add(convert_from_json_to_connection(conn))
        individual_opponent_info["number_of_cards"] = opponent["number_of_cards"]
    return PlayerGameState(connections, colored_cards, rails, destinations, game_info, opponent_info)

def convert_json_player_game_state_xlegal(json_player_state: dict, game_map: Map):
    """
    Uses a given dictionary representation of a player state and the corresponding Map to create an internal data representation of a 
    player game state (PlayerGameState).  Also uses the list of acquired connections in the given json_player_state to create internal
    data representations of Connections for those acquired connections. 
        Parameters:
            json_player_state (dict): The dictionary representation of a player game state
            game_map (Map): The Map that the given player game state is associated with
        Returns:
            PlayerGameState representation of the given json_player_state, set of Connections representing the acquired connections according to the given json_player_state
    """
    player_resources = convert_json_player_state_to_data(json_player_state, game_map)
    other_connections = set()
    for json_connection in json_player_state["acquired"]:
        for sub_connection in json_connection:
            connection = convert_json_connection_to_data(sub_connection, game_map)
            other_connections.add(connection)
    return player_resources, other_connections

def convert_json_players_to_player_list(json_player_instances: list):
    """
    Given a list of JSON representation Player instances, convert that list (contains player and strategy names)
    to a list of Players to hand to a Referee.
        Parameters:
            json_player_instances (list): A list of length-two arrays containing a Player name and Strategy name, in that order.
        Returns:
            A list of Players in the order of the given instance list to hand to a Referee.
    """
    players = []
    player_name_ind, player_strategy_ind = 0, 1
    for i in range(len(json_player_instances)):
        player_instance = json_player_instances[i]
        name = player_instance[player_name_ind]
        strategy_name = player_instance[player_strategy_ind]
        age = len(json_player_instances) - i
        file_path = strategy_name_to_strategy_path(strategy_name)
        player = DynamicPlayer(name, age, file_path)
        players.append(player)
    return players

def convert_json_players_to_player_given_map_list(json_player_instances: list, map: Map):
    """
    Given a list of JSON representation Player instances, convert that list (contains player and strategy names)
    to a list of Players to hand to a Referee.
        Parameters:
            json_player_instances (list): A list of length-two arrays containing a Player name and Strategy name, in that order.
        Returns:
            A list of Players in the order of the given instance list to hand to a Referee.
    """
    players = []
    for i in range(len(json_player_instances)):
        player_instance = json_player_instances[i]
        file_path = STRATEGY_FILE_PATH + player_instance[1].lower().replace('-', '_') + '.py' # + '_strategy.py'
        player = MockGivenMapPlayer(player_instance[0], i, file_path, map)
        players.append(player)
    return players

def convert_from_json_to_city(json_city: list) -> City:
    """
    Converts a json array to a City object.
    """
    name_index = 0
    coord_index = 1
    x_index = 0
    y_index = 1

    return City(json_city[name_index], json_city[coord_index][x_index], json_city[coord_index][y_index])

def convert_from_json_to_destination(json_destination: list) -> Destination:
    """Converts a json array to a Destination object"""
    destination = set()
    for city in json_destination:
        destination.add(convert_from_json_to_city(city))
    return Destination(destination)

def convert_from_json_to_card_plus(json_card_plus: list) -> list:
    """Converts a json array of color cards to a python list of Color objects
        Example: from: ["red", "blue", "green"]
                 to: [COLOR.RED, COLOR.BLUE, COLOR.GREEN]
    """
    card_plus = []
    for card in json_card_plus:
        card_plus.append(COLORS[card])
    return card_plus

def convert_from_card_plus_to_json(card_plus) -> list:
    """Converts a python list of Color objects to a json array of color cards
            Example: from: [COLOR.RED, COLOR.BLUE, COLOR.GREEN]
                     to: ["red", "blue", "green"]
        """
    json_card_plus = []
    for card in card_plus:
        json_card_plus.append(card.__str__())
    return json_card_plus

def convert_card_star_to_json(card_star) -> dict:
    """Convert a dictionary card* to a json object
        Example: from: card_star = {
                                    COLOR.RED: 4,
                                    COLOR.GREEN: 0,
                                    COLOR.BLUE: 5,
                                    COLOR.WHITE: 3
                                    }
                 to: card_star = {
                                        "red": 4,
                                        "green": 0,
                                        "blue": 5,
                                        "white": 3
                                    }

        """
    json_card_star = dict()
    for color_name in COLORS.keys():
        json_card_star[color_name] = card_star[COLORS[color_name]]
    return json_card_star

def convert_from_json_to_card_star(json_card_star) -> dict:
    """Convert a json object to a dictionary card* to
        Example: from: card_star = {
                                    "red": 4,
                                    "green": 0,
                                    "blue": 5,
                                    "white": 3
                                    }
                 to: card_star = {
                                    COLOR.RED: 4,
                                    COLOR.GREEN: 0,
                                    COLOR.BLUE: 5,
                                    COLOR.WHITE: 3
                                    }

        """
    card_star = dict()
    for color_name in COLORS.keys():
        card_star[COLORS[color_name]] = json_card_star[color_name]
    return card_star

def convert_from_json_to_connection(json_connection: list) -> Connection:
    """Converts a json array representing a Connection to a Connection data object.
        Example: from:  [City, City, "blue", 4]
                 to: Connection(frozenset(City, City), COLOR.BLUE, 4)

        """
    first_city_index = 0
    second_city_index = 1
    color_index = 2
    length_index = 3

    city_set = set()
    city_set.add(convert_from_json_to_city(json_connection[first_city_index]))
    city_set.add(convert_from_json_to_city(json_connection[second_city_index]))

    return Connection(frozenset(city_set), COLORS[json_connection[color_index]], json_connection[length_index])

def strategy_name_to_strategy_path(strategy_name: str) -> str:
    """
    Given the name of a strategy class (e.g., Buy-Now, Hold-10, etc.), convert the name
    into an actual path to an existing strategy path file in the Player directory in Trains.
        Returns:
            A string with the path to the specified strategy class.
    """
    file_path = STRATEGY_FILE_PATH + strategy_name.lower().replace('-', '_') + '.py' # + '_strategy.py'
    return file_path

def convert_from_json_to_playermove(action):
    if type(action) == str and action == "more cards":
        return DrawCardMove()
    else:
        connection = convert_from_json_to_connection(action)
        return AcquireConnectionMove(connection)