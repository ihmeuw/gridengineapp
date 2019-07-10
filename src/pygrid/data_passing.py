from logging import getLogger
from pathlib import Path


LOGGER = getLogger(__name__)


class FileEntity:
    """Responsible for making a path that is writable for a file.

    Args:
        relative_path (Path|str): Path to the file, relative to a root.
    """
    def __init__(self, relative_path):
        # If location_id isn't specified, it's the same location as the reader.
        self.relative_path = Path(relative_path)

    def path(self, execution_context):
        """Return a full file path to the file, given the current context."""
        full_path = execution_context.base_directory / self.relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return full_path

    def validate(self, execution_context):
        """Validate by checking file exists.

        Returns:
            None, on success, or a string on error.
        """
        path = self.path(execution_context)
        if not path.exists():
            return f"File {path} not found"

    def mock(self, execution_context):
        """Touch the file into existence."""
        self.path(execution_context).open("w").close()

    def remove(self, execution_context):
        """Delete, unlink, remove the file. No error if it doesn't exist."""
        path = self.path(execution_context)
        try:
            path.unlink()
        except FileNotFoundError:
            pass  # OK if it didn't exist
