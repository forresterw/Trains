import unittest
import json, sys
from jsonschema import validate

sys.path.append('../../../')
from Trains.Other.Util.json_utils import seperate_json_inputs, convert_json_map_to_data_map, \
    convert_from_card_plus_to_json, convert_card_star_to_json, convert_from_json_to_playermove
from Trains.Common.player_game_state import PlayerGameState
from Trains.Common.map import Connection, City, Destination, Color, Map
from Trains.Player.buy_now_player import Buy_Now_Player
from Trains.Player.hold_10_player import Hold_10_Player
from Trains.Admin.referee import Referee, Cheating, NotEnoughDestinations
from Trains.Player.moves import MoveType, DrawCardMove, PlayerMove, AcquireConnectionMove
from Trains.Other.Mocks.mock_move_player import MockConfigurablePlayer, MockBuyNowPlayer, BadMove
from Trains.Other.Mocks.mock_bad_setup_player import MockBadSetUpPlayer
from Trains.Other.Mocks.mock_bad_pick_player import MockBadPickPlayer


class TestRemoteJsonConversion(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        """Sets up a Map object"""
        self.atl = City("Atlanta", 600, 600)
        self.bismarck = City("Bismarck", 400, 100)
        self.dc = City("Washington, D.C.", 600, 500)
        self.ny = City("New York", 700, 400)
        self.boston = City("Boston", 800, 300)
        self.trenton = City("Trenton", 800, 500)
        self.seattle = City("Seattle", 100, 50)
        self.sacramento = City("Sacramento", 200, 500)
        self.austin = City("Austin", 400, 700)
        self.clt = City("Charlotte", 650, 500)
        self.atl_clt = Connection(frozenset([self.atl, self.clt]), Color.BLUE, 5)
        self.austin_dc_blue = Connection(frozenset([self.austin, self.dc]), Color.BLUE, 4)
        self.austin_dc_red = Connection(frozenset([self.austin, self.dc]), Color.RED, 4)
        self.austin_dc_green = Connection(frozenset([self.austin, self.dc]), Color.GREEN, 4)
        self.austin_dc_white = Connection(frozenset([self.austin, self.dc]), Color.WHITE, 4)
        self.bismarck_austin = Connection(frozenset([self.bismarck, self.austin]), Color.GREEN, 4)
        self.bismarck_boston = Connection(frozenset([self.bismarck, self.boston]), Color.WHITE, 5)
        self.bismarck_sacramento = Connection(frozenset([self.bismarck, self.sacramento]), Color.BLUE, 3)
        self.boston_ny_blue = Connection(frozenset([self.boston, self.ny]), Color.BLUE, 3)
        self.boston_ny_red = Connection(frozenset([self.boston, self.ny]), Color.RED, 3)
        self.boston_trenton = Connection(frozenset([self.boston, self.trenton]), Color.WHITE, 4)
        self.ny_trenton_red = Connection(frozenset([self.ny, self.trenton]), Color.RED, 3)
        self.ny_trenton_green = Connection(frozenset([self.ny, self.trenton]), Color.GREEN, 3)
        self.sacramento_seattle_blue = Connection(frozenset([self.sacramento, self.seattle]), Color.BLUE, 5)
        self.sacramento_seattle_red = Connection(frozenset([self.sacramento, self.seattle]), Color.RED, 5)
        self.sacramento_seattle_green = Connection(frozenset([self.sacramento, self.seattle]), Color.GREEN, 5)
        self.trenton_dc_green = Connection(frozenset([self.trenton, self.dc]), Color.GREEN, 3)
        self.trenton_dc_blue = Connection(frozenset([self.trenton, self.dc]), Color.BLUE, 3)

        self.cities = {self.austin, self.bismarck, self.boston, self.dc, self.ny, self.sacramento, self.seattle, self.trenton }

        self.connections = {self.austin_dc_blue, self.austin_dc_red, self.austin_dc_green, self.austin_dc_white, self.bismarck_austin,
                       self.bismarck_boston, self.bismarck_sacramento, self.boston_ny_blue, self.boston_ny_red, self.boston_trenton,
                       self.ny_trenton_red, self.ny_trenton_green, self.sacramento_seattle_blue, self.sacramento_seattle_red,
                       self.sacramento_seattle_green, self.trenton_dc_green, self.trenton_dc_blue}

        self.default_map1 = Map(self.cities, self.connections, 800, 800)
        self.chicago = City("Chicago", 400, 300)
        self.chi_ny = Connection(frozenset([self.chicago, self.ny]), Color.WHITE, 5)
        self.la = City("Los Angeles", 100, 600)
        self.sandiego = City("San Diego", 150, 650)
        self.la_sd = Connection(frozenset([self.la, self.sandiego]), Color.BLUE, 4)
        self.reno = City("Reno", 200, 500)
        self.sf = City("San Francisco", 100, 500)
        self.reno_sf = Connection(frozenset([self.reno, self.sf]), Color.RED, 3)
        self.portland = City("Portland",100, 200 )
        self.port_sea = Connection(frozenset([self.portland, self.seattle]), Color.BLUE, 4)
        self.port_sf = Connection(frozenset([self.portland, self.sf]), Color.GREEN, 5)
        self.jacksonville = City("Jacksonville", 600, 700)
        self.miami = City("Miami", 600, 800)
        self.jack_mia = Connection(frozenset([self.jacksonville, self.miami]), Color.BLUE, 3)
        self.neworleans = City("New Orleans", 500, 700)
        self.mia_no = Connection(frozenset([self.miami, self.neworleans]), Color.RED, 5)
        self.tampa = City("Tampa", 600, 750)
        self.miami_tamp = Connection(frozenset([self.miami, self.tampa]), Color.WHITE, 3)
        self.setup_player_state()

    def setup_player_state(self):

        connections = set([self.boston_ny_red, self.chi_ny])
        rails = 4
        color_cards = {Color.RED:0, Color.BLUE:4, Color.GREEN:0, Color.WHITE:0}
        austin_dc_destination = Destination([self.austin, self.dc])
        boston_ny_destination = Destination([self.boston, self.ny])
        destinations = set([austin_dc_destination, boston_ny_destination])
        game_info = {"unacquired_connections": [self.la_sd, self.reno_sf],
        "cards_in_deck": 75,
        "last_turn":False}
        opponent_info = [
            {
                "connections": [self.port_sea, self.port_sf

                ],
                "number_of_cards":10
            },
            {
                "connections": [self.jack_mia, self.mia_no, self.miami_tamp

                ],
                "number_of_cards":3
            }
        ]
        self.player_state = PlayerGameState(connections, color_cards, rails, destinations, game_info, opponent_info)


    def test_city_as_json(self):
        atl = City("Atlanta", 60, 60)
        self.assertEqual(atl.get_as_json(), ["Atlanta", [60, 60]])

    def test_city_as_json_malformed(self):
        atl = City("Atlanta", 60, 60)
        self.assertNotEqual(atl.get_as_json(), "Atlanta")

    def test_connection_as_acquired_as_json(self):
        atl = City("Atlanta", 60, 60)
        clt = City("Charlotte", 65, 50)
        atl_clt = Connection(frozenset([atl, clt]), Color.BLUE, 5)
        self.assertEqual(atl_clt.get_as_acquired_json(), ["Atlanta", "Charlotte", "blue", 5])

    def test_connection_as_acquired_as_json_malformed(self):
        atl = City("Atlanta", 60, 60)
        clt = City("Charlotte", 65, 50)
        atl_clt = Connection(frozenset([atl, clt]), Color.BLUE, 5)
        self.assertNotEqual(atl_clt.get_as_acquired_json(), ["Atlanta", "Charlotte", 5, "blue"])

    def test_connection_as_json(self):
        atl_clt_json = [["Atlanta", [600,600]], ["Charlotte", [650, 500]], "blue", 5]
        self.assertEqual(self.atl_clt.get_as_json(), atl_clt_json)

    def test_connection_as_json_malformed(self):
        atl_clt_json = ["Atlanta", "Charlotte", 5, "blue"]
        self.assertNotEqual(self.atl_clt.get_as_json(), atl_clt_json)

    def test_destination_as_json(self):
        la = City("Los Angeles", 15, 55)
        ny = City("New York", 70, 30)
        la_ny = Destination([la, ny])
        self.assertEqual(la_ny.get_as_json(), [["Los Angeles", [15,55]], ["New York", [70,30]]])

    def test_destination_as_json_malformed(self):
        la = City("Los Angeles", 15, 55)
        ny = City("New York", 70, 30)
        la_ny = Destination([la, ny])
        self.assertNotEqual(la_ny.get_as_json(), ["Los Angeles", "New York"])

    def test_destination_plus_as_json(self):
        atl_clt = Destination([self.atl, self.clt])
        bos_ny = Destination([self.boston, self.ny])
        expected = [[["Atlanta", [600, 600]], ["Charlotte", [650, 500]]],
                     [["Boston", [800, 300]], ["New York", [700, 400]]]]
        destination_plus_as_json = [atl_clt.get_as_json(), bos_ny.get_as_json()]
        self.assertEqual(destination_plus_as_json, expected)

    def test_destination_plus_as_json_malformed(self):
        atl_clt = Destination([self.atl, self.clt])
        bos_ny = Destination([self.boston, self.ny])
        expected = [["Atlanta", "Charlotte"],
                    ["Boston", "New York"]]
        destination_plus_as_json = [atl_clt.get_as_json(), bos_ny.get_as_json()]
        self.assertNotEqual(destination_plus_as_json, expected)

    def test_map_as_json(self):
        default_map_from_json_as_json = open("../../Examples/Maps/default_map1.json", 'r').read()
        default_map_from_json = json.loads(default_map_from_json_as_json)
        self.assertEqual(self.default_map1.get_as_json(),
                         default_map_from_json)

    def test_map_as_json_malformed(self):
        default_map_from_json_as_json = open("../../Examples/Maps/default_map1_malformed.json", 'r').read()
        default_map_from_json = json.loads(default_map_from_json_as_json)
        self.assertNotEqual(self.default_map1.get_as_json(),
                         default_map_from_json)

    def test_card_plus_as_json(self):
        expected_card_plus = ["blue", "red", "green", "green", "blue", "white"]
        actual_card_plus = [Color.BLUE, Color.RED, Color.GREEN, Color.GREEN, Color.BLUE, Color.WHITE]
        self.assertEqual(convert_from_card_plus_to_json(actual_card_plus), expected_card_plus)

    def test_card_star_as_json(self):
        expected_card_star = {"red": 4, "white": 10, "blue": 3, "green": 2}
        actual_card_star = {Color.RED: 4, Color.WHITE: 10, Color.BLUE: 3, Color.GREEN:2}
        self.assertEqual(convert_card_star_to_json(actual_card_star), expected_card_star)

    def test_convert_json_to_playermove_more(self):
        self.assertEqual(type(convert_from_json_to_playermove("more cards")), DrawCardMove)

    def test_convert_json_to_playermove_acquire_connection(self):
        self.assertEqual(type(convert_from_json_to_playermove(self.atl_clt.get_as_json())), AcquireConnectionMove)

if __name__ == '__main__':
    unittest.main()
