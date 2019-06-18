from functools import lru_cache

import toml
from pkg_resources import resource_string

from pygrid.delete import qdel
from pygrid.status import qstat, qstat_short
from pygrid.submit import qsub, qsub_template


@lru_cache(maxsize=1)
def configuration():
    return toml.loads(resource_string("pygrid", "configuration.toml").decode())


__all__ = [
    "configuration", "qstat", "qstat_short", "qdel", "qsub", "qsub_template"
]
