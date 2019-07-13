from copy import deepcopy

from pygrid.data_passing import PandasFile, ShelfFile, FileEntity


def test_file_path_constructed(tmp_path):
    # No validation here
    path = tmp_path / "my.db"
    db = FileEntity(path)
    relative_path = db.path.relative_to(tmp_path)
    assert relative_path.name == "my.db"
    db.mock()
    assert db.validate() is None
    # Removing without a file does nothing
    db.remove()


def test_file_path_subdir_constructed(tmp_path):
    """Ensure that relative paths in subdirectories can be written."""
    path = tmp_path / "subdir" / "my.db"
    db = FileEntity(path)
    assert db.validate() is not None
    db.mock()
    assert path.parent.exists()
    assert db.validate() is None


def test_pandas_no_validate(tmp_path):
    path = tmp_path / "my.hdf"
    pdf = PandasFile(path)
    assert pdf.validate()
    pdf.mock()
    assert not pdf.validate()


def test_pandas_validate_happy(tmp_path):
    datasets = dict(
        priors=["integrand", "location", "value"],
        data=["integrand", "stdev"],
    )
    path = tmp_path / "my.hdf"
    pdf = PandasFile(path, required_frames=datasets)
    assert pdf.validate()
    pdf.mock()
    assert not pdf.validate()


def test_pandas_validate_missing_dataset(tmp_path):
    datasets = dict(
        priors=["integrand", "location", "value"],
        data=["integrand", "stdev"],
    )
    path = tmp_path / "my.hdf"
    pdf = PandasFile(path, required_frames=datasets)
    missing_one = dict(priors=datasets["priors"])
    less = PandasFile(path, required_frames=missing_one)
    less.mock()
    assert pdf.validate() is not None


def test_pandas_validate_missing_columns(tmp_path):
    datasets = dict(
        priors=["integrand", "location", "value"],
        data=["integrand", "stdev"],
    )
    path = tmp_path / "my.hdf"
    pdf = PandasFile(path, required_frames=datasets)
    missing_col = deepcopy(datasets)
    missing_col["priors"].remove("value")
    less = PandasFile(path, required_frames=missing_col)
    less.mock()
    assert pdf.validate() is not None


def test_shelf_no_validate(tmp_path):
    path = tmp_path / "my.shelf"
    shelf = ShelfFile(path)
    assert shelf.validate() is not None
    # Create an empty file, but it's not the base filename.
    # Shelf files open a .dat, .bak, and .dir file.
    base_path = shelf.path
    (base_path.parent / (base_path.name + ".dat")).open("w").close()
    # An empty file should validate fine.
    assert shelf.validate() is None


def test_shelf_happy(tmp_path):
    keys = {"hi", "there"}
    path = tmp_path / "my.shelf"
    shelf = ShelfFile(path, required_keys=keys)
    assert shelf.validate() is not None
    shelf.mock()
    assert shelf.validate() is None


def test_shelf_remove(tmp_path):
    keys = {"hi", "there"}
    path = tmp_path / "my.shelf"
    shelf = ShelfFile(path, required_keys=keys)
    shelf.mock()
    assert shelf.validate() is None
    shelf.remove()
    assert shelf.validate() is not None
