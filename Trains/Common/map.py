from enum import Enum
from copy import deepcopy
from dataclasses import dataclass
from collections import deque
import json


# TODO: Color values should be a string
class Color(Enum):
    """
    A enumeration of the possible connection colors in Trains
    """
    RED = 1
    BLUE = 2
    GREEN = 3
    WHITE = 4

    def __str__(self):
        COLOR_TABLE = {
            Color.BLUE: "blue",
            Color.GREEN: "green",
            Color.RED: "red",
            Color.WHITE: "white"
        }

        return COLOR_TABLE[self]

    def lexicographic_ordering(color):
        """
        Returns the lexicographic ordering of colors
        Parameters:
                color (Color): color to get ordering of
        """
        COLOR_TABLE = {
            Color.BLUE: 0,
            Color.GREEN: 1,
            Color.RED: 2,
            Color.WHITE: 3
        }

        return COLOR_TABLE[color]

    def number_of_colors():
        return len(Color)


@dataclass(frozen=True)
class City:
    """
    A city represented by its name and its relative map position
    Map positions are normalized between 0% and 100% of map size
    """
    name: str
    x: int
    y: int

    def __post_init__(self):
        """
        Checks the validity for x and y fields
            Throws:
                ValueError: x and y must each be in the range [0, 100]
        """
        if self.x < 0 or self.y < 0:
            raise ValueError("Coordinates must not be negative for a city.")

    def get_as_json(self):
        """
        Returns the JSON string of City dataclass
        """
        city_json = [self.name, [self.x, self.y]]
        return city_json

    def __lt__(self, other) -> bool:
        """determines if this city is lexicographically less than a given city"""
        return self.name < other.name

    def __eq__(self, other) -> bool:
        """determines if this city is equal to a given city"""
        return self.name == other.name and self.x == other.x and self.y == other.y


@dataclass(frozen=True)
class Connection:
    """
    Represents a connection by the cities connected, color, and length
    Cities must be 2 distinct cities
    """
    cities: set
    color: Color
    length: int

    def __post_init__(self):
        """
        Checks validity of dataclass fields
            Throws:
                ValueError: 
                    - Dataclass fields must be the correct corresponding type
                    - The cities set must contain exactly 2 cities
                    - The color must be a supported color (red, green, blue, or white)
                    - The length must be 3, 4, or 5 
        """
        if type(self.cities) != frozenset:
            raise ValueError("Cities must be a frozen set")
        elif len(self.cities) != 2:
            raise ValueError("Connections conatain exactly 2 distinct cities")
        else:
            for city in self.cities:
                if type(city) != City:
                    raise ValueError("Cities must be of type City")

        if type(self.color) != Color:
            raise ValueError("Color must be a supported color")

        if self.length not in [3, 4, 5]:
            raise ValueError("Length must be one of [3, 4, 5]")

    def __lt__(self, obj):
        """
        Special method for the 'less than' operator when comparing two Connections.
            Parameters:
                self (Connection): The first connection
                obj (Connection): The second connection
            Returns:
                -1 if the first connection (self) is less than the other connection (obj), 1 Otherwise
        """

        list_self = list(self.cities)
        if list_self[1].name < list_self[0].name:
            list_self[0], list_self[1] = list_self[1], list_self[0]
        list_obj = list(obj.cities)
        if list_obj[1].name < list_obj[0].name:
            list_obj[0], list_obj[1] = list_obj[1], list_obj[0]

        if list_self[0].name < list_obj[0].name:
            return -1
        elif list_self[0].name == list_obj[0].name and list_self[1].name < list_obj[1].name:
            return -1
        elif list_self[0].name == list_obj[0].name and list_self[1].name == list_obj[
            1].name and self.length < obj.length:
            return -1
        elif list_self[0].name == list_obj[0].name and list_self[1].name == list_obj[
            1].name and self.length == obj.length and Color.lexicographic_ordering(
                self.color) < Color.lexicographic_ordering(obj.color):
            return -1
        else:
            return 1

    def get_as_json(self):
        """
        Returns the JSON string of Connection dataclass. Matches the spec for an Acquired from the Milestone 5
        test harness spec.  https://www.ccs.neu.edu/home/matthias/4500-f21/5.html#%28tech._acquired%29
        Will put alphanumerically first city first in JSON
            Returns: JSON representation of the connection.
        """
        city_json = []
        for city in self.cities:
            city_json.append(city.get_as_json())
        city_json.sort()  # TODO sort city_json
        city_json.append(self.color.__str__())
        city_json.append(self.length)
        return city_json

    def get_as_acquired_json(self):
        """
        Returns the JSON string of Connection dataclass. Matches the spec for an Acquired from the Milestone 5
        test harness spec.  https://www.ccs.neu.edu/home/matthias/4500-f21/5.html#%28tech._acquired%29
            Will put alphanumerically first city first in JSON
                Returns: JSON representation of the connection.
        """
        acquired_json = []
        for city in self.cities:
            acquired_json.append(city.name)
        acquired_json.sort()
        acquired_json.append(self.color.__str__())
        acquired_json.append(self.length)
        return acquired_json


