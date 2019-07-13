from logging import getLogger
from pathlib import Path
import shelve

try:
    import pandas as pd
except ImportError:
    pass


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
        exists = self.path.exists()
        LOGGER.debug(f"{self.path} exists {exists}")
        if not exists:
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


class PandasFile(FileEntity):
    """Responsible for validating a Pandas file.

    Args:
        file_path (Path|str): Path to the file.
        required_frames (Dict[str,set]): Map from the name of the dataset,
            as specified by the Pandas ``key`` argument, to a list of columns
            that should be in that dataset.
    """
    def __init__(self, file_path, required_frames=None):
        super().__init__(file_path)
        required_frames = required_frames if required_frames else dict()
        self._columns = {key: set(cols) for (key, cols) in required_frames.items()}

    def validate(self):
        """
        Returns:
            None, on success, or a string on error.
        """
        super_valid = super().validate()
        if super_valid:
            return super_valid

        errors = list()
        for key, cols in self._columns.items():
            try:
                df = pd.read_hdf(self.path, key=key)
                if cols != set(df.columns):
                    errors.append(f"for {key} found {df.columns} expected {cols}.")
            except KeyError as key:
                errors.append(f"for {key} found nothing expected {cols}.")
        return " ".join(errors) if errors else None

    def mock(self):
        path = self.path
        LOGGER.debug(f"Mocking Pandas dataframe {path}.")

        if self._columns:
            for key, cols in self._columns.items():
                df = pd.DataFrame({c: [0] for c in cols})
                df.to_hdf(path, key=key, mode="a", format="fixed")
        else:
            df = pd.DataFrame(dict(key=[1], value=[1]))
            df.to_hdf(
                path, key="data", mode="a", format="fixed",
            )


class ShelfFile(FileEntity):
    """Responsible for validating a Python shelf file.

    Args:
        file_path (Path|str): Path to the file.
        required_keys (Set[str]): String names of variables to find in the file.
    """
    def __init__(self, file_path, required_keys=None):
        super().__init__(file_path)
        self._keys = set(required_keys) if required_keys else set()

    def validate(self):
        """
        Validates that there are variables named after the required keys.
        Returns:
            None, on success, or a string on error.
        """
        path = self.path
        search_name = path.parent / (path.name + ".dat")
        if not search_name.exists():
            LOGGER.debug(f"Shelf path doesn't exist {path}")
            return f"Shelf path doesn't exist {path}"
        if self._keys:
            with shelve.open(str(path)) as db:
                in_file = set(db.keys())
            if self._keys - in_file:
                LOGGER.debug(f"Shelf keys not found {path}")
                return f"Shelf keys not found {path} expected {self._keys} found {in_file}"

    def mock(self):
        path = self.path
        with shelve.open(str(path)) as db:
            LOGGER.info(f"mocking shelf with keys {self._keys}")
            for key in self._keys:
                db[key] = "marker"

    def remove(self):
        path = self.path
        base = path.parent
        for dbm_file in base.glob(f"{path.name}.*"):
            dbm_file.unlink()
