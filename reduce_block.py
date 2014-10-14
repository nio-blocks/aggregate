from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties.string import StringProperty
from .mixins.group_by.group_by_block import GroupBy
import numbers


@Discoverable(DiscoverableType.block)
class Reduce(Block, GroupBy):

    """ Performs reduce on input signals.

    Properties:
        group_by (ExpressionProperty): The value by which signals are grouped.
        attr_name: The name of attribute in which to perfrom reduce on.

    """
    attr_name = StringProperty(title="Attribute Name")

    def __init__(self):
        super().__init__()
        GroupBy.__init__(self)
        self._signals_to_notify = []

    def process_signals(self, signals):
        self._signals_to_notify = []
        self.for_each_group(self.process_group, signals)
        self.notify_signals(self._signals_to_notify)

    def process_group(self, signals, key):
        """ Executed on each group of incoming signal objects.
        Increments the appropriate count and generates an informative
        output signal.

        """
        count = 0
        sum_ = 0.0
        minimum = None
        maximum = None
        for signal in signals:
            value = getattr(signal, self.attr_name, None)
            if isinstance(value, numbers.Number):
                sum_ += value
                count += 1
                minimum = min(minimum, value) if minimum is not None else value
                maximum = max(maximum, value) if maximum is not None else value
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
