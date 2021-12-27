import sys
import jsonschema
from jsonschema.exceptions import ValidationError

sys.path.append('../../../')
from Trains.Remote.messages.message_schemas import DESTINATION_PLUS_SCHEMA
from message_schemas import MAP_SCHEMA

def validate_map_json(formatted_json_map) -> bool:
    """
    Given a map that is formatted as a JSON object, return True if the given map
    follows the schema specified for clients to send maps as. Otherwise, return
    false.
        Parameters:
            formatted_json_map (MapJSON): Map data in the form of python data structures mirroring
            the json the map data was loaded from.
        Returns:
            True if the formatted json is valid, else False.
    """
    try:
        jsonschema.validate(instance=formatted_json_map, schema=MAP_SCHEMA)
        return True
    except ValidationError:
        return False

def validate_destination_plus(formatted_json_destination_set):
    """
    Given destinations loaded from a Destination+ JSON, confirms if the given data is 
    valid in structure based on the Destination+ JSON spec.
        Parameters:
            formatted_json_destination_set (Destination+): List of Destination (as per the JSON spec)
        Returns:
            True if the formatted json is valid, else False. 
    """
    try:
        jsonschema.validate(instance=formatted_json_destination_set, schema=DESTINATION_PLUS_SCHEMA)
        return True
    except:
        return False
