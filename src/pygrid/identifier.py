class IntegerIdentifier:
    def __init__(self, identifier):
        """

        Args:
            identifier (int): a unique integer ID.
        """
        self._id = identifier

    @property
    def arguments(self):
        return ["--job-id", str(self._id)]

    def __eq__(self, other):
        if not isinstance(other, IntegerIdentifier):
            return False
        return other._id == self._id

    def __hash__(self):
        return self._id

    def __repr__(self):
        return f"IntegerIdentifier({self._id})"


class StringIdentifier:
    def __init__(self, identifier):
        """

        Args:
            identifier (str): a unique string ID.
        """
        self._id = identifier

    @property
    def arguments(self):
        return ["--job-id", self._id]

    def __eq__(self, other):
        if not isinstance(other, StringIdentifier):
            return False
        return other._id == self._id

    def __hash__(self):
        return self._id

    def __repr__(self):
        return f"StringIdentifier({self._id})"