class Destination(frozenset):
    """
    A Destination is a set of exactly two distinct cities.  Subclasses the frozenset class.
    """

    # TODO: Is equality guaranteed or does this need to be overidden?

    def __init__(self, cities):
        """
        Checks validity of cities in a destination.
            Throws:
                ValueError: Cities must be a set of exactly 2 cities
        """
        if type(cities) == list and len(cities) == 2 and cities[0] != cities[1]:
            cities = set(cities)
        if type(cities) != frozenset and type(cities) != set:
            raise ValueError("Cities must be a set")
        if len(cities) != 2:
            raise ValueError("Destinations hold exactly 2 cities")
        else:
            for city in cities:
                if type(city) is not City:
                    raise ValueError("Destinations must contain cities")

    def __lt__(self, obj):
        """
        Special method for the 'less than' operator when comparing two Destinations.
            Parameters:
                self (Destination): The first destination
                obj (Destination): The second destination
            Returns:
                -1 if the first destination (self) is less than the other destination (obj), 1 Otherwise
        """
        list_self = list(self)
        if list_self[1].name < list_self[0].name:
            list_self[0], list_self[1] = list_self[1], list_self[0]
        list_obj = list(obj)
        if list_obj[1].name < list_obj[0].name:
            list_obj[0], list_obj[1] = list_obj[1], list_obj[0]

        if list_self[0].name < list_obj[0].name:
            return -1
        elif list_self[0].name == list_obj[0].name and list_self[1].name < list_obj[1].name:
            return -1
        else:
            return 1

    # TODO: Should carry over name and city coordinates.
    def get_as_json(self):
        """
        Returns the JSON string of Destination dataclass
        Will put alphanumerically first city first in JSON
        """
        city_json = []
        for city in self:
            city_json.append(city.get_as_json())
        city_json.sort()  # TODO sort by city_json
        return city_json


