import json
from nio.common.signal.base import Signal


class Stats(object):

    """ An object that will contain arithmetic aggregate information.

    Numbers can be "registered" with this object to update the stats.
    """

    def __init__(self):
        self._sum = 0
        self._count = 0
        self._minimum = None
        self._maximum = None

    def register_value(self, value):
        """ Include a numeric value in the stats.

        Requires that the passed value be numeric
        """
        self._sum += value
        self._count += 1
        self._minimum = min(self._minimum, value) \
            if self._minimum is not None else value
        self._maximum = max(self._maximum, value) \
            if self._maximum is not None else value

    def _get_dict(self):
        """ Get the stats information in a dictionary """
        return {
            "count": self._count,
            "sum": self._sum,
            "average": self._sum / self._count if self._count > 0 else None,
            "min": self._minimum,
            "max": self._maximum,
        }

    def get_signal(self):
        """ Produce a Signal with the stats information """
        return Signal(self._get_dict())

    def __len__(self):
        return self._count

    def __str__(self):
        return json.dumps(self._get_dict())

    def __add__(self, other):
        # These two conditionals will make sure we have data for all values
        if len(self) == 0:
            return other
        if len(other) == 0:
            return self

        result = Stats()
        result._count = self._count + other._count
        result._sum = self._sum + other._sum
        result._minimum = min(self._minimum, other._minimum)
        result._maximum = max(self._maximum, other._maximum)

        return result
