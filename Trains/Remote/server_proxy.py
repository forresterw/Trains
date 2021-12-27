import asyncio
import json, sys
from json.decoder import JSONDecoder
from typing import Any

sys.path.append('../../')

from Trains.Remote.networking_constants import MAX_MESSAGE_SIZE
from Trains.Common.map import Map
from Trains.Other.Mocks.mock_given_map_player import MockGivenMapPlayer
from Trains.Other.Util.json_utils import convert_json_map_to_data_map, convert_json_player_state_to_data, \
    convert_from_json_to_player_game_state, convert_from_json_to_card_plus, convert_from_json_to_destination, \
    convert_from_json_to_card_star, strategy_name_to_strategy_path
from Trains.Player.dynamic_player import DynamicPlayer
from Trains.Remote.messages.valdiate_server_message import validate_server_message

METHOD_CALL_NAME_INDEX = 0
METHOD_CALL_ARGS_INDEX = 1


class ServerProxy:
    """
    Objects of this class are used to allow clients to receive game messages from 
    a Trains server asking for output, as well as send messages to the server containing
    this output.

    Messages from the server will be method calls of the form (as JSON):
        [<method name: str>, [<method arguments: any>]]
    
    The ServerProxy will contain an instance of a player with a strategy and a 
    name. The age will be set to 0 since the **actual** server (and admin components) 
    is the only component that cares about its age (defined based on when they joined; i.e,
    "how old it is"). 
    """
    TIMEOUT = 20.0

    # TODO: Maybe pass in a player instead of instantiating them in the class?
    def __init__(self, hostname: str, port: int, player_name: str, strategy_name: str, map: Map) -> None:
        """
        Initializes an instance of a ServerProxy with a given hostname and port to connect
        to an actual server with, as well as the name and strategy of a player.
            Parameters:
                hostname (str): The host name of the server the proxy is connecting to.
                port (int): The port number the proxy is connecting to.
                player_name(str): Name of the player.
                strategy_name(str): Name of the player's strategy.
        """
        self.hostname = hostname
        self.port = port
        self.strategy_name = strategy_name
        # TODO: Write method to get the file path of a strategy from its name.
        strategy_path = strategy_name_to_strategy_path(strategy_name)
        self.player = MockGivenMapPlayer(player_name, 0, strategy_path, map)
        self.game_active, self.did_win = False, False
        self.reader, self.writer = None, None

    def play_game(self) -> bool:
        """
        Joins a game of trains through a TCP connection to a Trains.com server.

        Starts by signing up the player with the server. After sign up, the ServerProxy will
        lookout for method call messages. If one is received, it will compute the result and
        send that back to the server. 

        The player -- assuming it behaves -- will eventually receive a method call through
        win and end to determine if it won the tournnament or not. If it wins, the method will
        return True.

            Returns: True if the client/player wins the tournament, else False. 
        """
        self.game_active = True
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        event_loop.run_until_complete(self.sign_up_for_game())

        try:
            result = event_loop.run_until_complete(self.execute_gameplay())
        except GamePlayException:
            result = False
        
        self.writer.close()
        event_loop.close()
        
        return result
    
    async def sign_up_for_game(self) -> None:
        """
        Connects to a Trains.com server to sign up for a tournament. Opens a connection
        with the server and sends the server our player information (name).

        SIDE EFFECT: Sets the self.reader and self.writer fields with StreamReader
        and StreamWriter objects that are used to communicate over TCP.
        """
        self.reader, self.writer = await asyncio.open_connection(self.hostname, self.port)
        sign_up_info = [self.player.name]
        sign_up_info_msg = json.dumps(sign_up_info)
        self.writer.write(sign_up_info_msg.encode())
        await self.writer.drain()

    # TODO: Close connection if nothing back from the Server.
    async def execute_gameplay(self) -> bool:
        """
        Executes game play methods as they come in. These are the methods described by the previous
        Remote Interactions diagram.

        Once win(False) or end(True|False) is called on the player, return the boolean provided
        as the game result.

            Returns: True if the player wins the tournament, else False.
        """
        while self.game_active:
            server_data = await self.read_method_calls()
            method_calls = self.process_method_calls_from_server(server_data)
            for method_call_json in method_calls:
                await self.execute_method_call(method_call_json)
        self.writer.close()
        return self.did_win

    async def read_method_calls(self) -> str:  # or return list if loads
        """
        Waits until a nonempty result is returned from Reader.read().
        This method allows us to use wait for on a method that will timeout.
        Returns the non-empty results of Reader.read()
        """
        try:
            method_call_message_data = await asyncio.wait_for(self.reader.read(MAX_MESSAGE_SIZE), self.TIMEOUT)

        except asyncio.TimeoutError:
            raise GamePlayException("Timeout reading from server")
        method_call_json = method_call_message_data.decode()
        if method_call_json == "":
            raise GamePlayException("server has closed our writer.")
        return method_call_json

    def process_method_calls_from_server(self, server_data: str) -> list:
        """
            Split one json string into a list of pythonic jsons using raw_decode.

            When Reading from server, its possible to get two method calls at once:
            For Example: "["win", [True]] ["end", [True]]"
                can be read at once. This method will split this string into two method calls
        """
        method_call_decoder = JSONDecoder()
        data_length = len(server_data)

        server_method_calls = []

        current_index = 0
        while current_index != data_length:
            method_call, ending_ind = method_call_decoder.raw_decode(server_data[current_index:])
            server_method_calls.append(method_call)
            current_index += ending_ind
        
        return server_method_calls

    async def execute_method_call(self, method_call_json: list) -> None:
        """
            Takes in a method call formatted as a list of name and arguments.
            Calls the method call with the given name and arguments and writes the output to server

            SIDE EFFECTS:
                self.game_active is set to False when win(False) or end(True|False) is called

            Example: ["play", [PlayerGameState]] -> self.writer.write(self.player.play(PlayerGameState))
        """
        method_call_name = method_call_json[METHOD_CALL_NAME_INDEX]
        if not validate_server_message(method_call_json):
            raise GamePlayException("Client received an invalid JSON.")
        output = self.call_player_method_from_json(method_call_json)

        if output is not None:
            if method_call_name == 'pick': # Destination_Plus is not a data object with .get_as_json()
                output_pythonic_json = [destination.get_as_json() for destination in output]
            else:
                output_pythonic_json = output.get_as_json()
            output_json = json.dumps(output_pythonic_json)
            self.writer.write(output_json.encode())
            await self.writer.drain()

        if method_call_name == "end":
            result_index = 0
            result = method_call_json[METHOD_CALL_ARGS_INDEX][result_index]
            self.game_active = False
            self.did_win = result

        if method_call_name == "win":
            result_index = 0
            result = method_call_json[METHOD_CALL_ARGS_INDEX][result_index]
            if not result:
                self.game_active, self.did_win = False, False

    def call_player_method_from_json(self, player_method_json: list) -> Any:
        """
        Given a json with information about which player method to call and what arguments
        (see ProxyServer docstring for more information), call the proper player method with
        the given arguments.

        Player method data definition is the same as described in the docstring for this class.

        Example: ["play", [PlayerGameState]] -> self.player.play(PlayerGameState)
        """
        method_name = player_method_json[METHOD_CALL_NAME_INDEX]
        method_args_json = player_method_json[METHOD_CALL_ARGS_INDEX]
        method_args = self.convert_method_args_to_objects(method_name, method_args_json)
        player_api_method = getattr(self.player, method_name)
        return player_api_method(*method_args)

    def convert_method_args_to_objects(self, method_name: str, method_args_json: list) -> list:
        """
        Given the name of a method to be called on the player and a JSON (i.e., pythonic JSON)
        representation of the arguments, convert the arguments from JSON to their respective
        data structures defined by the various Trains.com APIs and return them in a list of
        the same order.
            Parameters:
                method_name (str): Name of the method whose arguments are being converted.
                method_args_json (List[Object]): Method arguments to be converted.
            Returns:
                List of data structures corresponding to the JSON representation of the arguments.
        """
        num_args = len(method_args_json)
        arg_range_tuple = tuple(range(num_args))

        # TODO: Add convert_card_plus function.
        if method_name == "start":
            args = []
        elif method_name == "setup":
            map_index, rails_index, card_star_index = arg_range_tuple
            game_map = convert_json_map_to_data_map(method_args_json[map_index])
            rails = method_args_json[rails_index]
            cards = convert_from_json_to_card_star(method_args_json[card_star_index])
            args = [game_map, rails, cards]
        elif method_name == "pick":
            destinations_ind = 0
            destinations = method_args_json[destinations_ind]
            set_of_destination_objects = set()
            for dest in destinations:
                set_of_destination_objects.add(convert_from_json_to_destination(dest))
            args = [set_of_destination_objects]
        # Methods play and update_game_state have the same argument.
        elif method_name == "play" or method_name == "update_game_state":
            # TODO: Convert current connection "acquired" JSON format to use all city info
            game_state_index = 0
            game_state_json = method_args_json[game_state_index]
            game_state = convert_from_json_to_player_game_state(game_state_json)
            args = [game_state]
        elif method_name == "more":
            card_plus_index = 0
            card_plus = method_args_json[card_plus_index]
            cards = convert_from_json_to_card_plus(card_plus)
            args = [cards]
        else:
            bool_index = 0
            bool_arg = method_args_json[bool_index]
            args = [bool_arg]
        
        return args
        





class GamePlayException(Exception):
    """
    Exception to be raised whenever an error occurs when the ServerProxy throws
    an error while attempting game play with the client/server.
    """
    pass