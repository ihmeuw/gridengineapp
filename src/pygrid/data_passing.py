from logging import getLogger
from pathlib import Path


LOGGER = getLogger(__name__)


class FileEntity:
    """Responsible for making a path that is writable for a file.

    Args:
        relative_path (Path|str): Path to the file, relative to a root.
    """
    def __init__(self, file_path):
        # If location_id isn't specified, it's the same location as the reader.
        self._file_path = Path(file_path)

    @property
    def path(self):
        """Return a full file path to the file, given the current context."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        return self._file_path

    def validate(self):
        """Validate by checking file exists.

        Returns:
            None, on success, or a string on error.
        """
        if not self.path.exists():
            return f"File {self.path} not found"

    def mock(self):
        """Touch the file into existence."""
        self.path.open("w").close()

    def remove(self):
        """Delete, unlink, remove the file. No error if it doesn't exist."""
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass  # OK if it didn't exist
