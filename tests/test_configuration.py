from pygrid.config import shell_directory, configuration
from pathlib import Path


def test_shell_directory():
    shell_dir = shell_directory()
    base_path = Path(configuration()["qsub-shell-file-directory"])
    first_two = Path(*base_path.parts[:2])
    if first_two.exists():
        # Will raise ValueError if not true.
        shell_dir.relative_to(first_two)
    assert isinstance(shell_dir, Path)
    assert shell_dir.is_dir()
