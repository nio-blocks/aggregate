import numbers
import json
import sys
from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties.expression import ExpressionProperty
from .mixins.group_by.group_by_block import GroupBy


class Stats(object):

    """ An object that will contain arithmetic aggregate information.

    Numbers can be "registered" with this object to update the stats.
    """

    def __init__(self):
        self._sum = 0
        self._count = 0
        self._minimum = sys.maxsize
        self._maximum = -sys.maxsize - 1

    def register_value(self, value):
        """ Include a numeric value in the stats.

        Requires that the passed value be numeric
        """
        self._sum += value
        self._count += 1
        self._minimum = min(self._minimum, value)
        self._maximum = max(self._maximum, value)

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

    def __str__(self):
        return json.dumps(self._get_dict())


@Discoverable(DiscoverableType.block)
class Reduce(GroupBy, Block):

    """ Performs arithmetic reduce operations on input signals.

    Properties:
        group_by (ExpressionProperty): The value by which signals are grouped.
        value (ExpressionProperty): The value to be passed to reduce functions.
    """
    value = ExpressionProperty(
        title="Reduce Input Value", default="{{$value}}")

    def process_signals(self, signals):
        signals_to_notify = []
        self.for_each_group(
            self.process_group,
            signals,
            kwargs={"to_notify": signals_to_notify})
        if signals_to_notify:
            self.notify_signals(signals_to_notify)

    def process_group(self, signals, key, to_notify):
        """ Executed on each group of incoming signal objects.
        Increments the appropriate count and generates an informative
        output signal.

        """
        stats = Stats()

        for signal in signals:
            try:
                value = self.value(signal)
            except Exception as e:
                self._logger.warning(
                    "Unable to compute value from signal : {} : {} {}".format(
                        signal, type(e).__name__, str(e)))
                continue  # non valid signals are ignored

            if isinstance(value, list):
                [self._process_value(v, stats) for v in value]
            else:
                self._process_value(value, stats)

        out_sig = stats.get_signal()
        setattr(out_sig, 'group', key)
        to_notify.append(out_sig)

    def _process_value(self, value, stats):
        """ Takes a number and some existing stats and updates them.

        If the value passed is not numeric, this method will log a warning
        and ignore the value.

        Returns:
            None: It will update the stats object in place
        """
        if isinstance(value, numbers.Number):
            stats.register_value(value)
            self._logger.debug("After {}, stats are {}".format(value, stats))
        else:
            self._logger.warning("{} is not a number".format(value))
