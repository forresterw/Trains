import sys
from enum import Enum
sys.path.append('../../')
from Trains.Common.map import Connection


class MoveType(Enum):
    """
    A enumeration of the possible moves in Trains.  Also considers a representation for when 
    there is no possible move available.
    """
    NO_MOVE = 0
    DRAW_CARDS = 1
    ACQUIRE_CONNECTION = 2


class PlayerMove:
    """
    Parent class that represents a player move.  Defaults move type to 'None' since
    a player's action on their turn will always dictate the move type.
    """
    def __init__(self):
        self.move_type = None


class DrawCardMove(PlayerMove):
    """
    Child class of PlayerMove that represents the player action of drawing 2 colored cards.
    """
    def __init__(self):
        """
        Constructor that sets the move type to the corresponding MoveType enum value, DRAW_CARDS.
        """
        self.move_type = MoveType.DRAW_CARDS

    def __str__(self):
        """
        String representation of the DrawCardMove class
        """
        return "Draw 2 cards"
    
    def get_as_json(self):
        """
        Returns a JSON representation of a DrawCardMove.
            Returns: (string) JSON string for a player requesting more cards.
        """
        return "more cards"


class AcquireConnectionMove(PlayerMove):
    """
    Child class of PlayerMove that represents the player action of attempting to acquire a connection.
    """
    def __init__(self, connection: Connection):
        """
        Constructor that sets the move type to the corresponding MoveType enum value of ACQUIRE_CONNECTION.
            Parameters:
                connection (Connection):
        """
        if type(connection) != Connection:
            raise ValueError("AcquireConnectionMove must be given a connection")

        self.move_type = MoveType.ACQUIRE_CONNECTION
        self.connection = connection

    def __str__(self):
        """
        String representation of the AcquireConnectionMove class
        """
        return f"Attempt to acquire {self.connection}"
    
    def get_as_json(self):
        """
        Returns a JSON representation of an AcquireConnection move, which is the same as
        a connection JSON/Acquired as returned in a Connection's get_as_json.
            Returns: (string) JSON array containing city names, color, and length of connection
                     player is attempting to acquire.
        """
        return self.connection.get_as_json()



class NoAvailableMove(PlayerMove):
    """
    Child class of PlayerMove that represents a player not having any actions available.
    """
    def __init__(self):
        """
        Constructor that sets the move type to the corresponding MoveType enum value of NO_MOVE.
        """
        self.move_type = MoveType.NO_MOVE

    def __str__(self):
        """
        String representation of the NoAvailableMove class
        """
        return "No possible move"