from collections import deque
from copy import deepcopy
import re
import unittest
import sys

sys.path.append('../../../')

from Trains.Common.player_game_state import PlayerGameState
from Trains.Common.map import Connection, City, Destination, Color, Map
from Trains.Player.buy_now_player import Buy_Now_Player
from Trains.Player.hold_10_player import Hold_10_Player
from Trains.Admin.referee import Referee, Cheating, NotEnoughDestinations
from Trains.Player.moves import MoveType, DrawCardMove, PlayerMove
from Trains.Other.Mocks.mock_move_player import MockConfigurablePlayer, MockBuyNowPlayer, BadMove
from Trains.Other.Mocks.mock_bad_setup_player import MockBadSetUpPlayer
from Trains.Other.Mocks.mock_bad_pick_player import MockBadPickPlayer


class TestReferee(unittest.TestCase):
    def setUp(self):
        # Setup a Map
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 90, 10)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.austin = City("Austin", 50, 10)
        self.wdc = City("Washington D.C.", 55, 60)
        self.boise = City("Boise", 30, 50)


        self.connection1 = Connection(frozenset({self.boston, self.new_york}), Color.BLUE, 3)
        self.connection2 = Connection(frozenset({self.boston, self.new_york}), Color.RED, 3)
        self.connection3 = Connection(frozenset({self.boston, self.new_york}), Color.GREEN, 3)
        self.connection4 = Connection(frozenset({self.boston, self.new_york}), Color.WHITE, 3)
        self.connection5 = Connection(frozenset({self.philadelphia, self.new_york}), Color.RED, 4)
        self.connection6 = Connection(frozenset({self.philadelphia, self.new_york}), Color.GREEN, 4)
        self.connection7 = Connection(frozenset({self.philadelphia, self.new_york}), Color.WHITE, 4)
        self.connection8 = Connection(frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection9 = Connection(frozenset({self.boston, self.philadelphia}), Color.BLUE, 4)
        self.connection10 = Connection(frozenset({self.austin, self.los_angeles}), Color.BLUE, 5)
        self.connection11 = Connection(frozenset({self.philadelphia, self.wdc}), Color.WHITE, 5)
        self.connection12 = Connection(frozenset({self.austin, self.boise}), Color.RED, 5)
        self.connection13 = Connection(frozenset({self.boise, self.los_angeles}), Color.GREEN, 5)
        self.connection14 = Connection(frozenset({self.boise, self.philadelphia}), Color.RED, 5)
        self.connection15 = Connection(frozenset({self.boise, self.wdc}), Color.GREEN, 5)


        self.destination1 = Destination({self.boston, self.wdc})
        self.destination2 = Destination({self.austin, self.boise})
        self.destination3 = Destination({self.philadelphia, self.new_york})
        self.destination4 = Destination({self.boston, self.new_york})
        self.destination5 = Destination({self.boise, self.philadelphia})

        self.cities = {self.boston, self.new_york, self.philadelphia, self.los_angeles, self.austin, self.wdc, self.boise}
        self.connections = {self.connection1, self.connection2, self.connection3, self.connection4, self.connection5, self.connection6, self.connection7, self.connection8, self.connection9, self.connection10, self.connection11, self.connection12, self.connection13, self.connection14, self.connection15}
        self.width = 800
        self.height = 800
        self.test_map = Map(self.cities, self.connections, self.height, self.width)

        # Setup ref constants/fields for testing
        self.INITIAL_DECK_SIZE = 250
        self.INITIAL_RAIL_COUNT = 45
        self.INITIAL_NUM_DESTINATIONS = 2
        self.NUM_DESTINATION_OPTIONS = 5
        self.INITIAL_HAND_SIZE = 4
        self.DRAW_NUM = 2
        self.RAIL_SEGMENT_POINT_VALUE = 1
        self.LONGEST_CONTINUOUS_PATH_VALUE = 20
        self.DESTINATION_COMPLETE_VALUE = 10
        self.BANNED_PLAYER_SCORE_REPRESENTATION = -21
        self.feasible_destinations = self.test_map.get_feasible_destinations(self.connections)

        # players list
        self.p1_name = "p1"
        self.p2_name = "p2"
        self.p3_name = "p3"
        self.player_names = [self.p1_name, self.p2_name, self.p3_name]
        self.p1 = Hold_10_Player(self.p1_name, 22)
        self.p2 = Hold_10_Player(self.p2_name, 17)
        self.p3 = Buy_Now_Player(self.p3_name, 12)

        self.players = [self.p1, self.p2, self.p3]
        self.ref = Referee(self.test_map, self.players)
        self.deck = self.ref.initialize_deck(self.INITIAL_DECK_SIZE)
        self.ref.set_up_game_states()


    def test_constructor(self):
        ref = Referee(self.test_map, self.players)
        self.assertEqual(ref.game_map, self.test_map)
        self.assertEqual(ref.players, self.players)
        self.assertEqual(ref.banned_player_indices, set())
        self.assertEqual(ref.took_last_turn, set())

    def test_constructor_invalid_map(self):
        with self.assertRaises(ValueError):
            ref = Referee(self.connections, self.players)
        
    def test_constructor_invalid_num_players_out_of_bounds(self):
        with self.assertRaises(ValueError):
            players = [self.p1]
            ref = Referee(self.test_map, players)

    def test_constructor_invalid_players_not_list(self):
        with self.assertRaises(ValueError):
            players = {self.p1, self.p2, self.p3}
            ref = Referee(self.test_map, players)
    
    def test_constructor_not_enough_destinations(self):
        with self.assertRaises(NotEnoughDestinations):
            cities = {self.boston, self.new_york}
            connections = {self.connection1}
            width = 800
            height = 800
            test_map = Map(cities, connections, height, width)
            ref = Referee(test_map, self.players)

    def test_initialize_deck(self):
        deck = self.ref.initialize_deck(self.INITIAL_DECK_SIZE)

        for card in deck:
            self.assertEqual(type(card), Color)
        
        self.assertEqual(len(deck), self.INITIAL_DECK_SIZE)

    def test_create_initial_player_hand(self):
        hand = self.ref.create_initial_player_hand(self.deck, self.INITIAL_HAND_SIZE)
        self.assertEqual(type(hand), dict)
        self.assertEqual(sum(hand.values()), self.INITIAL_HAND_SIZE)
        str_colors = set()
        for i in range(1, Color.number_of_colors() + 1):
            str_colors.add(Color(i))
        for card_color in hand.keys():
            self.assertIn(card_color, str_colors)

    def test_get_destination_selection(self):
        destination_options = self.ref.get_destination_selection(self.feasible_destinations, self.NUM_DESTINATION_OPTIONS)
        self.assertEqual(len(destination_options), self.NUM_DESTINATION_OPTIONS)
        for destination in destination_options:
            self.assertIn(destination, self.feasible_destinations)

    def test_verify_player_destinations_valid(self):
        destinations_given = set({self.destination1, self.destination2, self.destination3, self.destination4, self.destination5})
        destinations_chosen = set({self.destination1, self.destination2})
        self.assertTrue(self.ref.verify_player_destinations(destinations_given, destinations_chosen))

    def test_verify_player_destinations_invalid_number_of_destinations_too_many(self):
        destinations_given = set({self.destination1, self.destination2, self.destination3, self.destination4, self.destination5})
        destinations_chosen = set({self.destination1, self.destination2, self.destination3})
        self.assertFalse(self.ref.verify_player_destinations(destinations_given, destinations_chosen))

    def test_verify_player_destinations_invalid_number_of_destinations_too_few(self):
        destinations_given = set({self.destination1, self.destination2, self.destination3, self.destination4, self.destination5})
        destinations_chosen = set({self.destination1})
        self.assertFalse(self.ref.verify_player_destinations(destinations_given, destinations_chosen))

    def test_verify_player_destinations_invalid_destination_chosen(self):
        destinations_given = set({self.destination1, self.destination2, self.destination3, self.destination4, self.destination5})
        destination_not_given = Destination({self.boise, self.los_angeles})
        destinations_chosen = set({self.destination1, destination_not_given})
        self.assertFalse(self.ref.verify_player_destinations(destinations_given, destinations_chosen))

    def test_boot_player(self):
        banned_player_connections = self.ref.ref_game_state.player_game_states[0].connections
        self.ref.boot_player(0, "Cheating")
        exp_ban_list = {0}
        self.assertEqual(self.ref.banned_player_indices, exp_ban_list)
        # Should have no connections after being banned
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].connections, set())
        # Their connections were freed to the game again
        for connection in banned_player_connections:
            self.assertIn(connection, self.ref.ref_game_state.get_all_unacquired_connections())

    def test_is_game_over_true_no_change(self):
        self.ref.ref_game_state.no_change = True
        self.assertTrue(self.ref.is_game_over())

    def test_is_game_over_true_low_rails(self):
        for player_index in range(len(self.players)):
            self.ref.ref_game_state.player_game_states[player_index].rails = 0
        self.ref.ref_game_state.on_last_turn()
        self.ref.took_last_turn = self.players
        self.assertTrue(self.ref.is_game_over())

    def test_is_game_over_false(self):
        self.assertFalse(self.ref.is_game_over())

    def test_is_game_over_false_one_player_remaining(self):
        self.ref.banned_player_indices.add(0)
        self.ref.banned_player_indices.add(1)
        self.assertFalse(self.ref.is_game_over())
    
    def test_is_game_over_true_no_players_remaining(self):
        for index in range(len(self.players)):
            self.ref.banned_player_indices.add(index)
        self.assertTrue(self.ref.is_game_over())

    def test_is_game_over_false_player_kicked_more_than_one_player_remaining(self):
        self.ref.banned_player_indices.add(self.players[0])
        self.assertFalse(self.ref.is_game_over())

    def test_execute_draw_move(self):
        deck = deque([Color.GREEN, Color.RED, Color.RED])
        self.ref.ref_game_state.colored_card_deck = deck
        hand_before_draw = self.ref.ref_game_state.player_game_states[0].colored_cards
        exp_hand = deepcopy(hand_before_draw)
        if Color.RED in exp_hand.keys():
            exp_hand[Color.RED] += 2
        else:
            exp_hand[Color.RED] = 2
        self.ref.execute_draw_move()
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].colored_cards, exp_hand)
        self.assertEqual(self.ref.ref_game_state.colored_card_deck, deque([Color.GREEN]))
    
    def test_execute_draw_move_not_the_full_amount_drawn(self):
        deck = deque([Color.RED])
        self.ref.ref_game_state.colored_card_deck = deck
        hand_before_draw = self.ref.ref_game_state.player_game_states[0].colored_cards
        exp_hand = deepcopy(hand_before_draw)
        if Color.RED in exp_hand.keys():
            exp_hand[Color.RED] += 1
        else:
            exp_hand[Color.RED] = 1
        self.ref.execute_draw_move()
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].colored_cards, exp_hand)
        self.assertEqual(self.ref.ref_game_state.colored_card_deck, deque())

    def test_execute_draw_move_none_drawn_empty_deck(self):
        deck = deque()
        self.ref.ref_game_state.colored_card_deck = deck
        hand_before_draw = self.ref.ref_game_state.player_game_states[0].colored_cards
        exp_hand = hand_before_draw
        self.ref.execute_draw_move()
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].colored_cards, exp_hand)
        self.assertEqual(self.ref.ref_game_state.colored_card_deck, deque())

    def test_execute_acquire_connection_move(self):
        SET_BLUE_CARDS = 20
        self.ref.ref_game_state.player_game_states[0].colored_cards[Color.BLUE] = SET_BLUE_CARDS
        self.ref.execute_acquire_connection_move(self.connection1)
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].colored_cards[Color.BLUE], SET_BLUE_CARDS - self.connection1.length)
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].rails, self.INITIAL_RAIL_COUNT - self.connection1.length)
        self.assertIn(self.connection1, self.ref.ref_game_state.player_game_states[0].connections)

    def test_execute_acquire_connection_move_cheating(self):
        SET_BLUE_CARDS = 0
        self.ref.ref_game_state.player_game_states[0].colored_cards[Color.BLUE] = SET_BLUE_CARDS
        self.assertEqual(len(self.ref.banned_player_indices), 0)
        self.ref.execute_acquire_connection_move(self.connection1)
        self.assertIn(0, self.ref.banned_player_indices)

    def test_execute_player_move_draw_cards(self):
        for key in self.ref.ref_game_state.player_game_states[0].colored_cards.keys():
            self.ref.ref_game_state.player_game_states[0].colored_cards[key] = 0
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].get_number_of_colored_cards(), 0)
        self.ref.execute_active_player_move()
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].connections, set())
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].get_number_of_colored_cards(), self.DRAW_NUM)
        self.assertEqual(self.ref.ref_game_state.player_game_states[0].rails, self.INITIAL_RAIL_COUNT)

    def test_execute_player_cheating(self):
        bad_move = PlayerMove()
        bad_move.move_type = 30
        bad_player = MockConfigurablePlayer("cheater", 12, bad_move)
        players = [bad_player, self.p1]
        ref = Referee(self.test_map, players)
        ref.set_up_game_states()
        ref.players_pick_destinations()
        self.assertEqual(len(ref.banned_player_indices), 0)
        ref.execute_active_player_move()
        self.assertIn(0, ref.banned_player_indices)

    def test_all_last_turns_taken_false(self):
        self.assertFalse(self.ref.all_last_turns_taken())

    def test_all_last_turns_taken_true(self):
        self.ref.took_last_turn = self.players
        self.assertTrue(self.ref.all_last_turns_taken())

    def test_get_connection_score(self):
        self.ref.ref_game_state.player_game_states[0].connections.add(self.connection1)
        self.ref.ref_game_state.player_game_states[0].connections.add(self.connection2)
        score = self.ref.get_connection_score(self.ref.ref_game_state.player_game_states[0], self.RAIL_SEGMENT_POINT_VALUE)
        exp_score = self.connection1.length + self.connection2.length
        self.assertEqual(score, exp_score)

    def test_get_connection_score_zero(self):
        score = self.ref.get_connection_score(self.ref.ref_game_state.player_game_states[0], self.RAIL_SEGMENT_POINT_VALUE)
        exp_score = 0
        self.assertEqual(score, exp_score)

    def test_get_destination_score_completed_two(self):
        self.ref.players_pick_destinations()
        self.ref.ref_game_state.player_game_states[0].connections.add(self.connection1)
        self.ref.ref_game_state.player_game_states[0].connections.add(self.connection5)
        dest1 = Destination({self.boston, self.new_york})
        dest2 = Destination({self.philadelphia, self.new_york})
        destinations = {dest1, dest2}
        self.ref.ref_game_state.player_game_states[0].destinations = destinations
        score = self.ref.get_destination_score(self.ref.ref_game_state.player_game_states[0], self.DESTINATION_COMPLETE_VALUE)
        exp_score = self.DESTINATION_COMPLETE_VALUE + self.DESTINATION_COMPLETE_VALUE
        self.assertEqual(score, exp_score)

    def test_get_destination_score_completed_one(self):
        self.ref.ref_game_state.player_game_states[0].connections.add(self.connection1)
        dest1 = Destination({self.boston, self.new_york})
        dest2 = Destination({self.philadelphia, self.new_york})
        destinations = {dest1, dest2}
        self.ref.ref_game_state.player_game_states[0].destinations = destinations
        score = self.ref.get_destination_score(self.ref.ref_game_state.player_game_states[0], self.DESTINATION_COMPLETE_VALUE)
        exp_score = self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        self.assertEqual(score, exp_score)

    def test_get_destination_score_completed_zero(self):
        self.ref.players_pick_destinations()
        score = self.ref.get_destination_score(self.ref.ref_game_state.player_game_states[0], self.DESTINATION_COMPLETE_VALUE)
        exp_score = -self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        self.assertEqual(score, exp_score)

    def test_score_game_for_player_has_longest_path(self):
        self.ref.ref_game_state.player_game_states[0].connections.add(self.connection1)
        dest1 = Destination({self.boston, self.philadelphia})
        dest2 = Destination({self.austin, self.boston})
        destinations = {dest1, dest2}
        self.ref.ref_game_state.player_game_states[0].destinations = destinations
        has_longest_path = True
        score = self.ref.score_game_for_player(0, has_longest_path)
        exp_score = self.connection1.length + self.LONGEST_CONTINUOUS_PATH_VALUE - self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        self.assertEqual(score, exp_score)
    
    def test_score_game_for_player_does_not_have_longest_path(self):
        self.ref.ref_game_state.player_game_states[0].connections.add(self.connection1)
        dest1 = Destination({self.boston, self.philadelphia})
        dest2 = Destination({self.austin, self.boston})
        destinations = {dest1, dest2}
        self.ref.ref_game_state.player_game_states[0].destinations = destinations
        has_longest_path = False
        score = self.ref.score_game_for_player(0, has_longest_path)
        exp_score = self.connection1.length - self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        self.assertEqual(score, exp_score)

    def test_score_game(self):
        self.ref.ref_game_state.player_game_states[0].connections.add(self.connection1)
        self.ref.players_pick_destinations()
        dest1 = Destination({self.boston, self.new_york})
        dest2 = Destination({self.austin, self.boston})
        destinations = {dest1, dest2}
        self.ref.ref_game_state.player_game_states[0].destinations = destinations
        scores = self.ref.score_game()
        exp_score1 = self.connection1.length + self.LONGEST_CONTINUOUS_PATH_VALUE + self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        exp_score2 = -self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        exp_score3 = -self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        exp_scores = [exp_score1, exp_score2, exp_score3]
        self.assertEqual(scores, exp_scores)

    def test_score_game_banned_player(self):
        self.ref.players_pick_destinations()
        self.ref.ref_game_state.player_game_states[0].connections.add(self.connection1)
        dest1 = Destination({self.boston, self.new_york})
        dest2 = Destination({self.austin, self.boston})
        destinations = {dest1, dest2}
        self.ref.ref_game_state.player_game_states[0].destinations = destinations
        self.ref.boot_player(1, "cheating")
        scores = self.ref.score_game()
        exp_score1 = self.connection1.length + self.LONGEST_CONTINUOUS_PATH_VALUE + self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        exp_score2 = self.BANNED_PLAYER_SCORE_REPRESENTATION
        exp_score3 = -self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        exp_scores = [exp_score1, exp_score2, exp_score3]
        self.assertEqual(scores, exp_scores)

    def test_longest_path(self):
        self.ref.ref_game_state.player_game_states[0].connections = frozenset({self.connection1, self.connection5})
        self.assertEqual(self.ref.find_longest_continuous_path_for_player(0), 7)

    def test_longest_path_complex(self):
        self.ref.ref_game_state.player_game_states[0].connections = frozenset({self.connection1, self.connection2, self.connection3, \
            self.connection4, self.connection5, self.connection6, self.connection7, self.connection8, self.connection9, \
                self.connection10, self.connection11, self.connection12})
        self.assertEqual(self.ref.find_longest_continuous_path_for_player(0), 12)

    def test_longest_path_disjoint(self):
        self.ref.ref_game_state.player_game_states[0].connections = frozenset({self.connection1, self.connection12})
        self.assertEqual(self.ref.find_longest_continuous_path_for_player(0), 5)

    def test_longest_path_no_connections(self):
        self.assertEqual(self.ref.find_longest_continuous_path_for_player(0), 0)

    def test_get_active_player_first_turn(self):
        self.assertEqual(self.players[0], self.ref.get_active_player())

    def test_get_active_player_next_turn(self):
        self.ref.ref_game_state.next_turn()
        self.assertEqual(self.players[1], self.ref.get_active_player())

    def test_get_active_player_wrap_around(self):
        self.assertEqual(self.players[0], self.ref.get_active_player())    

    def test_notify_players(self):
        move = PlayerMove()
        move.move_type = 2
        winning_player = MockConfigurablePlayer("winner", 12, move)
        losing_player = MockConfigurablePlayer("loser", 12, move)
        players = [winning_player, losing_player]
        ref = Referee(self.test_map, players)
        scores = [10, 0]
        ref.notify_players(scores)
        self.assertTrue(winning_player.is_winner)
        self.assertFalse(losing_player.is_winner)

    def test_notify_players_tie(self):
        move = PlayerMove()
        move.move_type = 2
        tie_player1 = MockConfigurablePlayer("tie1", 12, move)
        tie_player2 = MockConfigurablePlayer("tie2", 12, move)
        losing_player = MockConfigurablePlayer("loser", 12, move)
        players = [tie_player1, tie_player2, losing_player]
        ref = Referee(self.test_map, players)
        scores = [10, 10, 0]
        ref.notify_players(scores)
        self.assertTrue(tie_player1.is_winner)
        self.assertTrue(tie_player2.is_winner)
        self.assertFalse(losing_player.is_winner)
    
    def test_get_banned_players(self):
        self.ref.get_banned_players()
        self.assertEqual(len(self.ref.get_banned_players()), 0)
        
        self.ref.boot_player(1, "Testing player2 getting booted.")
        self.assertEqual(len(self.ref.get_banned_players()), 1)
        self.assertEqual(self.ref.get_banned_players()[0], self.p2)

        self.ref.boot_player(0, "Testing player1 getting booted.")
        self.assertEqual(len(self.ref.get_banned_players()), 2)
        self.assertEqual(self.ref.get_banned_players()[0], self.p1)
        self.assertEqual(self.ref.get_banned_players()[1], self.p2)

    def test_get_ranking_of_players(self):
        move = PlayerMove()
        move.move_type = 2
        tie_player1 = MockConfigurablePlayer("tie1", 12, move)
        tie_player2 = MockConfigurablePlayer("tie2", 12, move)
        losing_player = MockConfigurablePlayer("loser", 12, move)
        players = [tie_player1, tie_player2, losing_player]
        ref = Referee(self.test_map, players)
        scores = [10, 10, 0]
        rankings = ref.get_ranking_of_players(scores)
        exp_rankings = [[(tie_player1, 10), (tie_player2, 10)], [(losing_player, 0)]]
        self.assertEqual(rankings, exp_rankings)

    def test_get_ranking_of_players_banned_player(self):
        move = PlayerMove()
        move.move_type = 2
        tie_player1 = MockConfigurablePlayer("tie1", 12, move)
        tie_player2 = MockConfigurablePlayer("tie2", 12, move)
        losing_player = MockConfigurablePlayer("loser", 12, move)
        banned_player = MockConfigurablePlayer("cheater", 7, move)
        players = [tie_player1, tie_player2, losing_player, banned_player]
        ref = Referee(self.test_map, players)
        scores = [10, 10, -10, self.BANNED_PLAYER_SCORE_REPRESENTATION]
        rankings = ref.get_ranking_of_players(scores)
        exp_rankings = [[(tie_player1, 10), (tie_player2, 10)], [(losing_player, -10)]]
        self.assertEqual(rankings, exp_rankings)

