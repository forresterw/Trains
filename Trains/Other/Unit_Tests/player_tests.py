import unittest, sys, os


sys.path.append('../../../')
from Trains.Common.player_game_state import PlayerGameState
from Trains.Common.map import Connection, City, Destination, Color, Map
from Trains.Player.buy_now import Buy_Now
from Trains.Player.hold_10 import Hold_10
from Trains.Player.moves import MoveType
from Trains.Player.strategy import PlayerStrategyInterface, AbstractPlayerStrategy
from Trains.Player.buy_now_player import Buy_Now_Player
from Trains.Player.hold_10_player import Hold_10_Player
from Trains.Player.dynamic_player import DynamicPlayer
from Trains.Player.player import PlayerInterface
from Trains.Other.Strategies.dynamic_hold_10 import Dynamic_Hold_10


class TestPlayerHold10(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 20)
        self.new_york = City("New York", 60, 30)
        self.austin = City("Austin", 50, 80)
        self.houston = City("Houston", 50, 90)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.wdc = City("Washington D.C.", 55, 60)
        self.cities = {self.boston, self.new_york, self.austin, self.houston, self.philadelphia, self.los_angeles, self.wdc}

        self.connection1 = Connection(frozenset({self.boston, self.new_york}), Color.BLUE, 4)
        self.connection2 = Connection(frozenset({self.philadelphia, self.new_york}), Color.GREEN, 3)
        self.connection3 = Connection(frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection4 = Connection(frozenset({self.austin, self.los_angeles}), Color.BLUE, 5)
        self.connection5 = Connection(frozenset({self.wdc, self.philadelphia}), Color.WHITE, 3)
        self.connection6 = Connection(frozenset({self.wdc, self.philadelphia}), Color.WHITE, 4)
        self.connection7 = Connection(frozenset({self.wdc, self.philadelphia}), Color.RED, 4)
        self.connection8 = Connection(frozenset({self.austin, self.los_angeles}), Color.GREEN, 5)
        self.all_connections = {self.connection1, self.connection2, self.connection3, self.connection4, \
            self.connection5, self.connection6, self.connection7, self.connection8}

        self.game_map = Map(self.cities, self.all_connections)

        self.dest1 = Destination(frozenset({self.austin, self.new_york}))
        self.dest2 = Destination(frozenset({self.boston, self.houston}))
        self.dest3 = Destination(frozenset({self.austin, self.houston}))

        self.age = 10
        self.name = "test_player_hold_10"
        self.test_h10 = Hold_10_Player(self.name, self.age)
        self.t10_initial_cards = {Color.RED: 2, Color.BLUE: 4, Color.GREEN: 3, Color.WHITE: 2}
        self.t10_initial_rails = 45
        self.t10_destinations = {self.dest1, self.dest2, self.dest3}
        self.t10_available_connections = {self.connection1, self.connection2, self.connection3, \
            self.connection4, self.connection5, self.connection6, self.connection7, self.connection8}

    def test_hold_10_constructor(self):
        test_player = Hold_10_Player(self.name, self.age)

        self.assertEqual(test_player.name, self.name)
        self.assertEqual(test_player.age, self.age)
        self.assertEqual(type(test_player.strategy), Hold_10)
        self.assertIsNone(test_player.game_state)

    def test_select_destinations_select_two_hold_10(self):
        number_of_destination = 2
        destinations = self.test_h10.strategy.select_destinations(self.t10_destinations, number_of_destination)
        self.assertEqual(destinations, {self.dest1, self.dest3})

    def test_select_destinations_select_three_hold_10(self):
        number_of_destination = 3
        destinations = self.test_h10.strategy.select_destinations(self.t10_destinations, number_of_destination)
        self.assertEqual(destinations, {self.dest1, self.dest2, self.dest3})

    def test_select_destinations_invalid_select_number_hold_10(self):
        number_of_destination = 4
        with self.assertRaises(ValueError):
            destinations = self.test_h10.strategy.select_destinations(self.t10_destinations, number_of_destination)

    def test_initialize_hold_10(self):
        # Sets up player with initial resourcres and map.
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)

        # The internal state should match the return value
        self.assertEqual(self.test_h10.game_state.colored_cards, self.t10_initial_cards)
        self.assertEqual(self.test_h10.game_state.rails, self.t10_initial_rails)
        self.assertEqual(self.test_h10.game_state.connections, set())
        self.assertEqual(self.test_h10.game_state.game_info, {})
        self.assertEqual(self.test_h10.game_state.opponent_info, [])

    def test_update_player_game_state_hold_10(self):
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        pre_connections = self.test_h10.game_state.connections
        pre_colored_cards = self.test_h10.game_state.colored_cards
        pre_rails = self.test_h10.game_state.rails
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, self.test_h10.game_state.colored_cards, \
            self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        # Old values stay the same
        self.assertEqual(self.test_h10.game_state.colored_cards, pre_colored_cards)
        self.assertEqual(self.test_h10.game_state.rails, pre_rails)
        self.assertEqual(self.test_h10.game_state.connections, pre_connections)
        # Update other game values
        self.assertEqual(self.test_h10.game_state.game_info["unacquired_connections"], self.t10_available_connections)
        self.assertEqual(self.test_h10.game_state.game_info["colored_cards"], 125)
        self.assertEqual(self.test_h10.game_state.opponent_info, [])

    def test_select_connection_hold_10_no_cards(self):
        self.t10_initial_cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, self.test_h10.game_state.colored_cards, \
            self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        connection = self.test_h10.strategy.select_connection(self.test_h10.game_state)

        self.assertIsNone(connection)

    def test_select_connection_hold_10_1_break_tie_with_second_city_name(self):
        self.t10_initial_cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 4, Color.WHITE: 0}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, self.test_h10.game_state.colored_cards, \
            self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        connection = self.test_h10.strategy.select_connection(self.test_h10.game_state)
        self.assertEqual(connection, self.connection3)

    def test_select_connection_hold_10_break_tie_with_length(self):
        self.t10_initial_cards = {Color.RED: 5, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 5}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, self.test_h10.game_state.colored_cards, \
            self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        connection = self.test_h10.strategy.select_connection(self.test_h10.game_state)
        self.assertEqual(connection, self.connection5)

    def test_select_connection_hold_10_break_tie_with_color(self):
        self.t10_initial_cards = {Color.RED: 5, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 0}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, self.test_h10.game_state.colored_cards, \
            self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        connection = self.test_h10.strategy.select_connection(self.test_h10.game_state)
        self.assertEqual(connection, self.connection4)

    def test_get_move_hold_10_draw(self):
        self.t10_initial_cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, self.test_h10.game_state.colored_cards, \
            self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        move = self.test_h10.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.DRAW_CARDS)

    def test_get_move_hold_10_draw_at_exactly_10(self):
        self.t10_initial_cards = {Color.RED: 10, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, self.test_h10.game_state.colored_cards, \
            self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        move = self.test_h10.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.DRAW_CARDS)

    def test_get_move_hold_10_11_cards(self):
        self.t10_initial_cards = {Color.RED: 11, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, \
            self.test_h10.game_state.colored_cards, self.test_h10.game_state.rails, \
                self.test_h10.game_state.destinations, \
                    {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        move = self.test_h10.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.ACQUIRE_CONNECTION)
        self.assertEqual(move.connection, self.connection7)

    def test_get_move_hold_10_break_tie_with_length(self):
        self.t10_initial_cards = {Color.RED: 5, Color.BLUE: 1, Color.GREEN: 0, Color.WHITE: 5}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, self.test_h10.game_state.colored_cards, \
            self.test_h10.game_state.rails, self.test_h10.game_state.destinations, {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        move = self.test_h10.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.ACQUIRE_CONNECTION)
        self.assertEqual(move.connection, self.connection5)

    def test_get_move_hold_10_break_tie_with_color(self):
        self.t10_initial_cards = {Color.RED: 5, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 1}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, \
            self.test_h10.game_state.colored_cards, self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        move = self.test_h10.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.ACQUIRE_CONNECTION)
        self.assertEqual(move.connection, self.connection4)

    def test_can_acquire_connection_true(self):
        self.t10_initial_cards = {Color.RED: 5, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 1}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, \
            self.test_h10.game_state.colored_cards, self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        self.assertEqual(self.test_h10.can_acquire_connection(self.connection1), True)

    def test_can_acquire_connection_false(self):
        self.t10_initial_cards = {Color.RED: 1, Color.BLUE: 2, Color.GREEN: 0, Color.WHITE: 1}
        self.test_h10.setup(self.game_map, self.t10_initial_rails, self.t10_initial_cards)
        updated_game_state = PlayerGameState(self.test_h10.game_state.connections, \
            self.test_h10.game_state.colored_cards, self.test_h10.game_state.rails, self.test_h10.game_state.destinations, \
                {"unacquired_connections": self.t10_available_connections, "colored_cards": 125}, [])
        self.test_h10.update_player_game_state(updated_game_state)

        self.assertEqual(self.test_h10.can_acquire_connection(self.connection1), False)

    def test_get_lex_order_destinations(self):
        self.assertEqual(self.test_h10.strategy.get_lexicographic_order_of_destinations(list(self.t10_destinations)), \
            [self.dest3, self.dest1, self.dest2])

    def test_get_lex_order_connections(self):
        self.assertEqual(self.test_h10.strategy.get_lexicographic_order_of_connections([self.connection1, self.connection2, \
            self.connection3, self.connection4]), [self.connection4, self.connection1, self.connection3, self.connection2])


