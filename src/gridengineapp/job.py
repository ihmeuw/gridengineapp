class Job:
    def __init__(self):
        self._inputs = dict()
        self._outputs = dict()

    @property
    def resources(self):
        return dict(
            memory_gigabytes=1,
            threads=1,
            run_time_minutes=1,
        )

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    def run(self):
        pass

    def mock_run(self):
        for input in self.inputs.values():
            input.validate()

        for output in self.outputs.values():
            output.mock()

    def done(self):
        errors = [output.validate() for output in self.outputs.values()]
        return all(err is None for err in errors)
