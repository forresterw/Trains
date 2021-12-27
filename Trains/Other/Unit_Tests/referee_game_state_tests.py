from collections import deque
import random
import sys
sys.path.append('../../../')

import unittest
from Trains.Admin.referee_game_state import RefereeGameState
from Trains.Common.player_game_state import PlayerGameState
from Trains.Common.map import Connection, City, Destination, Map, Color

class TestRefereeGameState(unittest.TestCase):
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
        self.pgs1 = PlayerGameState({self.connection1, self.connection2}, self.cc1, 10, {self.dest1, self.dest2}, dict(), [])
        self.cc2 = {Color.RED: 9, Color.BLUE: 10, Color.GREEN: 11, Color.WHITE: 12}
        self.pgs2 = PlayerGameState({self.connection3, self.connection4}, self.cc2, 4, {self.dest3, self.dest1}, dict(), [])
        self.rgs = RefereeGameState(self.test_map, self.deck, [self.pgs1, self.pgs2])

    def test_constructor(self):
        cc1 = {Color.RED: 5, Color.BLUE: 6, Color.GREEN: 7, Color.WHITE: 8}
        pgs1 = PlayerGameState({self.connection1, self.connection2}, cc1, 10, {self.dest1, self.dest2}, dict(), [])
        cc2 = {Color.RED: 9, Color.BLUE: 10, Color.GREEN: 11, Color.WHITE: 12}
        pgs2 = PlayerGameState({self.connection3, self.connection4}, cc2, 4, {self.dest3, self.dest1}, dict(), [])
        rgs = RefereeGameState(self.test_map, self.deck, [pgs1, pgs2])

        self.assertEqual(rgs.map, self.test_map)
        self.assertEqual(rgs.colored_card_deck, self.deck)
        self.assertEqual(rgs.player_game_states[0], pgs1)
        self.assertEqual(rgs.player_game_states[1], pgs2)
        self.assertEqual(rgs.free_connections, rgs.get_all_unacquired_connections())
        self.assertEqual(rgs.turn, 0)

    def test_constructor_invalid_map(self):
        with self.assertRaises(ValueError):
            RefereeGameState("map", self.deck, [("player1", self.pgs1), ("player2", self.pgs2)])

    def test_constructor_invalid_colored_card_deck(self):
        deck = []
        with self.assertRaises(ValueError):
            RefereeGameState(self.test_map, deck, [("player1", self.pgs1), ("player2", self.pgs2)])

    def test_constructor_invalid_player_game_state_entry_type(self):
        with self.assertRaises(ValueError):
            RefereeGameState(self.test_map, self.deck, [["player1", self.pgs1], ("player2", self.pgs2)])

    def test_constructor_invalid_player_game_state_entry_too_long(self):
        with self.assertRaises(ValueError):
            RefereeGameState(self.test_map, self.deck, [("player1", self.pgs1, "winner"), ("player2", self.pgs2)])

    def test_constructor_invalid_player_game_state_entry_too_short(self):
        with self.assertRaises(ValueError):
            RefereeGameState(self.test_map, self.deck, [(self.pgs1), ("player2", self.pgs2)])

    def test_constructor_invalid_player_game_state_entry_bad_identifier(self):
        with self.assertRaises(ValueError):
            RefereeGameState(self.test_map, self.deck, [(1, self.pgs1), ("player2", self.pgs2)])

    def test_constructor_invalid_player_game_state_entry_bad_player_resources(self):
        with self.assertRaises(ValueError):
            RefereeGameState(self.test_map, self.deck, [("player1", "bad resources"), ("player2", self.pgs2)])

    def test_turns(self):
        self.assertEqual(self.rgs.turn, 0)
        self.rgs.next_turn()
        self.assertEqual(self.rgs.turn, 1)
        self.rgs.next_turn()
        self.assertEqual(self.rgs.turn, 0)
        self.rgs.next_turn()
        self.assertEqual(self.rgs.turn, 1)

    def test_get_player_game_state(self):
        self.assertEqual(self.rgs.get_player_game_state(), self.pgs1)
        self.rgs.next_turn()
        self.assertEqual(self.rgs.get_player_game_state(), self.pgs2)

    def test_get_all_player_connections(self):
        all_cities = set(self.pgs1.connections)
        for city in self.pgs2.connections:
            all_cities.add(city)
        self.assertEqual(self.rgs.get_all_player_connections(), all_cities)

    def test_verify_legal_connection_for_player_valid(self):
        self.assertEqual(self.rgs.verify_legal_connection_for_player(self.connection5, self.pgs1), True)

    def test_verify_legal_connection_for_player_invalid_connection_already_acquired1(self):
        self.assertEqual(self.rgs.verify_legal_connection_for_player(self.connection1, self.pgs1), False)

    def test_verify_legal_connection_for_player_invalid_connection_already_acquired2(self):
        self.assertEqual(self.rgs.verify_legal_connection_for_player(self.connection3, self.pgs1), False)

    def test_verify_legal_connection_for_player_invalid_not_enough_rails(self):
        pr1 = PlayerGameState({self.connection1, self.connection2}, self.cc1, 1, {self.dest1, self.dest2}, dict(), [])
        self.assertEqual(self.rgs.verify_legal_connection_for_player(self.connection5, pr1), False)

    def test_verify_legal_connection_for_player_invalid_not_enough_colored_cards(self):
        cc1 = {Color.RED: 5, Color.BLUE: 6, Color.GREEN: 7, Color.WHITE: 2}
        pr1 = PlayerGameState({self.connection1, self.connection2}, cc1, 10, {self.dest1, self.dest2}, dict(), [])
        self.assertEqual(self.rgs.verify_legal_connection_for_player(self.connection5, pr1), False)

    def test_verify_legal_connection_valid(self):
        self.rgs.next_turn()
        self.rgs.next_turn()
        self.assertEqual(self.rgs.verify_legal_connection(self.connection5), True)

    def test_verify_legal_connection_invalid_already_acquired(self):
        self.assertEqual(self.rgs.verify_legal_connection(self.connection1), False)

    def test_verify_legal_connection_invalid_not_enough_rails(self):
        cc1 = {Color.RED: 5, Color.BLUE: 6, Color.GREEN: 7, Color.WHITE: 8}
        pgs1 = PlayerGameState({self.connection1, self.connection2}, cc1, 10, {self.dest1, self.dest2}, dict(), [])
        cc2 = {Color.RED: 9, Color.BLUE: 10, Color.GREEN: 11, Color.WHITE: 12}
        pgs2 = PlayerGameState({self.connection3, self.connection4}, cc2, 4, {self.dest3, self.dest1}, dict(), [])
        rgs = RefereeGameState(self.test_map, self.deck, [pgs1, pgs2])
        rgs.next_turn()
        self.assertEqual(rgs.verify_legal_connection(self.connection5), False)

    def test_verify_legal_connection_invalid_not_enough_colored_cards(self):
        cc1 = {Color.RED: 5, Color.BLUE: 6, Color.GREEN: 7, Color.WHITE: 8}
        pgs1 = PlayerGameState({self.connection1, self.connection2}, cc1, 10, {self.dest1, self.dest2}, dict(), [])
        cc2 = {Color.RED: 9, Color.BLUE: 10, Color.GREEN: 11, Color.WHITE: 0}
        pgs2 = PlayerGameState({self.connection3, self.connection4}, cc2, 7, {self.dest3, self.dest1}, dict(), [])
        rgs = RefereeGameState(self.test_map, self.deck, [pgs1, pgs2])
        rgs.next_turn()
        self.assertEqual(rgs.verify_legal_connection(self.connection5), False)

    def test_get_all_acquirable_connections(self):
        self.assertEqual(self.rgs.get_all_acquirable_connections(self.pgs1), {self.connection5})

    def test_get_all_acquirable_connections_but_there_are_none(self):
        self.assertEqual(self.rgs.get_all_acquirable_connections(self.pgs2), set())

    def test_get_all_unacquired_connections(self):
        self.assertEqual(self.rgs.get_all_unacquired_connections(), {self.connection5})

    def test_get_all_unacquired_connections_but_none(self):
        self.pgs1.connections.add(self.connection5)
        self.rgs.next_turn()
        self.assertEqual(self.rgs.get_all_unacquired_connections(), set())

    def test_get_cards_from_deck(self):
        NUM_CARDS_ON_DRAW = 2
        deck = deque([Color.RED, Color.BLUE, Color.GREEN, Color.WHITE])
        rgs = RefereeGameState(self.test_map, deck, [self.pgs1, self.pgs2])
        drawn_cards = rgs.get_cards_from_deck(NUM_CARDS_ON_DRAW)
        self.assertEqual(drawn_cards, [Color.WHITE, Color.GREEN])
        self.assertEqual(rgs.colored_card_deck, deque([Color.RED, Color.BLUE]))

    def test_get_cards_from_deck_only_1_card_in_deck(self):
        NUM_CARDS_ON_DRAW = 2
        deck = deque([Color.WHITE])
        rgs = RefereeGameState(self.test_map, deck, [self.pgs1, self.pgs2])
        drawn_cards = rgs.get_cards_from_deck(NUM_CARDS_ON_DRAW)
        self.assertEqual(drawn_cards, [Color.WHITE])
        self.assertEqual(rgs.colored_card_deck, deque())

    def test_get_cards_from_deck_empty_deck(self):
        NUM_CARDS_ON_DRAW = 2
        deck = deque()
        rgs = RefereeGameState(self.test_map, deck, [self.pgs1, self.pgs2])
        drawn_cards = rgs.get_cards_from_deck(NUM_CARDS_ON_DRAW)
        self.assertEqual(drawn_cards, [])
        self.assertEqual(rgs.colored_card_deck, deque())

    def test_on_last_turn_true(self):
        rails = 1
        pgs1 = PlayerGameState({self.connection1, self.connection2}, self.cc1, rails, {self.dest1, self.dest2}, dict(), [])
        rgs = RefereeGameState(self.test_map, self.deck, [pgs1, self.pgs2])
        self.assertTrue(rgs.on_last_turn())

    def test_on_last_turn_false(self):
        rails = 10
        pgs1 = PlayerGameState({self.connection1, self.connection2}, self.cc1, rails, {self.dest1, self.dest2}, dict(), [])
        rgs = RefereeGameState(self.test_map, self.deck, [pgs1, self.pgs2])
        self.assertFalse(rgs.on_last_turn())

    def test_on_last_turn_false_exactly_3_rails(self):
        rails = 3
        pgs1 = PlayerGameState({self.connection1, self.connection2}, self.cc1, rails, {self.dest1, self.dest2}, dict(), [])
        rgs = RefereeGameState(self.test_map, self.deck, [pgs1, self.pgs2])
        self.assertFalse(rgs.on_last_turn())

    def test_get_current_active_player_index_first_turn(self):
        self.assertEqual(self.rgs.get_current_active_player_index(), 0)

    def test_get_current_active_player_index_next_turn(self):
        self.rgs.next_turn()
        self.assertEqual(self.rgs.get_current_active_player_index(), 1)

    def test_get_current_active_player_index_wrap_around(self):
        self.assertEqual(self.rgs.get_current_active_player_index(), 0)

    def test_detect_state_change_no_change_true(self):
        self.rgs.next_turn()
        self.rgs.next_turn()
        self.assertTrue(self.rgs.no_change_after_cycle())

    def test_detect_state_change_no_change_false_one_turn(self):
        self.rgs.next_turn()
        self.assertFalse(self.rgs.no_change_after_cycle())

    def test_detect_state_change_no_change_false_multiple_turns(self):
        deck = deque([Color.RED for _ in range(random.randint(2, 100))])
        rgs = RefereeGameState(self.test_map, deck, [self.pgs1, self.pgs2])
        rgs.next_turn()
        rgs.colored_card_deck.pop()
        rgs.colored_card_deck.pop()
        rgs.next_turn()
        self.assertFalse(self.rgs.no_change_after_cycle())

    def test_referee_game_state_equality_true(self):
        rgs2 = RefereeGameState(self.test_map, self.deck, [self.pgs1, self.pgs2])
        self.assertTrue(self.rgs == rgs2)

    def test_referee_game_state_equality_false_deck(self):
        rgs2 = RefereeGameState(self.test_map, deque([Color.RED]), [self.pgs1, self.pgs2])
        self.assertFalse(self.rgs == rgs2)

    def test_referee_game_state_equality_false_map(self):
        connections = {self.connection1, self.connection2, self.connection3, self.connection4}
        test_map = Map(self.cities, connections)
        rgs2 = RefereeGameState(test_map, self.deck, [self.pgs1, self.pgs2])
        self.assertFalse(self.rgs == rgs2)

    def test_referee_game_state_equality_false_type(self):
        self.assertFalse(self.rgs == self.pgs1)

    def test_referee_game_state_equality_false_player_game_states(self):
        pgs2 = PlayerGameState({self.connection3, self.connection4}, self.cc2, 10, {self.dest3, self.dest1}, dict(), [])
        rgs2 = RefereeGameState(self.test_map, self.deck, [self.pgs1, pgs2])
        self.assertFalse(self.rgs == rgs2)


if __name__ == '__main__':
    unittest.main()