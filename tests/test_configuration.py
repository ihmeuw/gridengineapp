from configparser import ConfigParser
from pathlib import Path

from pkg_resources import resource_string

from gridengineapp.config import shell_directory, configuration


def test_shell_directory():
    shell_dir = shell_directory()
    base_path = Path(configuration()["qsub-shell-file-directory"])
    first_two = Path(*base_path.parts[:2])
    if first_two.exists():
        # Will raise ValueError if not true.
        shell_dir.relative_to(first_two)
    assert isinstance(shell_dir, Path)
    assert shell_dir.is_dir()


def test_use_configparser():
    bytes_form = resource_string("gridengineapp", "configuration.cfg")
    parser = ConfigParser()
    parser.read_string(bytes_form.decode())
    section = parser["gridengineapp"]
    print(dir())
    print(type(section))
    for k, v in section.items():
        print(f"{k}: {type(v)} {v}")