class TestPlayerBuyNow(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 20)
        self.new_york = City("New York", 60, 30)
        self.austin = City("Austin", 50, 80)
        self.houston = City("Houston", 50, 90)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.wdc = City("Washington D.C.", 55, 60)
        self.cities = {self.boston, self.new_york, self.austin, self.houston, self.philadelphia, self.los_angeles, self.wdc}

        self.connection1 = Connection(frozenset({self.boston, self.new_york}), Color.BLUE, 4)
        self.connection2 = Connection(frozenset({self.philadelphia, self.new_york}), Color.GREEN, 3)
        self.connection3 = Connection(frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection4 = Connection(frozenset({self.austin, self.los_angeles}), Color.BLUE, 5)
        self.connection5 = Connection(frozenset({self.wdc, self.philadelphia}), Color.WHITE, 3)
        self.connection6 = Connection(frozenset({self.wdc, self.philadelphia}), Color.WHITE, 4)
        self.connection7 = Connection(frozenset({self.wdc, self.philadelphia}), Color.RED, 4)
        self.connection8 = Connection(frozenset({self.austin, self.los_angeles}), Color.GREEN, 5)
        self.all_connections = {self.connection1, self.connection2, self.connection3, self.connection4, \
            self.connection5, self.connection6, self.connection7, self.connection8}

        self.game_map = Map(self.cities, self.all_connections)

        self.dest1 = Destination(frozenset({self.austin, self.new_york}))
        self.dest2 = Destination(frozenset({self.boston, self.houston}))
        self.dest3 = Destination(frozenset({self.austin, self.houston}))

        self.age = 20
        self.name = "test_player_buy_now"
        self.test_bn = Buy_Now_Player(self.name, self.age)
        self.bn_initial_cards = {Color.RED: 2, Color.BLUE: 4, Color.GREEN: 3, Color.WHITE: 2}
        self.bn_initial_rails = 45
        self.bn_destinations = {self.dest1, self.dest2, self.dest3}
        self.bn_available_connections = {self.connection1, self.connection2, self.connection3, \
            self.connection4, self.connection5, self.connection6, self.connection7, self.connection8}

    def test_buy_now_constructor(self):
        test_player = Buy_Now_Player(self.name, self.age)

        self.assertEqual(test_player.name, self.name)
        self.assertEqual(test_player.age, self.age)
        self.assertEqual(type(test_player.strategy), Buy_Now)
        self.assertIsNone(test_player.game_state)

    def test_select_destinations_select_two_buy_now(self):
        number_of_destination = 2
        destinations = self.test_bn.strategy.select_destinations(self.bn_destinations, number_of_destination)
        self.assertEqual(destinations, {self.dest1, self.dest2})

    def test_select_destinations_select_three_buy_now(self):
        number_of_destination = 3
        destinations = self.test_bn.strategy.select_destinations(self.bn_destinations, number_of_destination)
        self.assertEqual(destinations, {self.dest1, self.dest2, self.dest3})

    def test_select_destinations_invalid_select_number_hold_10(self):
        number_of_destination = 4
        with self.assertRaises(ValueError):
            destinations = self.test_bn.strategy.select_destinations(self.bn_destinations, number_of_destination)

    def test_initialize_buy_now(self):
        # Set up player with initial rails, initial cards, and the game map.
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)

        # The internal state should match the return value
        self.assertEqual(self.test_bn.game_state.colored_cards, self.bn_initial_cards)
        self.assertEqual(self.test_bn.game_state.rails, self.bn_initial_rails)
        self.assertEqual(self.test_bn.game_state.connections, set())
        self.assertEqual(self.test_bn.game_state.game_info, {})
        self.assertEqual(self.test_bn.game_state.opponent_info, [])

    def test_update_player_game_state_buy_now(self):
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        pre_connections = self.test_bn.game_state.connections
        pre_colored_cards = self.test_bn.game_state.colored_cards
        pre_rails = self.test_bn.game_state.rails
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, \
                {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        # Old values stay the same
        self.assertEqual(self.test_bn.game_state.colored_cards, pre_colored_cards)
        self.assertEqual(self.test_bn.game_state.rails, pre_rails)
        self.assertEqual(self.test_bn.game_state.connections, pre_connections)
        # Update other game values
        self.assertEqual(self.test_bn.game_state.game_info["unacquired_connections"], self.bn_available_connections)
        self.assertEqual(self.test_bn.game_state.game_info["colored_cards"], 125)
        self.assertEqual(self.test_bn.game_state.opponent_info, [])

    def test_select_connection_buy_now_no_cards(self):
        self.bn_initial_cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, \
                {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        connection = self.test_bn.strategy.select_connection(self.test_bn.game_state)

        self.assertIsNone(connection)

    def test_select_connection_buy_now_break_tie_with_second_city_name(self):
        self.bn_initial_cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 4, Color.WHITE: 0}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, \
            self.test_bn.game_state.colored_cards, self.test_bn.game_state.rails, \
                self.test_bn.game_state.destinations, {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        connection = self.test_bn.strategy.select_connection(self.test_bn.game_state)
        self.assertEqual(connection, self.connection3)

    def test_select_connection_buy_now_break_tie_with_length(self):
        self.bn_initial_cards = {Color.RED: 5, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 5}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        connection = self.test_bn.strategy.select_connection(self.test_bn.game_state)
        self.assertEqual(connection, self.connection5)

    def test_select_connection_buy_now_break_tie_with_color(self):
        self.bn_initial_cards = {Color.RED: 5, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 0}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, \
                {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        connection = self.test_bn.strategy.select_connection(self.test_bn.game_state)
        self.assertEqual(connection, self.connection4)

    def test_get_move_buy_now_draw_not_enough_cards(self):
        self.bn_initial_cards = {Color.RED: 2, Color.BLUE: 2, Color.GREEN: 2, Color.WHITE: 2}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, \
                {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        move = self.test_bn.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.DRAW_CARDS)

    def test_get_move_buy_now_draw_at_exactly_10(self):
        self.bn_initial_cards = {Color.RED: 3, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, \
            self.test_bn.game_state.colored_cards, self.test_bn.game_state.rails, \
                self.test_bn.game_state.destinations, {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        move = self.test_bn.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.DRAW_CARDS)

    def test_get_move_buy_now_enough_cards_to_aquire(self):
        self.bn_initial_cards = {Color.RED: 11, Color.BLUE: 2, Color.GREEN: 0, Color.WHITE: 0}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, \
                {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        move = self.test_bn.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.ACQUIRE_CONNECTION)
        self.assertEqual(move.connection, self.connection7)

    def test_get_move_buy_now_break_tie_with_length(self):
        self.bn_initial_cards = {Color.RED: 5, Color.BLUE: 1, Color.GREEN: 0, Color.WHITE: 5}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, \
                {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        move = self.test_bn.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.ACQUIRE_CONNECTION)
        self.assertEqual(move.connection, self.connection5)

    def test_get_move_buy_now_break_tie_with_color(self):
        self.bn_initial_cards = {Color.RED: 5, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 1}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, \
                {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        move = self.test_bn.play(updated_game_state)
        self.assertEqual(move.move_type, MoveType.ACQUIRE_CONNECTION)
        self.assertEqual(move.connection, self.connection4)

    def test_can_acquire_connection_true(self):
        self.bn_initial_cards = {Color.RED: 5, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 1}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, \
                {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        self.assertEqual(self.test_bn.can_acquire_connection(self.connection1), True)

    def test_can_acquire_connection_false(self):
        self.bn_initial_cards = {Color.RED: 1, Color.BLUE: 2, Color.GREEN: 0, Color.WHITE: 1}
        self.test_bn.setup(self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        updated_game_state = PlayerGameState(self.test_bn.game_state.connections, self.test_bn.game_state.colored_cards, \
            self.test_bn.game_state.rails, self.test_bn.game_state.destinations, \
                {"unacquired_connections": self.bn_available_connections, "colored_cards": 125}, [])
        self.test_bn.update_player_game_state(updated_game_state)

        self.assertEqual(self.test_bn.can_acquire_connection(self.connection1), False)

    def test_get_lex_order_destinations(self):
        self.assertEqual(self.test_bn.strategy.get_lexicographic_order_of_destinations(list(self.bn_destinations)), [self.dest3, self.dest1, self.dest2])

    def test_get_lex_order_connections(self):
        self.assertEqual(self.test_bn.strategy.get_lexicographic_order_of_connections([self.connection1, self.connection2, self.connection3, self.connection4]), [self.connection4, self.connection1, self.connection3, self.connection2])


class TestPlayerDynamicallyLoadedStrategy(unittest.TestCase):
    # We do not test the strategy itself because it is simply the Hold_10 strategy dynamically loaded
    def setUp(self):
        self.age = 20
        self.name = "test_player_dynamic_hold_10"
        self.rel_filepath = "../Strategies/dynamic_hold_10.py"
        self.abs_filepath = os.path.abspath(self.rel_filepath)

    def test_constructor_absolute_file_path(self):
        abs_dh10 = DynamicPlayer(self.name, self.age, self.abs_filepath)
        self.assertEqual(abs_dh10.name, self.name)
        self.assertEqual(abs_dh10.age, self.age)
        self.assertTrue(issubclass(abs_dh10.strategy.__class__, AbstractPlayerStrategy))
        self.assertTrue(isinstance(abs_dh10.strategy, PlayerStrategyInterface))
        self.assertEqual(type(abs_dh10.strategy).__name__, Dynamic_Hold_10.__name__)

    def test_constructor_relative_file_path(self):
        rel_dh10 = DynamicPlayer(self.name, self.age, self.rel_filepath)
        self.assertEqual(rel_dh10.name, self.name)
        self.assertEqual(rel_dh10.age, self.age)
        self.assertTrue(issubclass(rel_dh10.strategy.__class__, AbstractPlayerStrategy))
        self.assertTrue(isinstance(rel_dh10.strategy, PlayerStrategyInterface))
        self.assertEqual(type(rel_dh10.strategy).__name__, Dynamic_Hold_10.__name__)

if __name__ == '__main__':
    unittest.main()
