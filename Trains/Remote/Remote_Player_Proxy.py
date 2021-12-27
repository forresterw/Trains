from asyncio import StreamReader, StreamWriter
import asyncio
import json, sys

sys.path.append('../../')
from Trains.Remote.networking_constants import MAX_MESSAGE_SIZE
from Trains.Common.map import Map, Destination
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Util.json_utils import convert_json_connection_to_data, convert_json_player_state_to_data, \
    convert_from_json_to_destination, convert_card_star_to_json, convert_json_map_to_data_map, \
    convert_from_json_to_connection, convert_from_json_to_playermove
from Trains.Player.moves import AcquireConnectionMove, PlayerMove, DrawCardMove
from Trains.Player.player import AbstractPlayer


class RemotePlayerProxy(AbstractPlayer):
    """RemotePlayerProxy is a Proxy for a Client/Player that implements all the player methods.
        This class communicates with a ServerProxy over a tcp connection, sending and receiving json messages.
        Each time a server calls a player method on this class, this class converts the data object to a json message,
        sends that message via tcp to a server proxy, and listens for a responds message from that server proxy. This
        class then converts the received message back to a data object and returns it to the server.
        Example Interaction:
            Server calls RemotePlayerProxy.play(PlayerGameState pgs) -> PlayerMove
            RemotePlayerProxy converts pgs to json message
            RemotePlayerProxy sends json message over tcp connection via self.tcp_communicate(message) -> message
            TCP_COMMUNICATE returns a json message, and this class converts the message to a PlayerMove
            RemotePlayerProxy returns PlayerMove
    """
    TIMEOUT = 10.0

    def __init__(self, name: str, age: int, reader: StreamReader, writer: StreamWriter):
        """
        Constructs a RemotePlayerProxy with a name, an age, a reader, and a writer.
            name: str: = the name of this player
            age: int = the age of this player
            reader: StreamReader = an asyncio.StreamReader object used to read input
            writer: StreamWriter = an asyncio.StreamWriter object used to write output
        """
        self.reader = reader
        self.writer = writer
        super().__init__(name, age)

    def tcp_communicate(self, message: list, expecting_response: bool = True) -> str:
        """
        TCP_Communicate handles tcp communications with each client. Each player method converts the data to an
        array formatted as a method call [method, [argument]]. Tcp_communicate will dump that array to a json string
        and  write that json string to the socket where a client will read it and write back the appropriate response
        as json. Tcp_communicate will return that json string.

        Input: message : A method call of the format [str, [Argument, ..]]
               expecting_response: whether or not we should wait for a response in the reader
        Output: the json string read from self.reader

        Example: tcp_communicate(["play",[PlayerState]]) -> "more cards"
        """
        event_loop = asyncio.get_event_loop()
        message = json.dumps(message)
        message_data = message.encode()
        self.writer.write(message_data)
        event_loop.run_until_complete(self.writer.drain())
        player_response = ""
        if expecting_response:
            player_response_data = \
                event_loop.run_until_complete(asyncio.wait_for(self.reader.read(MAX_MESSAGE_SIZE), self.TIMEOUT))
            player_response = player_response_data.decode()
        return player_response

    def start(self) -> Map:
        """Notify the player the game has started, and return a suggested map."""
        start_json_argument = []
        start_json_function_call = ["start", start_json_argument]
        output_start_json = self.tcp_communicate(start_json_function_call)
        output_start = json.loads(output_start_json)
        suggested_map = convert_json_map_to_data_map(output_start)
        return suggested_map

    def setup(self, map: Map, rails: int, cards: dict) -> None:
        """Set up the player with a map, number of rails, and hand of cards"""
        setup_json_argument = [map.get_as_json(), rails, convert_card_star_to_json(cards)]
        setup_json_function_call = ["setup", setup_json_argument]
        self.tcp_communicate(setup_json_function_call, False)

    def pick(self, destinations: set) -> set:
        """pick two destinations from a set of five. Return the three unwanted destinations"""
        pick_json_argument = \
            [[destination.get_as_json() for destination in destinations]]
        pick_json_function_call = ["pick", pick_json_argument]
        pick_json_response = self.tcp_communicate(pick_json_function_call)
        pick_pythonic_json = json.loads(pick_json_response)
        output_destinations = set()
        for dest in pick_pythonic_json:
            output_destinations.add(convert_from_json_to_destination(dest))
        return output_destinations

    def play(self, active_game_state: PlayerGameState) -> PlayerMove:
        """Play a turn. Given a playergamestate, decide to request more cards or a new connection"""
        play_json_argument = [active_game_state.get_as_json()]
        play_json_function_call = ["play", play_json_argument]
        play_json_response = self.tcp_communicate(play_json_function_call)
        response_loaded_from_json = json.loads(play_json_response)
        return convert_from_json_to_playermove(response_loaded_from_json)

    def more(self, cards: list) -> None:
        # TODO this method, maybe convert card plus
        return super().more(cards)

    def boot_player_from_game(self, reason_for_boot: str) -> None:
        self.writer.close()

    def update_player_game_state(self, updated_game_state: PlayerGameState) -> None:
        """Depreceated Method.
            Update the player after every single turn with an updated playergamestate"""
        updated_game_state_arg = [updated_game_state.get_as_json()]
        updated_player_game_state_call = \
            ["update_player_game_state", updated_game_state_arg]
        self.tcp_communicate(updated_player_game_state_call, False)

    def win(self, winner: bool) -> None:
        """Notify the player whether or not they won the game"""
        win_method_call = ["win", [winner]]
        self.tcp_communicate(win_method_call, False)
        if not winner:
            self.writer.close()

    def boot_player_from_tournament(self, reason_for_boot: str) -> None:
        self.writer.close()

    def end(self, winner: bool) -> None:
        """Notify the player that the tournament is over. This will close off the writer."""
        end_method_call = ["end", [winner]]
        self.tcp_communicate(end_method_call, False)
        self.writer.close()
