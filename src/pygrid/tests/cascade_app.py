"""
Tests don't belong in the main repository, but there
have to be tests of applications that are installed
into packages, so this is the only way I can think of to test
that.
"""

from pygrid import Job, FileEntity, entry

class LocationSexJob(Job):
    def __init__(self, location, sex, base_directory):
        super().__init__()
        self.location_id = location
        self.sex = sex
        out_file = base_directory / f"{location}_{sex}.hdf"
        self.outputs["out"] = FileEntity(out_file)

    def run(self):
        self.mock_run()


class CascadeIsh:
    def __init__(self):
        self.base_directory = None
        self.name