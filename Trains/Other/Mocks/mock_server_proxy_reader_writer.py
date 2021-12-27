import asyncio

from Trains.Remote.server_proxy import ServerProxy, GamePlayException


class MockServerProxy(ServerProxy):
    """Mock of a Server proxy object that takes in a reader and writer in the constructor.
        This is used to test how the server proxy reads and writes to streams."""

    def __init__(self, hostname: str, port: int, player_name: str, strategy_name: str, reader, writer, map: Map) -> None:
        self.server_reader = reader
        self.server_writer = writer
        super().__init(hostname, port, player_name, strategy_name, map)

    def join_and_play_game(self) -> bool:
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
        # Connect to the server and return the reader and writer for data
        # transmission.
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        print("Getting reader and writer.")
        #self.server_reader, self.server_writer = \
        #    self.event_loop.run_until_complete(asyncio.open_connection(self.hostname, self.port))

        # Sign Up with Server
        print("Begin sign up.")
        self.event_loop.run_until_complete(self.sign_up_with_server())

        # Look for messages. If method call received, act accordingly.
        # Get the result of the game. If player booted, set result to False
        # as this is equivalent to being booted.

        try:
            # WAIT until game started:
            print("Begin game.")
            result = self.event_loop.run_until_complete(self.execute_gameplay())
        except GamePlayException:
            print("Gameplay Error.")
            result = False

        self.server_writer.close()
        self.event_loop.close()

        return result
