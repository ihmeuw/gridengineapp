import logging
import sys
from ast import parse, If
from hashlib import sha224
from inspect import isclass, getmodule, getsource
from os import linesep
from pathlib import Path
from textwrap import dedent

from .config import shell_directory

LOGGER = logging.getLogger(__name__)


def write_if_does_not_exist(main_str):
    hash = sha224()
    hash.update(main_str.encode())
    pyfile = shell_directory() / f"{hash.hexdigest()}.py"
    if not pyfile.exists():
        with pyfile.open("w") as pystream:
            pystream.write(main_str)
    return pyfile


def module_has_main_guard(source):
    """Decide whether this module has a main guard."""
    body = parse(source).body
    found_guard = False
    for line in body:
        try:
            if isinstance(line, If) and line.test.left.id == "__name__":
                found_guard = line.test.comparators[0].s == "__main__"
        except AttributeError:
            pass  # This didn't match. Keep looking.
    return found_guard


def find_or_create_executable(application):
    if isclass(application):
        app_class = application
    else:
        app_class = application.__class__

    module = getmodule(app_class)
    package_name = module.__package__
    class_name = app_class.__name__
    installed = package_name is not ""
    module_name = module.__spec__.name
    app_has_main = module_has_main_guard(getsource(module))

    if app_has_main and installed:
        # "python -m mypackage.module"
        argv0 = ["-m", module_name]
    elif app_has_main and not installed:
        # python filename
        argv0 = [str(Path(module.__file__).resolve())]
    elif not app_has_main and installed:
        main_str = dedent(f"""
            from {module_name} import {class_name}
            from pygrid import entry
            app = {class_name}()
            exit(entry(app))
        """)
        pyfile = write_if_does_not_exist(main_str)
        argv0 = [str(pyfile)]
    else:
        module_file = Path(module.__file__).resolve()
        module_dir = module_file.parent
        main_str = dedent(f"""
            import sys
            sys.path.append("{module_dir}")
            from {module_name} import {class_name}
            from pygrid import entry
            app = {class_name}()
            exit(entry(app))
        """)
        pyfile = write_if_does_not_exist(main_str)
        argv0 = [str(pyfile)]
    return argv0


def subprocess_executable(app):
    argv0 = find_or_create_executable(app)
    python_executable = Path(sys.executable)
    return python_executable, argv0


def executable_for_job(app):
    argv0 = find_or_create_executable(app)
    main_path = " ".join(str(command_arg) for command_arg in argv0)
    environment_base = Path(sys.exec_prefix)
    activate = environment_base / "bin" / "activate"
    commands = ["#!/bin/bash"]
    if activate.exists():
        commands.append(f"source {activate}")
    else:
        conda_sh = environment_base / "etc" / "profile.d" / "conda.sh"
        if conda_sh.exists():
            commands.append(f". {conda_sh}")
        commands.append(f"conda activate {environment_base}")
    commands.append(f"python {main_path} $*")
    commands.append("")
    command_lines = linesep.join(commands)

    hash = sha224()
    hash.update(command_lines.encode())
    filename = f"{hash.hexdigest()}.sh"
    tmp = shell_directory() / filename
    if not tmp.exists():
        LOGGER.debug(f"Writing {tmp} shell file.")
        with tmp.open("w") as script_out:
            script_out.write(command_lines)
    else:
        LOGGER.debug(f"Using existing shell file {tmp}.")
    return tmp
