from asyncio import events
from collections import deque
import json, time, sys
from threading import Thread
from typing import Deque, List
sys.path.append('../../')
from Trains.Remote.networking_constants import MAX_MESSAGE_SIZE
from Trains.Remote.Remote_Player_Proxy import RemotePlayerProxy
from Trains.Admin.manager import Manager
from Trains.Admin.referee import NotEnoughDestinations
from Trains.Common.map import Color
from Trains.Other.Types.trains_types import TournmentResult

# ayncio imports
import asyncio
from asyncio.streams import StreamReader, StreamWriter

MIN_NUMBER_OF_PLAYERS_FOR_GAME = 2
NO_RESULT = [[], []]


# NOTE: In the docstrings, client and player will be used interchangeably as they are, for 
# all intents and purposes, the same thing.

class Server():
    """
    Objects of this class represent a server capable of connecting to clients (players) in order to carry out a game of trains.
    When a client connects, we should create an instance of a Remote Proxy Player for them and add them to the list of 
    players who will be playing in a tournament.    
    """
    PLAYER_NAME_INDEX = 0
    PLAYER_STRATEGY_INDEX = 1
    CLIENT_TIMEOUT = 10

    def __init__(self, hostname: str, port: int, min_players_accepted: int, max_players_accepted: int, \
        waiting_time: int, deck: Deque(Color) = None) -> None:
        """
        Constructs an instance of a server given a host and a port that it should run on/allow clients to 
        connect on. The server is also given a deck of cards such that it can pass this to the Manager for
        running games.
        """
        self.players = []
        self.hostname = hostname
        self.port = port
        self.waiting_time = waiting_time
        self.max_players_accepted = max_players_accepted
        self.min_players_accepted = min_players_accepted
        self.first_wait_phase = True
        self.sign_up_handles = []
        self.deck = deck
        self.active_server = None

    # TODO: Define type TournamentResult
    def run_server(self) -> list:
        """
        Starts the server for running a game of Trains. The server will open itself up to connections on 
        its hostname/port field.        
        """
        event_loop = asyncio.get_event_loop()
        
        # Create Server
        self.active_server = self.create_asyncio_server()

        # Sign Up Phase
        self.sign_up_players()

        # Run Tournament/Return Result
        result = self.get_tournament_result()
        self.active_server.close()
        event_loop.run_until_complete(self.active_server.wait_closed())
        event_loop.close()

        return result

    # Server Creation

    def create_asyncio_server(self) -> asyncio.AbstractServer:
        """
        Using asyncio's event loop and start_server coroutine, creates an asyncio.Server object
        and returns that object.
            Returns:
                asyncio.Server to be used for connecting clients/players to the game.
        """
        event_loop = asyncio.get_event_loop()
        server_coro = asyncio.start_server(self.on_client_connection, self.hostname, self.port, loop=event_loop)
        return event_loop.run_until_complete(server_coro)

    async def on_client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        This method is called whenever a client connects to the server.

        Given the reader and the writer from connecting a client to the server, 
        create a RemoteProxyPlayer for them and append it to the list of players 
        contained in this server (self.players).

        If the server should no longer be accepting client connections (see method 
        Server.capacity_reached), then simply close the connection without creating a player.

        SIDE EFFECT: If player successfully signs up, RemoteProxyPlayer created/added to the 
        self.players list.
        """
        try:
            connected_player = await self.create_player(reader, writer)
            self.players.append(connected_player)
        except asyncio.TimeoutError:
            # Player should not be added if they cannot be successfully created.
            writer.close()
            return 
        if self.capacity_reached():
            self.end_sign_up_phase()

    async def create_player(self, reader: StreamReader, writer: StreamWriter) -> RemotePlayerProxy:
        """
        Given a a network I/O StreamReader and StreamWriter, create an instance of a RemotePlayerProxy
        from the data received from the StreamReader and instantiate an instance of  RemotePlayerProxy
        containing the name and age received from the StreamReader and the StreamWriter.
            Parameters:
                reader (StreamReader): The network input stream that receives data from the client (and 
                    will receive player information from the client on).
                writer (StreamWriter): The network output stream where data will be sent to the client.
            Returns:
                A RemotePlayerProxy containing the player name and strategy information received over
                the network, as well as the StreamReader and StreamWriter for the RemoteProxyPlayer
                to receive method returns and send method calls over, respectively.
        """
        data = await asyncio.wait_for(reader.read(MAX_MESSAGE_SIZE), RemotePlayerProxy.TIMEOUT)
        player_information_json = data.decode()
        player_information = json.loads(player_information_json)

        player_name = player_information[self.PLAYER_NAME_INDEX]
        # The oldest player should be the first to join and the youngest player
        # should be the last to join. Thus, we just take the maximum number of 
        # possibly players and subtract the current number of players from that.
        player_age = self.max_players_accepted - len(self.players)

        return RemotePlayerProxy(player_name, player_age, reader, writer)

    # Sign Up Methods

    def sign_up_players(self) -> None:
        """
        Attempts to sign up players to run a game of Trains. This sign up process occurs in two phases.

        The first phase waits for either the maximum number of players to join (self.max_players_accepted)
        or, at the end of the time specified with self.waiting_time
        """
        event_loop = asyncio.get_event_loop()
        first_waiting_phase_handle = \
            event_loop.call_later(self.waiting_time, self.end_loop_upon_players_or_end_of_second_phase)
        second_waiting_phase_handle = \
            event_loop.call_later(self.waiting_time * 2, self.end_loop_upon_players_or_end_of_second_phase)
        self.sign_up_handles = [first_waiting_phase_handle, second_waiting_phase_handle]
        event_loop.run_forever()

    def enough_players_joined(self) -> bool:
        """
        Determines if enough clients have connected to the server in order to run a game.
        This number is accessed by the field self.min_players_accepted.

        As documented in the run_server method, the server initially waits for some
        amount of time (specified with self.waiting_time) for some amount of players
        to join (self.min_players_accepted) and later waits for the minimum number of players
        possible for a game to join.

            Returns:
                True if enough players have joined, else false.
        """
        num_players = len(self.players)

        # self.min_players_accepted is changed from first to second phase.
        return num_players >= self.min_players_accepted \
            and num_players <= self.max_players_accepted 

    def capacity_reached(self) -> bool:
        """
        Determines if the server is connected with the maximum number of players allowed
        to connect (this number is detailed with self.max_players_accepted).
            Returns:
                True if capacity has been reached, else False.
        """
        return len(self.players) == self.max_players_accepted

    def end_loop_upon_players_or_end_of_second_phase(self) -> None:
        """
        Kills the event loop (from asyncio.get_event_loop()) if enough players 
        have joined or if the server is in the second waiting period for 
        sign up.

        SIDE EFFECTS:
            - Sets self.first_wait_phase to False if that phase has come to an end.
            - Sets the minimum number of players accepted to the lowest possible to 
            run a game.
        """
        if not self.first_wait_phase or self.enough_players_joined():
            self.end_sign_up_phase()
        else:
            self.first_wait_phase = False
            self.min_players_accepted = MIN_NUMBER_OF_PLAYERS_FOR_GAME

    def end_sign_up_phase(self) -> None:
        """
        Ends the sign up phase for the server by stopping the running event loop
        that allows for client/server callbacks and cancelling any tasks
        that checked the number of players who joined after either the first or
        second waiting period.

        SIDE EFFECT: Any tasks with handles in the self.sign_up_handles list will be canceled.
        """
        for handle in self.sign_up_handles:
            handle.cancel()
        event_loop = asyncio.get_event_loop()
        event_loop.stop()

    # Running the Tournament
  
    def get_tournament_result(self) -> TournmentResult:
        """
        Gets the result of a tournament. 

        If enough players are availble to run a tournament, we start the tournament
        with the clients connected (RemoteProxyPlayers in self.players).

        Otherwise, return an empty result as no tournament can be run.

            Returns: Result of running a tournament with the players connected to the server, or no
                result if this is not possible.
        """
        result = NO_RESULT
        if self.enough_players_joined():
            try:
                result = self.start_tournament()
            except NotEnoughDestinations:
                return result
        return result

    def start_tournament(self) -> TournmentResult:
        """
        Creates a new Manager with the list of RemotePlayerProxy (self.players) from clients who have connected.
        Runs the tournament with the RemotePlayerProxy's and returns the result from doing so.
            Returns: [List[Player], List[Player]], a list containing two elements:
                    - The List of Winners
                    - The List of Cheaters
        """
        manager = Manager(self.players, self.deck)
        return manager.run_tournament()
