import re

from typing import Dict

from boodle.exceptions import BoodlerError

# Regular expression for valid event/property names: one or more elements,
# separated by periods. Each element must contain only letters, digits,
# and underscores. An element may not start with a digit.
_prop_name_regexp = re.compile(r'\A[a-zA-Z_][a-zA-Z_0-9]*(\.([a-zA-Z_][a-zA-Z_0-9]*))*\Z')

# A cache of valid event/property names. We keep this so that we don't
# have to regexp them every time.
_valid_prop_names: Dict[str, str] = {}


def check_prop_name(val):
    """check_prop_name(val) -> str

    Ensure that the value is a valid event or property name. If it isn't,
    raise BoodlerError. If it is, return a str version of it (in case it
    was a unicode object).
    """

    res = _valid_prop_names.get(val)
    if res:
        return res

    res = _prop_name_regexp.match(val)
    if not res:
        raise BoodlerError('invalid prop/event name: ' + val)

    res = str(val)
    _valid_prop_names[res] = res

    return res
