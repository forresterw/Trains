# City as specified here:
# https://www.ccs.neu.edu/home/matthias/4500-f21/3.html#%28tech._city%29
CITY_SCHEMA = {
    "type": "array",
    "prefixItems": [
        {"type": "string"},
        {"type": "array",
         "items": {
             "type": "number"
         }}
    ]
}

CONNECTION_SCHEMA = {
    "type": "array",
    "prefixItems": [
        CITY_SCHEMA,
        CITY_SCHEMA,
        {"type": "string"},
        {"type": "number"}
    ]
}

DESTINATION_SCHEMA = {
    "type": "array",
    "prefixItems": [
        CITY_SCHEMA,
        CITY_SCHEMA
    ]
}

# Card* as specified here
# https://www.ccs.neu.edu/home/matthias/4500-f21/5.html#%28tech._card%2A%29
CARD_STAR_SCHEMA = {
    "type": "object",
    "properties": {
        "red": {"type": "number"},
        "blue": {"type": "number"},
        "green": {"type": "number"},
        "white": {"type": "number"}

    }
}

# Acquired as specified here
# https://www.ccs.neu.edu/home/matthias/4500-f21/5.html#%28tech._acquired%29
ACQUIRED_SCHEMA = {
    "type": "array",
    "prefixItems": [
        {"type": "string"},
        {"type": "string"},
        {"type": "string"},
        {"type": "number"}
    ]
}

# Map as specified here
# https://www.ccs.neu.edu/home/matthias/4500-f21/3.html#%28tech._map%29
MAP_SCHEMA = {
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
                       ]},
                   "uniqueItems": True
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

# ThisPlayer as specified here:
# https://www.ccs.neu.edu/home/matthias/4500-f21/5.html#%28tech._thisplayer%29
THIS_PLAYER_SCHEMA = {
    "type": "object",
    "properties": {
        "destination1": DESTINATION_SCHEMA,
        "destination2": DESTINATION_SCHEMA,
        "rails": {"type": "number"},
        "cards": CARD_STAR_SCHEMA,
        "acquired": {"type": "array",
                     "items":
                         ACQUIRED_SCHEMA
                     }
    }
}

GAME_INFO_SCHEMA = {
    "type": "object",
    "properties": {
        "unacquired_connections": {"type": "array",
                                   "items": CONNECTION_SCHEMA},
        "cards_in_deck": {"type": "number"},
        "last_turn": {"type": "boolean"}
    }
}

OPPONENT_INFO_SCHEMA = {
    "type": "array",
    "items": {"type": "object",
              "properties": {
                  "connections": {"type": "array",
                                  "items": CONNECTION_SCHEMA},
                  "number_of_cards": {"type": "number"}
              }}
}

PLAYER_GAME_STATE_SCHEMA = {"type": "object",
                            "properties": {
                                "this": THIS_PLAYER_SCHEMA,
                                "game_info": GAME_INFO_SCHEMA,
                                "opponent_info": OPPONENT_INFO_SCHEMA,
                            }}

# Card+ as specified here
# https://www.ccs.neu.edu/home/matthias/4500-f21/remote.html#%28tech._card%2B%29
CARD_PLUS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "string"
    }
}



# Destination+ as specified here
# https://www.ccs.neu.edu/home/matthias/4500-f21/remote.html#%28tech._destination%2B%29
DESTINATION_PLUS_SCHEMA = {
    "type": "array",
    "items":
        DESTINATION_SCHEMA

}

METHOD_CALL_SCHEMA = {"type": "array",
                      "prefixItems": [
                          {"type": "string"},
                          {"type": "array"}
                      ]}
# All method call arguments as specified here:
# https://www.ccs.neu.edu/home/matthias/4500-f21/remote.html#%28tech._argument%29
START_SCHEMA = {"type": "array",
                "prefixItems": [
                    {"type": "boolean"}
                ]}

SETUP_SCHEMA = {"type": "array",
                "prefixItems": [
                    MAP_SCHEMA,
                    {"type": "number"},
                    CARD_PLUS_SCHEMA
                ]}

PICK_SCHEMA = {"type": "array",
               "prefixItems": [
                   DESTINATION_PLUS_SCHEMA
               ]}

PLAY_SCHEMA = {"type": "array",
               "prefixItems": [
                   PLAYER_GAME_STATE_SCHEMA
               ]}

MORE_SCHEMA = {"type": "array",
               "prefixItems": [
                   CARD_PLUS_SCHEMA
               ]}

GAME_BOOT_SCHEMA = {}

WIN_SCHEMA = {"type": "array",
              "prefixItems": [
                  {"type": "boolean"}
              ]}

TOURNAMENT_BOOT_SCHEMA = {}

END_SCHEMA = {"type": "array",
              "prefixItems": [
                  {"type": "boolean"}
              ]}
