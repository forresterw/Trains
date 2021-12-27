import jsonschema
import sys

from jsonschema.exceptions import ValidationError
sys.path.append('../../../')


def validate_action_message(formatted_json_action):
    """
    Given a python representation of a player action JSON, return true if the action is 
    valid, else return false.
        Parameters:
            formatted_json_action (PlayerActionJSON): Python data structure(s) for the PlayerActionJSON
        Returns:
            True if the json is well-formed and structurally valid, else false.
    """
    try:
        is_more_cards = type(formatted_json_action) == str \
            and formatted_json_action == "more cards"

        # Validation returns None assuming no exception thrown.
        return is_more_cards or jsonschema.validate() is None
    
    except ValidationError:
        return False
