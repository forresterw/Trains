import jsonschema
import sys

from jsonschema.exceptions import ValidationError

from Trains.Remote.messages.message_schemas import END_SCHEMA, GAME_BOOT_SCHEMA, \
    METHOD_CALL_SCHEMA, MORE_SCHEMA, PICK_SCHEMA, PLAY_SCHEMA, SETUP_SCHEMA, \
        START_SCHEMA, TOURNAMENT_BOOT_SCHEMA, WIN_SCHEMA
sys.path.append('../../../')

METHOD_CALL_VALIDATION_SCHEMAS = {
    "start": START_SCHEMA,
    "setup": SETUP_SCHEMA,
    "pick": PICK_SCHEMA,
    "play": PLAY_SCHEMA,
    # Args for play and update_player_game_state are the same.
    "update_player_game_state": PLAY_SCHEMA,
    "more": MORE_SCHEMA,
    "boot_player_from_game": GAME_BOOT_SCHEMA,
    "win": WIN_SCHEMA,
    "boot_player_from_tournament": TOURNAMENT_BOOT_SCHEMA,
    "end": END_SCHEMA
}

def validate_server_message(server_message_json: list):
    """
    Given a python representation of a JSON containing a message from the server
    (data for method call, or a [string, [args]]), return True if the JSON is 
    well-formed and structurally valid, else false.
        Parameters:
            server_message_json (MethodCallJSON): Pythonic JSON containing a method name and
                data for its arguments.
        Returns:
            True if it is valid/well-formed, else False.
    """
    try:
        jsonschema.validate(instance=server_message_json, schema=METHOD_CALL_SCHEMA)

        # Method name variables.
        method_name_index = 0
        method_name = server_message_json[method_name_index]
        possible_method_names = set(METHOD_CALL_VALIDATION_SCHEMAS.keys())

        # Method args variables.
        method_args_index = 1
        method_args = server_message_json[method_args_index]
        if method_name in possible_method_names:
            jsonschema.validate(instance=method_args, schema=METHOD_CALL_VALIDATION_SCHEMAS[method_name])
            return True
        
    except ValidationError:
        return False
        