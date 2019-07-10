class Job:
    def __init__(self, identifier):
        self.inputs = list()
        self.outputs = list()
        self._identifier = identifier

    @property
    def identifier(self):
        return self._identifier

    def run(self):
        pass

    def mock_run(self):
        for input in self.inputs:
            input.validate()

        for output in self.outputs:
            output.mock()
