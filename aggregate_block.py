import numbers

from nio.block.base import Block
from nio.properties import Property, VersionProperty
from nio.block.mixins.group_by.group_by import GroupBy

from .stats_data import Stats


class Aggregate(GroupBy, Block):

    """ Performs arithmetic aggregate operations on input signals.

    Properties:
        group_by (Property): The value by which signals are grouped.
        value (Property): The value to be passed to aggregate functions.
    """
    version = VersionProperty("0.1.1")
    value = Property(
        title="Aggregate Input Value", default="{{ $value }}")

    def process_signals(self, signals):
        signals_to_notify = self.for_each_group(self.process_group, signals)
        if signals_to_notify:
            self.notify_signals(signals_to_notify)

    def process_group(self, signals, key):
        """ Executed on each group of incoming signal objects.
        Increments the appropriate count and generates an informative
        output signal.

        """
        stats = Stats()

        for signal in signals:
            self._process_signal_for_stats(signal, stats)

        out_sig = stats.get_signal()
        setattr(out_sig, 'group', key)
        return out_sig

    def _process_signal_for_stats(self, signal, stats):
        """ Take action on a Stats object for this signal.

        This should not return anything, it should update the Stats object.
        """
        try:
            value = self.value(signal)
        except:
            self.logger.warning(
                "Unable to compute value from signal : {}".format(signal),
                exc_info=True)
            return  # non valid signals are ignored

        if isinstance(value, list):
            [self._process_value(v, stats) for v in value]
        else:
            self._process_value(value, stats)

    def _process_value(self, value, stats):
        """ Takes a number and some existing stats and updates them.

        If the value passed is not numeric, this method will log a warning
        and ignore the value.

        Returns:
            None: It will update the stats object in place
        """
        if isinstance(value, numbers.Number):
            stats.register_value(value)
            self.logger.debug("After {}, stats are {}".format(value, stats))
        else:
            self.logger.warning("{} is not a number".format(value))