class Map:
    """
    Represents the game map for a game of trains. A master map object
    should be held by the Referee and a deep copy of the map should be
    passed to players to prevent tampering. A map also has a width and height,
    which represent its display size.
    """

    def __init__(self, cities: set, connections: set, height: int = 800, width: int = 800):
        """
        Map constructor that checks the validity of arguments before assignment.
            Throws:
                ValueError:
                    - The width and height of the canvas must each be in the range [10, 800]
                    - Cities and connections must be sets
                    - Cities used in connections must be present in the cities set
        """
        if width < 10 or width > 800 or height < 10 or height > 800:
            raise ValueError("Width and height must each be in the range [10, 800]")

        if type(connections) != set:
            raise ValueError("Connections must be a set")
        if type(cities) != set:
            raise ValueError("Cities must be a set")

        for connection in connections:
            for city in connection.cities:
                if city not in cities:
                    raise ValueError("Cities in connections must be in cities set")

        self.cities = cities
        self.connections = connections
        self.height = height
        self.width = width

    def __eq__(self, obj):
        """
        Checks equality for Map class
        """
        if type(obj) != Map:
            return False
        else:
            return self.cities == obj.cities and self.connections == obj.connections \
                   and self.width == obj.width and self.height == obj.height

    def get_copy_of_map(self):
        """
        Returns a deep copy of the map for players to construct their
        game map.
                Returns
                    map (Map): Copy of the map
        """
        return deepcopy(self)

    def get_city_names(self):
        """
        Returns the names of all the cities
                Returns
                    (set): All names of cities as a set
        """
        return {city.name for city in self.cities}

    def get_cities_from_connections(self, connections: set):
        """
        Returns all the cities in given connections as a set
                Returns
                    (set): All cities as a set
        """
        ret_cities = set()
        for connection in connections:
            for city in connection.cities:
                ret_cities.add(city)
        return ret_cities

    def get_all_cities(self):
        """
        Returns all the cities on the map as a set
                Returns
                    (set): All cities on the map as a set
        """
        return deepcopy(self.cities)

    def get_all_connections(self):
        """
        Returns all the connections on the map as a set
                Returns
                    (set): All connections on the map as a set
        """
        return deepcopy(self.connections)

    def get_feasible_destinations(self, connections: set):
        """
        Returns all feasible destinations from a subset of map connections
        A Destination is a frozenset of cities that are connected via some
        path on the map.
                Parameters:
                    connections (set(Connection)): set of connections on map
                Returns
                    (set(Destination)): All possible destinations
        """
        starting_cities = self.get_cities_from_connections(connections)
        destinations = set()
        for city in starting_cities:
            terminal_cities = self.get_all_terminal_cities_from_city(city, connections)
            for terminal_city in terminal_cities:
                destinations.add(Destination({city, terminal_city}))

        return destinations

    def get_all_terminal_cities_from_city(self, city: City, connections: set):
        """
        Finds the list of cities that can be reached from a given starting city
        within a set of connections
            Parameters:
                city (City): The starting city
                connections (set(Connection)): The connections a player owns
            Returns:
                a list of cities (list(City))
        """
        visit_q = deque()
        visit_q.append(city)
        visited = []
        all_connection_cities = [connection.cities for connection in connections]

        while len(visit_q) > 0:
            current_city = visit_q.popleft()
            visited.append(current_city)

            for connection_cities in all_connection_cities:
                if current_city in connection_cities:
                    for neighbor in connection_cities:
                        if neighbor not in visited:
                            visit_q.append(neighbor)

        visited.remove(city)
        return visited

    def get_as_json(self):
        """
        Returns the JSON string of Map dataclass
        Will put alphanumerically first city/connection first in JSON
        """
        city_json = []
        for city in self.cities:
            city_json.append(city.get_as_json())
        city_json.sort()

        map_dict = {
            "width": self.width,
            "height": self.height,
            "cities": city_json,
            "connections": self.get_map_connections_as_dict()
        }

        return map_dict

    def get_map_connections_as_dict(self):
        """
        Generates a python dictionary representing all connections between cities on the map. The format
        of this mirrors the JSON spec for a map's connections provided in the JSON Map spec at this link:
        https://www.ccs.neu.edu/home/matthias/4500-f21/3.html#%28tech._map%29
            Returns: A dictionary of connections for a map. 
        """
        map_connections = {}

        sorted_cities = list(self.cities)
        sorted_cities.sort()

        added_connections = set()

        for city in sorted_cities:
            self.add_city_connections_to_map_connections_dict(map_connections, city, added_connections)

        return map_connections

    def add_city_connections_to_map_connections_dict(self, map_connections: dict, city: City, added_connections: set):
        """
        Given a dictionary containing information about map connections, a city whose connections need to be added the the
        map connections dictionary, and a set of connections that have already been added, add all connections from that city
        to other cities on the map to the map connections dictionary.
            Parameters:
                map_connections (dict): Dictionary representation of all connections between cities.
                city (City): City that needs its connections added to map_connections.
                added_connections(set(Connections)): Set of connections that have already been added to map_connections.
        """
        for connection in self.connections:
            if city in connection.cities and connection not in added_connections:
                other_city = None
                for connection_city in connection.cities:
                    if city != connection_city:
                        other_city = connection_city

                if city.name not in map_connections.keys():
                    map_connections[city.name] = {}
                if other_city.name not in map_connections[city.name].keys():
                    map_connections[city.name][other_city.name] = {}

                map_connections[city.name][other_city.name][connection.color.__str__()] = connection.length
                added_connections.add(connection)
