import sys
from typing import Dict, List, Set

sys.path.append('../../')
from Trains.Common.map import Color, Connection, Destination
from Trains.Common.map import Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.moves import PlayerMove


class PlayerInterface:

    def setup(self, map: Map, rails: int, cards: Dict[Color, int]) -> None:
        """
        Sets the player up with a map, a number of rails, and a hand of cards.
            Parameters:
                - map (Map): The map of the game.
                - rails (int): The number of rails the player will start with.
                - cards (dict): The hand of cards the player starts with.
        """
        pass

    def update_player_game_state(self, updated_game_state: PlayerGameState) -> None:
        """
        Updates the player on their current game state.  Receives an updated game state from the referee to
        reflect changes made by a player's move.
            Parameters:
                updated_game_state (PlayerGameState): The updated game state for the player
        """
        pass

    def play(self, active_game_state: PlayerGameState) -> PlayerMove:
        """
        Polls the player strategy for a move.
            Parameters:
                active_game_state (PlayerGameState): The game state of this player when they've become active.
            Return:
                A PlayerMove indicating a player's intended move
        """
        pass

    def pick(self, destinations: Set[Destination]) -> Set[Destination]:
        """
        Given a set of destinations, the player picks two destinations and the three
        that were not chosen are returned.
            Parameters:
                destinations (set(Destination)): Set of five destinations to choose from.
            Return:
                A set(Destination) containing the three destinations the player did not pick.
        """
        pass

    def more(self, cards: List[Color]) -> None:
        """
        Hands this player some cards
            Parameters:
                cards (list(Color)): cards being handed to player
        """
        pass

    def boot_player_from_game(self, reason_for_boot: str) -> None:
        """
        Informs a player that they have been booted from the game with the reason why.
        Local response to boot is up to implementation, but the Referee will not continue to query the player for moves.
            Parameters:
                reason_for_boot (str): Written reason for booting the player
        """
        pass

    def boot_player_from_tournament(self, reason_for_boot: str) -> None:
        """
        Informs a player that they have been booted from the tournament with the reason why.
        The Manager will not enter the booted player into any games.
            Parameters:
                reason_for_boot (str): Written reason for booting the player
        """
        pass

    def win(self, winner: bool) -> None:
        """
        Informs player that the game is over.  Tells players whether or not they won the game.
        ONLY CALLED ONCE(PER PLAYER) AT THE END OF THE GAME
            Parameters:
                winner (bool): True if this player won the game, False otherwise
        """
        pass

    def start(self) -> Map:
        """
        Informs player that they have been entered into a tournament.  Player responds by
        returning a game map to suggest for use in a game of trains.
        ONLY CALLED ONCE(PER PLAYER) BY MANAGER AT THE START OF A TOURNAMENT
            Returns:
                The player's game map (Map) suggestion
        """
        pass

    def end(self, winner: bool) -> None:
        """
        Informs player that the tournament is over.  Tells the player whether or not they won
        the tournament.
        ONLY CALLED ONCE (PER PLAYER) BY MANAGER AT THE END OF A TOURNAMENT
            Parameters:
                winner: True if the player won the tournament, False otherwise
        """
        pass


class AbstractPlayer(PlayerInterface):
    """
    Abstract player class that contains methods relevant to all player for the setup of the game,
    gameplay during the game, and the end of the game.
    """
    NUMBER_OF_DESTINATIONS = 2

    def __init__(self, name: str, age: int):
        """
        Constructor for AbstractPlayer that takes in a player name and player age (some metric to determine turn order).
            Parameters:
                name (str): Player name
                age (int): Player age
        """
        self.name = name
        self.age = age
        # The PlayerGameState for a given player that is initialized by Referee at start of game
        self.strategy = None
        self.game_state = None
        self.map = None

    def setup(self, map: Map, rails: int, cards: Dict[Color, int]) -> None:
        """
        Sets the player up with a map, a number of rails, and a hand of cards.
            Parameters:
                - map (Map): The map of the game.
                - rails (int): The number of rails the player will start with.
                - cards (dict): The hand of cards the player starts with.
        """
        self.map = map
        self.game_state = PlayerGameState(set(), cards, rails, set(), {}, [])

    def pick(self, destinations: set) -> Set[Destination]:
        """
        Given a set of destinations, the player picks two destinations and the three
        that were not chosen are returned.
            Parameters:
                destinations (set(Destination)): Set of five destinations to choose from.
            Return:
                A set(Destination) containing the three destinations the player did not pick.
        """
        chosen_destinations = self.strategy.select_destinations(destinations, self.NUMBER_OF_DESTINATIONS)
        self.game_state.destinations = chosen_destinations
        return self._compute_destinations_to_return(destinations, chosen_destinations)

    def _compute_destinations_to_return(self, destinations_given: set, destinations_chosen: set) -> Set[Destination]:
        """
        Given the destinations obtained by the player from the referee to pick from and the destinations
        the player chose, return a set containing the destinations the player will give back to the referee.
            Parameters:
                destinations_given (set(Destination)): The set of destinations the player picked from.
                destinations_chosen (set(Destination)): The set of destinations the player chose out of the ones given to them.
            Return:
                A set(Destination) the player will return to the referee.
        """
        return destinations_given - destinations_chosen

    def update_player_game_state(self, updated_game_state: PlayerGameState) -> None:
        """
        Updates the player on their current game state.  Receives an updated game state from the referee to
        reflect changes made by a player's move.
            Parameters:
                updated_game_state(PlayerGameState): The updated game state for the player
        """
        self.game_state = updated_game_state

    # TODO: Add more method

    # TODO: deprecated method
    def can_acquire_connection(self, unacquired_connection: Connection) -> bool:
        """
        Determines whether or not a player has enough resources (rails and corresponding colored cards) to acquire a given connection.
            Parameters:
                unacquired_connection (Connection): The connection being checked to see if the player has the resources to acquire it.
            Returns:
                True if the player has the necessary resources to acquire the connection, False otherwise
        """
        return self.strategy.can_acquire_connection(self.game_state, unacquired_connection)

    def play(self, active_game_state: PlayerGameState) -> PlayerMove:
        """
        Polls the player strategy for a move.
            Parameters:
                active_game_state (PlayerGameState): The game state of this player when they've become active.
            Return:
                A PlayerMove indicating a player's intended move
        """
        self.game_state = active_game_state
        return self.strategy.get_player_move(self.game_state)

    def boot_player_from_game(self, reason_for_boot: str) -> None:
        """
        Informs a player that they have been booted from the game with the reason why.
        Local response to boot is up to implementation, but the Referee will not continue to query the player for moves.
            Parameters:
                reason_for_boot (str): Written reason for booting the player
        """
        # print("You were kicked from the game for cheating\nReason:")
        # print(reason_for_boot)
        pass

    def win(self, winner: bool) -> None:
        """
        Informs player that the game is over.  Tells players whether or not they won the game.
        ONLY CALLED ONCE(PER PLAYER) AT THE END OF THE GAME
            Parameters:
                winner (bool): True if this player won, False otherwise
        """
        if winner:
            pass
            # print("You won")
        else:
            # print("You lost")
            pass


