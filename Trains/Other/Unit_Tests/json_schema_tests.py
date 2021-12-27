import unittest
import json, sys
from jsonschema import validate, ValidationError

sys.path.append('../../../')

import Trains.Remote.messages.message_schemas as schemas


class TestRemoteJsonConversion(unittest.TestCase):

    def test_json_schema_destination(self):
        example_destinations_plus = [["Atlanta", [100, 300]], ["Boston", [400, 200]]]
        self.assertIsNone(validate(instance=example_destinations_plus, schema=schemas.DESTINATION_SCHEMA))

    def test_json_schema_destination_malformed(self):
        example_destinations_plus = ["Atlanta", "Boston"]
        with self.assertRaises(ValidationError):
            validate(instance=example_destinations_plus, schema=schemas.DESTINATION_SCHEMA)

    def test_json_schema_destination_plus(self):
        example_destinations_plus = [[["Atlanta", [100, 300]], ["Boston", [400, 200]]],
                                     [["Atlanta", [100, 300]], ["Charlotte", [20, 700]]]]
        self.assertIsNone(validate(instance=example_destinations_plus, schema=schemas.DESTINATION_PLUS_SCHEMA))
        print(schemas.DESTINATION_PLUS_SCHEMA)

    def test_json_schema_destination_plus_malformed(self):
        example_destinations_plus = [[["Atlanta", [100, 300]], ["Boston", [400, 200]]],
                                     [["Atlanta", [100, 300]], ["Charlotte", [20, 700]]],
                                     ["Dallas", "Houston"]]
        with self.assertRaises(ValidationError):
            validate(instance=example_destinations_plus, schema=schemas.DESTINATION_PLUS_SCHEMA)

    def test_json_schema_card_plus(self):
        example_card_plus = ["red", "white", "green", "blue", "blue", "red"]
        self.assertIsNone(validate(instance=example_card_plus, schema=schemas.CARD_PLUS_SCHEMA))

    def test_json_schema_card_plus_malformed(self):
        example_card_plus = ["red", "white", "green", "blue", "blue", "red", True]
        with self.assertRaises(ValidationError):
            validate(instance=example_card_plus, schema=schemas.CARD_PLUS_SCHEMA)

    def test_json_schema_map(self):
        default_map_from_json = json.loads(open("../../Examples/Maps/default_map1.json", 'r').read())
        self.assertIsNone(validate(instance=default_map_from_json, schema=schemas.MAP_SCHEMA))

    def test_json_schema_map_malformed(self):
        default_map_from_json = json.loads(open("../../Examples/Maps/default_map1_malformed.json", 'r').read())
        with self.assertRaises(ValidationError):
            validate(instance=default_map_from_json, schema=schemas.MAP_SCHEMA)

    def test_json_schema_city(self):
        example_city = ["Boston", [700, 200]]
        self.assertIsNone(validate(instance=example_city, schema=schemas.CITY_SCHEMA))

    def test_json_schema_city_malformed(self):
        example_city = ["Boston", 700, 200]
        with self.assertRaises(ValidationError):
            validate(instance=example_city, schema=schemas.CITY_SCHEMA)

    def test_json_schema_acquired(self):
        example_acquired = ["Atlanta", "Charlotte", "blue", 4]
        self.assertIsNone(validate(instance=example_acquired, schema=schemas.ACQUIRED_SCHEMA))

    def test_json_schema_acquired_malformed(self):
        example_acquired = ["Atlanta", 4, "blue", "Charlotte"]
        with self.assertRaises(ValidationError):
            validate(instance=example_acquired, schema=schemas.ACQUIRED_SCHEMA)

    def test_json_schema_this_player(self):
        example_this_player = json.loads(open("../../Examples/Players/example_this_player.json", 'r').read())
        self.assertIsNone(validate(instance=example_this_player, schema=schemas.THIS_PLAYER_SCHEMA))

    def test_json_schema_this_player_malformed(self):
        example_this_player = json.loads(open("../../Examples/Players/example_this_player_malformed.json", 'r').read())
        with self.assertRaises(ValidationError):
            validate(instance=example_this_player, schema=schemas.THIS_PLAYER_SCHEMA)

    def test_json_schema_game_info(self):
        example_game_info = dict()
        example_game_info["unacquired_connections"] = [
            [["Atlanta", [600, 500]], ["Charlotte", [600, 400]], "blue", 4],
            [["Memphis", [300, 300]], ["Nashville", [400, 400]], "green", 3]]

        example_game_info["cards_in_deck"] = 150
        example_game_info["last_turn"] = False

        self.assertIsNone(validate(instance=example_game_info, schema=schemas.GAME_INFO_SCHEMA))

    def test_json_schema_game_info_malformed(self):
        example_game_info = dict()
        example_game_info["unacquired_connections"] = [
            [["Atlanta", [600, 500]], ["Charlotte", [600, 400]], "blue", 4],
            [["Memphis", [300, 300]], ["Nashville", [400, 400]], "green", 3]]
        example_game_info["cards_in_deck"] = "150"
        example_game_info["last_turn"] = False

        with self.assertRaises(ValidationError):
            validate(instance=example_game_info, schema=schemas.GAME_INFO_SCHEMA)

    def test_json_schema_opponent_info(self):
        example_opponent_info_1 = dict()
        example_opponent_info_1["connections"] = [
            [["Atlanta", [600, 500]], ["Charlotte", [600, 400]], "blue", 4],
            [["Memphis", [300, 300]], ["Nashville", [400, 400]], "green", 3]]
        example_opponent_info_1["number_of_cards"] = 13
        example_opponent_info_2 = dict()
        example_opponent_info_2["connections"] = [
            [["Boston", [700, 200]], ["Providence", [725, 250]], "red", 4],
            [["New Orleans", [500, 700]], ["Miami", [600, 800]], "white", 5]]

        example_opponent_info_2["number_of_cards"] = 4
        example_opponent_info_list = [example_opponent_info_1, example_opponent_info_2]
        self.assertIsNone(validate(instance=example_opponent_info_list, schema=schemas.OPPONENT_INFO_SCHEMA))

    def test_json_schema_opponent_info_malformed(self):
        example_opponent_info = dict()
        example_opponent_info["connections"] = [["Atlanta", "Charlotte", "blue", 4]]
        example_opponent_info["number_of_cards"] = 13
        with self.assertRaises(ValidationError):
            validate(instance=example_opponent_info, schema=schemas.OPPONENT_INFO_SCHEMA)

    def test_json_schema_player_state(self):
        example_player_state = json.loads(open("../../Examples/Players/example_player_state.json", 'r').read())
        self.assertIsNone(validate(instance=example_player_state, schema=schemas.PLAYER_GAME_STATE_SCHEMA))

    def test_json_schema_player_state_malformed(self):
        example_player_state = json.loads(
            open("../../Examples/Players/example_player_state_malformed.json", 'r').read())
        with self.assertRaises(ValidationError):
            validate(instance=example_player_state, schema=schemas.PLAYER_GAME_STATE_SCHEMA)

    def test_json_schema_method_call(self):
        example_method_call = ["win", [True]]
        self.assertIsNone(validate(instance=example_method_call, schema=schemas.METHOD_CALL_SCHEMA))

    def test_json_schema_method_call_malformed(self):
        example_method_call = ["win", True]
        with self.assertRaises(ValidationError):
            validate(instance=example_method_call, schema=schemas.METHOD_CALL_SCHEMA)

    def test_json_schema_start_argument(self):
        example_start_argument = [True]
        self.assertIsNone(validate(instance=example_start_argument, schema=schemas.START_SCHEMA))

    def test_json_schema_start_argument_malformed(self):
        example_start_argument = True
        with self.assertRaises(ValidationError):
            validate(instance=example_start_argument, schema=schemas.START_SCHEMA)

    def test_json_schema_setup_argument(self):
        default_map_from_json = json.loads(open("../../Examples/Maps/default_map1.json", 'r').read())
        example_card_plus = ["red", "white", "green", "blue", "blue", "red"]
        example_setup_argument = [default_map_from_json, 8, example_card_plus]
        self.assertIsNone(validate(instance=example_setup_argument, schema=schemas.SETUP_SCHEMA))

    def test_json_schema_setup_argument_malformed(self):
        default_map_from_json_malformed = json.loads(
            open("../../Examples/Maps/default_map1_malformed.json", 'r').read())
        example_card_plus = ["red", "white", "green", "blue", "blue", "red"]
        example_setup_argument = [default_map_from_json_malformed, 8, example_card_plus]
        with self.assertRaises(ValidationError):
            validate(instance=example_setup_argument, schema=schemas.SETUP_SCHEMA)

    def test_json_schema_pick_argument(self):
        example_destinations_plus = [
            [["Atlanta", [600, 500]], ["Charlotte", [600, 400]]],
            [["Memphis", [300, 300]], ["Nashville", [400, 400]]]]
        example_pick_argument = [example_destinations_plus]
        self.assertIsNone(validate(instance=example_pick_argument, schema=schemas.PICK_SCHEMA))

    def test_json_schema_pick_argument_malformed(self):
        example_destinations_plus = [["Atlanta", "Boston"], ["Charlotte", "Raleigh"], ["Nashville", "Memphis"]]
        example_pick_argument = example_destinations_plus
        with self.assertRaises(ValidationError):
            validate(instance=example_pick_argument, schema=schemas.PICK_SCHEMA)

    def test_json_schema_play_argument(self):
        example_player_state = json.loads(open("../../Examples/Players/example_player_state.json", 'r').read())
        example_play_argument = [example_player_state]
        self.assertIsNone(validate(instance=example_play_argument, schema=schemas.PLAY_SCHEMA))

    def test_json_schema_play_argument_malformed(self):
        example_player_state = json.loads(open("../../Examples/Players/example_player_state.json", 'r').read())
        example_play_argument = example_player_state
        with self.assertRaises(ValidationError):
            validate(instance=example_play_argument, schema=schemas.PLAY_SCHEMA)

    def test_json_schema_more_argument(self):
        example_card_plus = ["red", "white", "green", "blue", "blue", "red"]
        example_more_argument = [example_card_plus]
        self.assertIsNone(validate(instance=example_more_argument, schema=schemas.MORE_SCHEMA))

    def test_json_schema_more_argument_malformed(self):
        example_card_plus = ["red", "white", "green", "blue", "blue", "red"]
        example_more_argument = example_card_plus
        with self.assertRaises(ValidationError):
            validate(instance=example_more_argument, schema=schemas.MORE_SCHEMA)

    def test_json_schema_win_argument(self):
        example_win_argument = [True]
        self.assertIsNone(validate(instance=example_win_argument, schema=schemas.WIN_SCHEMA))

    def test_json_schema_win_argument_malformed(self):
        example_win_argument = True
        with self.assertRaises(ValidationError):
            validate(instance=example_win_argument, schema=schemas.WIN_SCHEMA)

    def test_json_schema_end_argument(self):
        example_end_argument = [False]
        self.assertIsNone(validate(instance=example_end_argument, schema=schemas.END_SCHEMA))

    def test_json_schema_end_argument_malformed(self):
        example_end_argument = False
        with self.assertRaises(ValidationError):
            validate(instance=example_end_argument, schema=schemas.END_SCHEMA)

    def test_json_scheme_intro_map(self):
        map_schema = {
            "type": "object",
            "properties": {
                "width": {"type": "number"},
                "height": {"type": "number"},
                "cities": {"type": "array",
                           "items": {
                               "type": "array",
                               "prefixItems": [
                                   {"type": "string"},
                                   {"type": "array",
                                    "items": {
                                        "type": "number"
                                    }}
                               ]}
                           },
                "connections": {"type": "object",
                                "additionalProperties": {"type": "object",
                                                         "additionalProperties": {"type": "object",
                                                                                  "additionalProperties": {
                                                                                      "type": "number"},
                                                                                  }
                                                         }
                                }
            }
        }

        default_map_from_json = json.loads(open("../../Examples/Maps/default_map1.json", 'r').read())
        print(type(default_map_from_json))
        validate(instance=default_map_from_json, schema=map_schema)

    def test_json_schema_intro_destination_plus(self):
        destination_plus_schema = {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
        example_destinations_plus = [["Atlanta", "Boston"], ["Charlotte", "Raleigh"], ["Nashville", "Memphis"]]
        validate(instance=example_destinations_plus, schema=destination_plus_schema)

    def test_json_schema_intro_card_plus(self):
        card_plus_schema = {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
        example_card_plus = ["red", "white", "green", "blue", "blue", "red"]
        validate(instance=example_card_plus, schema=card_plus_schema)


if __name__ == '__main__':
    unittest.main()
