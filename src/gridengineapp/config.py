from functools import lru_cache
from getpass import getuser
from pathlib import Path
from tempfile import gettempdir

import toml
from pkg_resources import resource_string


@lru_cache(maxsize=1)
def configuration():
    return toml.loads(resource_string("gridengineapp", "configuration.toml").decode())


def shell_directory():
    shell_dir = Path(configuration()["qsub-shell-file-directory"].format(
        user=getuser()
    ))
    early_path = Path(*shell_dir.parts[:2])
    if early_path.exists():
        shell_dir.mkdir(parents=True, exist_ok=True)
        return shell_dir
    temp_dir = Path(gettempdir())
    shell_dir = temp_dir / "shellfiles"
    shell_dir.mkdir(parents=True, exist_ok=True)
    return shell_dir
