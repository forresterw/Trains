from numbers import Number


def reverse_json_value(json_value):
    if isinstance(json_value, bool):
        return not json_value
    elif isinstance(json_value, Number):
        return -json_value
    elif isinstance(json_value, str):
        return json_value[::-1]
    elif json_value is None:
        return None
    elif isinstance(json_value, list):
        return [reverse_json_value(x) for x in reversed(json_value)]
    elif isinstance(json_value, object):
        for key in json_value:
            json_value[key] = reverse_json_value(json_value[key])
        return json_value
    else:
        print("Error")
