from inspect import getmembers


def identifier_problems(identifier_class):
    """Given an identifier class, check that it has the
    right properties."""
    errors = list()
    class_name = identifier_class.__name__
    members = {name: obj for (name, obj) in getmembers(identifier_class)}
    necessary_functions = [
        "add_arguments", "arguments", "__eq__", "__hash__", "__str__"
    ]
    for member in necessary_functions:
        if member not in members:
            errors.append(f"Function {member} not in {class_name}")
    return errors


class IntegerIdentifier:
    def __init__(self, identifier):
        """

        Args:
            identifier (int): a unique integer ID.
        """
        self._id = identifier

    def __int__(self):
        return self._id

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("--job-id", type=int)

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

    def __str__(self):
        return str(self._id)


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

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("--job-id", type=str)

    def __eq__(self, other):
        if not isinstance(other, StringIdentifier):
            return False
        return other._id == self._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"StringIdentifier({self._id})"

    def __str__(self):
        return self._id
