from functools import lru_cache
from pkg_resources import resource_string
import toml


@lru_cache(maxsize=1)
def configuration():
    return toml.loads(resource_string("pygrid", "configuraiton.toml").decode())