class TestRefereeIntegrationTests(unittest.TestCase):
    
    def setUp(self):
        # Create map
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 90, 10)
        self.wdc = City("Washington D.C.", 55, 60)
        self.boise = City("Boise", 30, 50)
        self.connection1 = Connection(frozenset({self.boston, self.new_york}), Color.BLUE, 3)
        self.connection2 = Connection(frozenset({self.philadelphia, self.new_york}), Color.RED, 4)
        self.connection3 = Connection(frozenset({self.boston, self.wdc}), Color.BLUE, 5)
        self.connection4 = Connection(frozenset({self.philadelphia, self.wdc}), Color.WHITE, 5)
        self.connection5 = Connection(frozenset({self.boise, self.wdc}), Color.GREEN, 5)
        self.cities = {self.boston, self.new_york, self.philadelphia, self.wdc, self.boise}
        self.connections = {self.connection1, self.connection2, self.connection3, self.connection4, self.connection5}
        self.height = 800
        self.width = 800
        self.test_map = Map(self.cities, self.connections, self.height, self.width)

        # Create mock players that always draw cards - this means they will tie
        # The buy now player will always win if they are in the game because the 
        # draw_playerX players are mock players that only draw (never acquire connections)
        draw = PlayerMove()
        draw.move_type = MoveType.DRAW_CARDS
        self.draw_player1 = MockConfigurablePlayer("player1", 12, draw)
        self.draw_player2 = MockConfigurablePlayer("player2", 15, draw)
        self.h10_player = Hold_10_Player("holder", 18)
        self.bn_player = MockBuyNowPlayer("buyer", 20)
        bad_move = BadMove()
        self.bad_player = MockConfigurablePlayer("always draw", 12, bad_move)

        # The deck has 12 red cards
        self.red_deck = deque([Color.RED, Color.RED, Color.RED, Color.RED, Color.RED, Color.RED, \
            Color.RED, Color.RED, Color.RED, Color.RED, Color.RED, Color.RED])

    def test_play_game_all_players_booted_on_setup(self):
        num_players = 2
        players = []
        for pi in range(num_players):
            players.insert(0, MockBadSetUpPlayer(f"player{pi}", {pi}))
        ref = Referee(self.test_map, players, self.red_deck)
        rankings = ref.play_game()

        for player_index in range(len(rankings[1])):
            self.assertEqual(rankings[1][player_index].name, f"player{player_index}")

    def test_play_game_all_players_booted_on_pick(self):
        # TODO: Create mock player with good set up but bad pick of destinations.
        num_players = 2
        players = []
        for pi in range(num_players):
            players.insert(0, MockBadPickPlayer(f"player{pi}", {pi}))
        ref = Referee(self.test_map, players, self.red_deck)
        rankings = ref.play_game()

        for player_index in range(len(rankings[1])):
            self.assertEqual(rankings[1][player_index].name, f"player{player_index}")

    def test_play_game_tie(self):
        players = [self.draw_player1, self.draw_player2]
        ref = Referee(self.test_map, players, self.red_deck)
        rankings, banned_list = ref.play_game()
        for player in players:
            self.assertTrue(player.is_winner)
            self.assertFalse(player.booted)
        # The expected scores are 0 instead of -20 because both player's have
        # no connections, so they tie for the longest path and are both awarded points
        exp_rankings = [[(self.draw_player1, 0), (self.draw_player2, 0)]]
        self.assertEqual(rankings, exp_rankings)
        self.assertEqual(banned_list, [])
            
    def test_play_game_no_tie(self):
        players = [self.bn_player, self.draw_player1]
        ref = Referee(self.test_map, players, self.red_deck)
        rankings, banned_list = ref.play_game()
        self.assertFalse(self.draw_player1.is_winner)
        self.assertFalse(self.draw_player1.booted)
        self.assertTrue(self.bn_player.is_winner)
        self.assertFalse(self.bn_player.booted)
        check_dest = Destination({self.philadelphia, self.new_york})
        # Expected score is 4 or 24 depending on whether or not the buy now
        # player selected a destination containing the cities in connection2
        # which is the only acquireable connection with the given deck
        if check_dest in self.bn_player.game_state.destinations:
            exp_winner_score = 24
        else:
            exp_winner_score = 4
        exp_rankings = [[(self.bn_player, exp_winner_score)], [(self.draw_player1, -20)]]
        self.assertEqual(rankings, exp_rankings)
        self.assertEqual(banned_list, [])

    def test_play_game_h10_buy_now(self):
        players = [self.bn_player, self.h10_player]
        ref = Referee(self.test_map, players, self.red_deck)
        rankings, banned_players = ref.play_game()

        for rank_index in range(len(rankings)):
            rank = rankings[rank_index]
            self.assertEqual(len(rank), 1)
            if rank_index == 0:
                self.assertEqual(rank[0][0], self.bn_player)
            else:
                self.assertEqual(rank[0][0], self.h10_player)
        self.assertEqual(len(banned_players), 0)           

    def test_play_game_with_cheater(self):
        players = [self.bn_player, self.bad_player]
        ref = Referee(self.test_map, players, self.red_deck)
        rankings, banned_list = ref.play_game()
        self.assertFalse(self.bad_player.is_winner)
        self.assertTrue(self.bad_player.booted)
        self.assertTrue(self.bn_player.is_winner)
        self.assertFalse(self.bn_player.booted)
        # Expected score is 4 or 24 depending on whether or not the buy now
        # player selected a destination containing the cities in connection2
        # which is the only acquireable connection with the given deck
        exp_winner_score = 4
        check_dest = Destination({self.philadelphia, self.new_york})
        # If the player has the destination, then destination points cancel out
        if check_dest in self.bn_player.game_state.destinations:
            exp_winner_score = 24
        exp_rankings = [[(self.bn_player, exp_winner_score)]]
        exp_banned = [self.bad_player]
        self.assertEqual(rankings, exp_rankings)
        self.assertIn(self.bad_player, ref.get_banned_players())
        self.assertEqual(banned_list, exp_banned)

    def test_play_game_no_tie_with_cheater(self):
        players = [self.bn_player, self.draw_player1, self.bad_player]
        ref = Referee(self.test_map, players, self.red_deck)
        rankings, banned_list = ref.play_game()
        self.assertFalse(self.draw_player1.is_winner)
        self.assertFalse(self.draw_player1.booted)
        self.assertTrue(self.bn_player.is_winner)
        self.assertFalse(self.bn_player.booted)
        self.assertFalse(self.bad_player.is_winner)
        self.assertTrue(self.bad_player.booted)
        check_dest = Destination({self.philadelphia, self.new_york})
        if check_dest in self.bn_player.game_state.destinations:
            exp_winner_score = 24
        else:
            exp_winner_score = 4
        exp_rankings = [[(self.bn_player, exp_winner_score)], [(self.draw_player1, -20)]]
        exp_banned = [self.bad_player]
        self.assertEqual(rankings, exp_rankings)
        self.assertIn(self.bad_player, ref.get_banned_players())
        self.assertEqual(banned_list, exp_banned)

    def test_play_game_all_players_booted_on_play(self):
        """Tests a scenario of all players being kicked on play"""
        players = [self.bad_player, self.bad_player]# self.bad_player, self.bad_player]
                   #self.bad_player, self.bad_player, self.bad_player, self.bad_player]
        ref = Referee(self.test_map, players, self.red_deck)
        rankings, banned_list = ref.play_game()
        for player in players:
            self.assertFalse(player.is_winner)
            self.assertTrue(player.booted)
        self.assertEqual(len(banned_list), 2)
        self.assertEqual(rankings, [])



if __name__ == '__main__':
    unittest.main()
