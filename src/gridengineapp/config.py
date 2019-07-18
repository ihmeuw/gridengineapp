from configparser import ConfigParser
from getpass import getuser
from logging import getLogger
from pathlib import Path
from tempfile import gettempdir

from pkg_resources import resource_string, iter_entry_points

LOGGER = getLogger(__name__)


def installed_config_parsers():
    parsers = list()
    for entry_point in iter_entry_points("ihmeuw.config", __package__):
        LOGGER.debug(f"Found configuration in distribution {entry_point.dist}")
        parsers.append(entry_point.load()())
    return parsers


def configuration(alternate_configparser=None):
    """Returns a configuration dictionary.
    If something passes in an object of type ConfigParser,
    then we use that.

    Args:
        alternate_configparser (ConfigParser.SectionProxy):
            If this is passed in, then use this instead of
            the internal config parser.

    Returns:
        ConfigParser.SectionProxy: This is a mapping type.
    """
    if (not hasattr(configuration, "_config") or
            alternate_configparser is not None):
        bytes_form = resource_string(__package__, "configuration.cfg")
        parser = ConfigParser()
        parser.read_string(bytes_form.decode())
        parsers = installed_config_parsers()
        if alternate_configparser is not None:
            parsers.append(alternate_configparser)
        for ordered_load in parsers:
            parser.read_dict(ordered_load)
        section = parser[__package__]
        configuration._config = section
    return getattr(configuration, "_config")


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
