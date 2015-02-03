from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties.expression import ExpressionProperty
from .mixins.group_by.group_by_block import GroupBy
import numbers


@Discoverable(DiscoverableType.block)
class Reduce(Block, GroupBy):

    """ Performs reduce on input signals.

    Properties:
        group_by (ExpressionProperty): The value by which signals are grouped.
        value (ExpressionProperty): The value to be passed to reduce functions.
    """
    value = ExpressionProperty(title="Reduce Input Value")

    def __init__(self):
        super().__init__()
        GroupBy.__init__(self)
        self._signals_to_notify = []

    def process_signals(self, signals):
        self._signals_to_notify = []
        self.for_each_group(self.process_group, signals)
        if self._signals_to_notify:
            self.notify_signals(self._signals_to_notify)

    def process_group(self, signals, key):
        """ Executed on each group of incoming signal objects.
        Increments the appropriate count and generates an informative
        output signal.

        """
        sum_ = 0.0
        count = 0
        minimum = None
        maximum = None
        stats = sum_, count, minimum, maximum
        for signal in signals:
            try:
                value = self.value(signal)
            except Exception:
                continue  # non valid signals have no impact
            if isinstance(value, list):
                for v in value:
                    stats = self._process_value(v, stats)
            else:
                stats = self._process_value(value, stats)
        sum_, count, minimum, maximum = stats
        average = sum_ / count if count > 0 else None
        signal = Signal({
            "count": count,
            "sum": sum_,
            "average": average,
            "min": minimum,
            "max": maximum,
            "group": key
        })
        self._signals_to_notify.append(signal)

    def _process_value(self, value, stats):
        sum_, count, minimum, maximum = stats
        if isinstance(value, numbers.Number):
            sum_ += value
            count += 1
            minimum = min(minimum, value) if minimum is not None else value
            maximum = max(maximum, value) if maximum is not None else value
        return sum_, count, minimum, maximum
