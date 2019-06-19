from functools import lru_cache

import toml
from pkg_resources import resource_string


@lru_cache(maxsize=1)
def configuration():
    return toml.loads(resource_string("pygrid", "configuration.toml").decode())
