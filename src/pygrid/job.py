class Job:
    def __init__(self):
        self._inputs = list()
        self._outputs = list()

    @property
    def identifier(self):
        raise NotImplementedError()

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
        for input in self.inputs:
            input.validate()

        for output in self.outputs:
            output.mock()

    def done(self):
        errors = [output.validate() for output in self.outputs]
        return any(err is not None for err in errors)
