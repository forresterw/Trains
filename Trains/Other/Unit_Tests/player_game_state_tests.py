from collections import deque
import sys
sys.path.append('../../../')

import unittest
from Trains.Common.player_game_state import PlayerGameState
from Trains.Common.map import Connection, City, Destination, Map, Color
  

class TestPlayerGameState(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.austin = City("Austin", 50, 15)
        self.wdc = City("Washington D.C.", 55, 60)
        self.connection1 = Connection(frozenset({self.boston, self.new_york}), Color.BLUE, 3)
        self.connection2 = Connection(frozenset({self.philadelphia, self.new_york}), Color.RED, 3)
        self.connection3 = Connection(frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection4 = Connection(frozenset({self.austin, self.los_angeles}), Color.WHITE, 5)
        self.connection5 = Connection(frozenset({self.wdc, self.philadelphia}), Color.WHITE, 5)
        self.cities = {self.boston, self.new_york, self.philadelphia, self.los_angeles, self.austin, self.wdc}
        self.connections = {self.connection1, self.connection2, self.connection3, self.connection4, self.connection5}
        self.test_map = Map(self.cities, self.connections)
        self.dest1 = Destination({self.new_york, self.philadelphia})
        self.dest2 = Destination({self.new_york, self.boston})
        self.dest3 = Destination({self.boston, self.philadelphia})

        self.deck = deque()
        self.cc1 = {Color.RED: 5, Color.BLUE: 6, Color.GREEN: 7, Color.WHITE: 8}
        self.pr1 = PlayerGameState({self.connection1, self.connection2}, self.cc1, 10, {self.dest1, self.dest2}, dict(), [])
        self.cc2 = {Color.RED: 9, Color.BLUE: 10, Color.GREEN: 11, Color.WHITE: 12}
        self.pr2 = PlayerGameState({self.connection3, self.connection4}, self.cc2, 4, {self.dest3, self.dest1}, dict(), [])

    def test_constructor(self):
        test_pr = PlayerGameState({self.connection1, self.connection2}, self.cc1, 10, {self.dest1, self.dest2}, dict(), [])
        self.assertEqual(test_pr.connections, {self.connection1, self.connection2})
        self.assertEqual(test_pr.colored_cards, self.cc1)
        self.assertEqual(test_pr.rails, 10)
        self.assertEqual(test_pr.destinations, {self.dest1, self.dest2})

    def test_constructor_bad_connections(self):
        with self.assertRaises(ValueError):
            PlayerGameState([self.connection1, self.connection2], self.cc1, 10, {self.dest1, self.dest2}, dict(), [])

    def test_constructor_bad_colored_cards(self):
        with self.assertRaises(ValueError):
            PlayerGameState({self.connection1, self.connection2}, [Color.RED, Color.GREEN], 10, {self.dest1, self.dest2}, dict(), [])

    def test_constructor_bad_card_dictionary_too_low(self):
        test_deck = {Color.RED: -2, Color.BLUE: 6, Color.GREEN: 7, Color.WHITE: 8}
        with self.assertRaises(ValueError):
            PlayerGameState({self.connection1, self.connection2}, test_deck, 10, {self.dest1, self.dest2}, dict(), [])

    def test_constructor_bad_rails_too_low(self):
        with self.assertRaises(ValueError):
            PlayerGameState({self.connection1, self.connection2}, self.cc1, -1, {self.dest1, self.dest2}, dict(), [])

    def test_constructor_bad_destination_type(self):
        with self.assertRaises(ValueError):
            PlayerGameState({self.connection1, self.connection2}, self.cc1, 10, [self.dest1, self.dest2], dict(), [])

    def test_constructor_bad_opponent_info_type(self):
        with self.assertRaises(ValueError):
            PlayerGameState({self.connection1, self.connection2}, self.cc1, 10, [self.dest1, self.dest2], dict(), dict())

    def test_constructor_bad_opponent_info_contents_type(self):
        with self.assertRaises(ValueError):
            PlayerGameState({self.connection1, self.connection2}, self.cc1, 10, [self.dest1, self.dest2], dict(), [list()])

    def test_get_number_of_colored_cards(self):
        self.assertEqual(self.pr1.get_number_of_colored_cards(), 26)

    def test_get_number_of_colored_cards_zero(self):
        cc1 = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        pr1 = PlayerGameState({self.connection1, self.connection2}, cc1, 10, {self.dest1, self.dest2}, dict(), [])
        self.assertEqual(pr1.get_number_of_colored_cards(), 0)

    def test_get_as_json(self):
        dest1 = "[\"Boston\", \"New York\"]"
        dest2 = "[\"New York\", \"Philidelphia\"]"
        rails = "10"
        connection1 = "[\"Boston\", \"New York\", \"blue\", 3]"
        connection2 = "[\"New York\", \"Philidelphia\", \"red\", 3]"
        cards = "{\"red\": 5, \"blue\": 6, \"green\": 7, \"white\": 8}"
        acquired = f"[{connection1}, {connection2}]"
        this_player = f"{{\"destination1\": {dest1}, \"destination2\": {dest2}, \"cards\": {cards}, \"acquired\": {acquired}, \"rails\": {rails}}}"
        opponent_info = "[]"
        exp_json = f"{{ \"this\": {this_player}, \"opponent_info\": {opponent_info}}}"

        exp_json = exp_json.replace(" ", "").replace("\n", "")
        actual_json = self.pr1.get_as_json().replace(" ", "").replace("\n", "")

        self.assertEqual(exp_json, actual_json.replace('\\', ''))


if __name__ == '__main__':
    unittest.main()
