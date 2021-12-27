from collections import deque
from copy import deepcopy
import sys, json, unittest

sys.path.append('../../../')
from Trains.Admin.referee import NotEnoughDestinations
from Trains.Common.map import City, Color, Connection
from Trains.Admin.manager import Manager
from Trains.Other.Mocks.mock_tournament_player import MockTournamentCheaterEnd, MockTournamentCheaterStart, MockTournamentPlayer, MockTournamentPlayerNoMap
from Trains.Other.Mocks.configurable_manager import ConfigurableManager
from Trains.Player.moves import AcquireConnectionMove, DrawCardMove
from Trains.Player.buy_now import Buy_Now
from Trains.Other.Util.json_utils import convert_json_map_to_data_map
from Trains.Player.buy_now_player import Buy_Now_Player
from Trains.Player.hold_10_player import Hold_10_Player


class TestManager(unittest.TestCase):

    def setUp(self):
        # Initialize a list of players
        self.draw_players = []
        self.num_draw_players = 20
        for i in range(self.num_draw_players):
            self.draw_players.append(MockTournamentPlayer(f"player{i}", i, DrawCardMove()))
        
        self.hold_10_players = []
        self.num_hold_10_players = 10
        for i in range(self.num_hold_10_players):
            self.hold_10_players.append(MockTournamentPlayer(f"hold_player{i}", i))

        self.h10_player = Hold_10_Player("hold10 guy", 25)
        self.bn_player = Buy_Now_Player("buynow guy", 40)

        default_game_map_file_path = "../../../Trains/Other/Examples/Maps/default_map1.json"
        with open(default_game_map_file_path) as default_map_file:
            default_map_json = json.load(default_map_file)
            self.default_game_map = convert_json_map_to_data_map(default_map_json)
        
        invalid_map_file_path = "../../../Trains/Other/Examples/Maps/example_map1.json"
        with open(invalid_map_file_path) as invalid_map_file:
            invalid_map_json = json.load(invalid_map_file)
            self.invalid_game_map = convert_json_map_to_data_map(invalid_map_json)

    def create_red_deck(self, num_cards):
        red_deck = deque()
        for _ in range(num_cards):
            red_deck.append(Color.RED)
        return red_deck

    def test_constructor(self):
        manager = Manager(self.draw_players)
        # All 20 players suggest the same map, so the length of suggested_maps should be 1
        self.assertEqual(manager.active_players, self.draw_players)
        self.assertEqual(manager.banned_players, [])
        self.assertEqual(manager.tournament_map, None)

    def test_constructor_invalid_players_not_a_list(self):
        with self.assertRaises(ValueError):
            manager = Manager(set(self.draw_players))

    def test_constructor_invalid_not_enough_players(self):
        with self.assertRaises(ValueError):
            manager = Manager(self.draw_players[0])

    def test_setup_tournament(self):
        players = self.draw_players
        players.append(MockTournamentPlayer("map guy", 20, DrawCardMove, "../../../Trains/Other/Examples/Maps/default_map1.json"))
        manager = Manager(players)
        suggested_maps = manager.get_player_maps()
        # Load expected maps for assertion
        exp_game_map_file_path1 = "../../../Trains/Other/Examples/Maps/example_map1.json"
        with open(exp_game_map_file_path1) as exp_map_file1:
            exp_json_game_map1 = json.load(exp_map_file1)
            exp_game_map1 = convert_json_map_to_data_map(exp_json_game_map1)
        exp_game_map_file_path2 = "../../../Trains/Other/Examples/Maps/default_map1.json"
        with open(exp_game_map_file_path2) as exp_map_file2:
            exp_json_game_map2 = json.load(exp_map_file2)
            exp_game_map2 = convert_json_map_to_data_map(exp_json_game_map2)
        exp_suggested_maps = [exp_game_map1, exp_game_map2]
        self.assertEqual(suggested_maps, exp_suggested_maps)

    def test_setup_tournament_duplicate_map_suggested(self):
        manager = Manager(self.draw_players)
        suggested_maps = manager.get_player_maps()
        # Load expected map for assertion
        exp_game_map_file_path = "../../../Trains/Other/Examples/Maps/example_map1.json"
        with open(exp_game_map_file_path) as exp_map_file:
            exp_json_game_map = json.load(exp_map_file)
            exp_game_map = convert_json_map_to_data_map(exp_json_game_map)
        exp_suggested_maps = [exp_game_map]
        self.assertEqual(suggested_maps, exp_suggested_maps)
    
    def test_setup_tournament_no_maps_suggested(self):
        no_map_players = []
        for i in range(self.num_draw_players):
            no_map_players.append(MockTournamentPlayerNoMap(f"player{i}", i, DrawCardMove()))
        manager = Manager(no_map_players)
        suggested_maps = manager.get_player_maps()
        exp_suggested_maps = []
        self.assertEqual(suggested_maps, exp_suggested_maps)

    def test_verify_suggested_map_true_max_players(self):
        valid_map = "../../../Trains/Other/Examples/Maps/default_map1.json"
        with open(valid_map) as map_file:
            json_map = json.load(map_file)
            valid_game_map = convert_json_map_to_data_map(json_map)
        manager = Manager(self.draw_players)
        self.assertTrue(manager.verify_suggested_map(valid_game_map, 8))

    def test_verify_suggested_map_false_not_enough_destinations(self):
        invalid_map = "../../../Trains/Other/Examples/Maps/example_map1.json"
        with open(invalid_map) as map_file:
            json_map = json.load(map_file)
            invalid_game_map = convert_json_map_to_data_map(json_map)
        manager = Manager(self.draw_players)
        self.assertFalse(manager.verify_suggested_map(invalid_game_map, 2))

    def test_assign_players_to_games_exactly_max_players_in_one_game(self):
        manager = Manager(self.draw_players[0:8])
        game_assignments = manager.assign_players_to_games()
        exp_game_assignments = [self.draw_players[0:8]]
        for exp_assignment in exp_game_assignments:
            exp_assignment.sort(key=lambda p: p.age, reverse=True)
        self.assertEqual(len(game_assignments), 1)
        self.assertEqual(len(game_assignments[0]), 8)
        self.assertEqual(game_assignments, exp_game_assignments)

    def test_assign_players_to_games_less_than_max_players_in_one_game(self):
        manager = Manager(self.draw_players[0:5])
        game_assignments = manager.assign_players_to_games()
        exp_game_assignments = [self.draw_players[0:5]]
        for exp_assignment in exp_game_assignments:
            exp_assignment.sort(key=lambda p: p.age, reverse=True)
        self.assertEqual(len(game_assignments), 1)
        self.assertEqual(len(game_assignments[0]), 5)
        self.assertEqual(game_assignments, exp_game_assignments)

    def test_assign_players_to_games_more_than_max_players_in_one_game(self):
        manager = Manager(self.draw_players[0:10])
        game_assignments = manager.assign_players_to_games()
        exp_game_assignments = [self.draw_players[0:8], self.draw_players[8:10]]
        for exp_assignment in exp_game_assignments:
            exp_assignment.sort(key=lambda p: p.age, reverse=True)
        self.assertEqual(len(game_assignments), 2)
        self.assertEqual(len(game_assignments[0]), 8)
        self.assertEqual(len(game_assignments[1]), 2)
        self.assertEqual(game_assignments, exp_game_assignments)

    def test_assign_players_to_games_multiple_full_games(self):
        players = self.draw_players
        for i in range(4):
            players.append(MockTournamentPlayer(f"filler{i}", i, DrawCardMove()))

        manager = Manager(players)
        game_assignments = manager.assign_players_to_games()
        exp_game_assignments = [self.draw_players[0:8], self.draw_players[8:16], \
            self.draw_players[16:24]]
        for exp_assignment in exp_game_assignments:
            exp_assignment.sort(key=lambda p: p.age, reverse=True)

        self.assertEqual(len(game_assignments), 3)
        self.assertEqual(len(game_assignments[0]), 8)
        self.assertEqual(len(game_assignments[1]), 8)
        self.assertEqual(len(game_assignments[2]), 8)
        self.assertEqual(game_assignments, exp_game_assignments)

    def test_assign_players_to_games_need_to_backtrack_assignment(self):
        # The max number of players in a game is 8 and the minimum is 2, so the
        # backtrack scenario is when there are 9 players in a tournament
        manager = Manager(self.draw_players[0:9])
        game_assignments = manager.assign_players_to_games()

        exp_game_assignments = [self.draw_players[0:8]]
        for exp_assignment in exp_game_assignments:
            exp_assignment.sort(key=lambda p: p.age, reverse=True)
        last_assigned = exp_game_assignments[0].pop(7)
        exp_game_assignments.append([self.draw_players[8], last_assigned])

        self.assertEqual(len(game_assignments), 2)
        self.assertEqual(len(game_assignments[0]), 7)
        self.assertEqual(len(game_assignments[1]), 2)
        self.assertEqual(game_assignments, exp_game_assignments)

    def test_get_valid_map_no_valid_player_maps(self):
        # All suggested player maps do not have enough destinations.
        manager = Manager(self.draw_players[0:8])
        # All draw players in list would give this map, yielding the same list in manager.
        self.assertRaises(NotEnoughDestinations, manager.get_valid_map, 8, [self.invalid_game_map])

    def test_get_valid_map(self):
        manager = Manager(self.draw_players)
        valid_map = "../../../Trains/Other/Examples/Maps/one_red_connection_map.json"
        with open(valid_map) as map_file:
            json_map = json.load(map_file)
            valid_game_map = convert_json_map_to_data_map(json_map)
        # Give the manager a valid game map
        self.assertEqual(manager.get_valid_map(8, [valid_game_map]), valid_game_map)

    def test_eliminate_losing_players(self):
        manager = Manager(self.draw_players)
        first = []
        second = []
        third = []
        # Create the rankings to test with
        for i in range(len(self.draw_players)):
            if i < 5:
                first.append((self.draw_players[i], 0))
            elif i < 10:
                second.append((self.draw_players[i], 0))
            else:
                third.append((self.draw_players[i], 0))
        rankings = [first, second, third]
        for rank in rankings:
            rank.sort(key=lambda ps: ps[0].name)
        # Get the losing ranks
        losing_player_rankings = rankings[1:]

        self.assertEqual(manager.active_players, self.draw_players)
        manager.eliminate_losing_players(losing_player_rankings)

        # Should only be 5 players remaining
        self.assertEqual(len(manager.active_players), 5)
        exp_active_players = []
        for player_results in first:
            exp_active_players.append(player_results[0])
        self.assertEqual(manager.active_players, exp_active_players)

    def test_eliminate_losing_players_none_eliminated(self):
        manager = Manager(self.draw_players)
        losing_player_rankings = []

        self.assertEqual(len(manager.active_players), len(self.draw_players))
        self.assertEqual(manager.active_players, self.draw_players)
        manager.eliminate_losing_players(losing_player_rankings)
        # All players should still be active
        self.assertEqual(len(manager.active_players), len(self.draw_players))
        self.assertEqual(manager.active_players, self.draw_players)

    def test_run_tournament_round(self):
        players = deepcopy(self.draw_players)
        winner_of_round = Hold_10_Player("winner_of_round", 50)
        players.append(winner_of_round)
        bogus_connection = Connection(frozenset({City("Nowhere", 50, 50), City("The Void", 100, 100)}), Color.BLUE, 4)
        cheater = MockTournamentPlayer("cheater", 999, AcquireConnectionMove(bogus_connection))
        players.append(cheater)
        manager = ConfigurableManager(players, self.create_red_deck(70), True)

        self.assertEqual(len(manager.active_players), len(players))
        self.assertEqual(len(manager.eliminated_players), 0)
        self.assertEqual(len(manager.banned_players), 0)

        assignments = manager.assign_players_to_games()
        manager.run_tournament_round(assignments)

        self.assertEqual(len(manager.active_players), 17)
        self.assertIn(winner_of_round, manager.active_players)
        for player in manager.active_players:
            self.assertNotIn(player, manager.eliminated_players)
            self.assertNotIn(player, manager.banned_players)
        self.assertNotIn(cheater, manager.active_players)
        self.assertEqual(len(manager.banned_players), 1)
        self.assertIn(cheater, manager.banned_players)
        self.assertEqual(len(manager.eliminated_players), 4)
        for player in manager.eliminated_players:
            self.assertNotIn(player, manager.active_players)
            self.assertNotIn(player, manager.banned_players)
        self.assertNotIn(winner_of_round, manager.eliminated_players)
        self.assertNotIn(cheater, manager.eliminated_players)

    def test_boot_player(self):
        manager = Manager(deepcopy(self.draw_players))
        self.assertEqual(len(manager.active_players), len(self.draw_players))
        self.assertEqual(len(manager.banned_players), 0)
        manager.boot_player(manager.active_players[0])
        self.assertEqual(len(manager.banned_players), 1)
        self.assertIn(self.draw_players[0].name, [player.name for player in manager.banned_players])
        self.assertEqual(len(manager.active_players), len(self.draw_players))

    def test_remove_banned_players_from_active(self):
        manager = Manager(deepcopy(self.draw_players))
        self.assertEqual(len(manager.active_players), len(self.draw_players))
        self.assertEqual(len(manager.banned_players), 0)
        
        manager.boot_player(manager.active_players[0])
        self.assertEqual(len(manager.banned_players), 1)
        self.assertIn(self.draw_players[0].name, [player.name for player in manager.banned_players])
        self.assertEqual(len(manager.active_players), len(self.draw_players))

        manager.remove_banned_players_from_active()
        self.assertEqual(len(manager.banned_players), 1)
        self.assertIn(self.draw_players[0].name, [player.name for player in manager.banned_players])
        self.assertEqual(len(manager.active_players), len(self.draw_players) - 1)
        self.assertNotIn(self.draw_players[0].name, [player.name for player in manager.active_players])

    def test_call_player_method_invalid_end(self):
        players = deepcopy(self.draw_players)
        cheater = MockTournamentCheaterEnd("cheater", 66)
        players.append(cheater)
        manager = Manager(players)
        
        self.assertEqual(len(manager.banned_players), 0)

        manager.call_player_method(cheater, cheater.end, False)
        self.assertEqual(len(manager.banned_players), 1)
        self.assertIn(cheater, manager.banned_players)

    def test_call_player_method_valid_end(self):
        players = deepcopy(self.draw_players)
        valid_player = MockTournamentPlayer("valid", 66)
        players.append(valid_player)
        manager = Manager(players)
        
        self.assertEqual(len(manager.active_players), len(self.draw_players) + 1)
        self.assertEqual(len(manager.banned_players), 0)

        manager.call_player_method(valid_player, valid_player.end, False)
        self.assertEqual(len(manager.active_players), len(self.draw_players) + 1)
        self.assertIn(valid_player, manager.active_players)
        self.assertEqual(len(manager.banned_players), 0)

    def test_notify_players(self):
        players = deepcopy(self.draw_players[:7])
        bn_player = MockTournamentPlayer("winner", 50, strategy=Buy_Now())
        players.append(bn_player)
        manager = ConfigurableManager(players, self.create_red_deck(40), True)

        game_assignments = manager.assign_players_to_games()
        manager.run_tournament_round(game_assignments)

        manager.notify_players_with_results()
        for player in manager.active_players:
            self.assertTrue(player.is_tournament_winner)

    def test_run_tournament_all_players_booted_at_start(self):
        players = []
        num_players = 10
        for i in range(num_players):
            players.append(MockTournamentCheaterStart(f"player{i}", i))
        manager = Manager(players)
        self.assertEqual(len(manager.banned_players), num_players)
        manager.run_tournament()
        self.assertEqual(len(manager.banned_players), num_players)

    def test_run_tournament_all_players_booted_during_game(self):
        players = []
        num_players = 10
        for i in range(num_players):
            bogus_connection = Connection(frozenset({City("Nowhere", 50, 50), City("The Void", 100, 100)}), Color.BLUE, 4)
            cheater = MockTournamentPlayer("cheater", 999, AcquireConnectionMove(bogus_connection))
            players.append(cheater)
        manager = ConfigurableManager(players, self.create_red_deck(40), True)

        self.assertEqual(len(manager.active_players), num_players)
        self.assertEqual(len(manager.banned_players), 0)

        winners, cheaters = manager.run_tournament()

        self.assertEqual(len(cheaters), num_players)
        self.assertEqual(len(winners), 0)

        # Check that players were not notified of winning/losing tournament
        for player in manager.banned_players:
            self.assertIsNone(player.is_tournament_winner)

    def test_run_tournament_ends_no_state_change(self):
        manager = ConfigurableManager(self.draw_players[0:10], self.create_red_deck(40), True)
        winners, banned = manager.run_tournament()
        exp_winners = self.draw_players[0:10]
        exp_banned = []
        self.assertEqual(winners, exp_winners)
        self.assertEqual(banned, exp_banned)

    def test_run_tournament_one_winner_no_bans(self):
        players = self.hold_10_players
        exp_winner = MockTournamentPlayer("winner", 35, game_map_file_path="../../../Trains/Other/Examples/Maps/one_red_connection_map.json",
        strategy=Buy_Now())
        players.append(exp_winner)
        manager = ConfigurableManager(players, self.create_red_deck(40), True)
        winners, banned = manager.run_tournament()
        exp_winners = [exp_winner]
        exp_banned = []
        self.assertEqual(winners, exp_winners)
        self.assertEqual(banned, exp_banned)
        for player in players:
            if player not in winners:
                self.assertFalse(player.is_tournament_winner)
            else:
                self.assertTrue(player.is_tournament_winner)

    def test_run_tournament_tie_all_players_booted_at_end(self):
        players = []
        num_players = 10
        for i in range(num_players):
            players.append(MockTournamentCheaterEnd(f"player{i}", i, DrawCardMove()))
        manager = ConfigurableManager(players, self.create_red_deck(40), True)
        
        self.assertEqual(len(manager.active_players), num_players)
        self.assertEqual(len(manager.eliminated_players), 0)
        self.assertEqual(len(manager.banned_players), 0)

        manager.run_tournament()

        self.assertEqual(len(manager.active_players), num_players)
        self.assertEqual(len(manager.eliminated_players), 0)
        self.assertEqual(len(manager.banned_players), num_players)

if __name__ == '__main__':
    unittest.main()
