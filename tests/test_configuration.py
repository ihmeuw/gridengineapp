from configparser import ConfigParser
from pathlib import Path

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


def test_use_outside_configuration():
    """Verify that external config adds to internal config."""
    parser = ConfigParser()
    parser.read_string("""
    [gridengineapp]
    queues = i.q
    """)
    if hasattr(configuration, "_config"):
        delattr(configuration, "_config")
    config = configuration(parser)
    assert "project" in config
    # This new queue overwrote.
    assert config["queues"] == "i.q"

    config = configuration()
    assert "project" in config
    # And later queries get the overwritten one.
    assert config["queues"] == "i.q"
