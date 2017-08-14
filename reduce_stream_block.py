from collections import defaultdict
from time import time as _time
from threading import Lock

from nio.properties import TimeDeltaProperty, VersionProperty
from nio.modules.scheduler import Job
from nio.block.mixins.persistence.persistence import Persistence

from .stats_data import Stats
from .reduce_block import Reduce


class ReduceStream(Persistence, Reduce):

    version = VersionProperty('0.1.0')
    report_interval = TimeDeltaProperty(
        default={"seconds": 1}, title="Report Interval")
    averaging_interval = TimeDeltaProperty(
        default={"seconds": 5}, title="Averaging Interval")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stats_values = defaultdict(list)
        self._stats_locks = defaultdict(Lock)

    def persisted_values(self):
        return ["_stats_values"]

    def start(self):
        super().start()
        self._start_time = _time()
        self._job = Job(self.report_stats, self.report_interval(), True)

    def stop(self):
        if self._job:
            self._job.cancel()
        super().stop()

    def process_group(self, signals, group):
        """ Process signals from a specific group.

        The parent block will use the GroupBy mixin to call this. It will
        get called for every group of incoming signals.
        """
        stats = Stats()
        for signal in signals:
            # Call the parent block's function to update our stats object
            # with the value off of this signal
            self._process_signal_for_stats(signal, stats)

        # Our stats object is built, let's lock the list of stats and add it
        # to our group
        with self._stats_locks[group]:
            self._stats_values[group].append((_time(), stats))

    def report_stats(self):
        """ Called repeatedly based on the configured report interval.

        This should notify signals for the non-empty groups of data.
        """
        out_sigs = []
        # Iterate over a list rather than the iterator so that we can delete
        # items that are empty lists
        for group, group_stats in list(self._stats_values.items()):
            with self._stats_locks[group]:
                self.trim_old_values(group_stats, _time())

                # If they were all old, get rid of the group
                if len(group_stats) == 0:
                    del self._stats_values[group]
                    continue

            # Sum every Stats (second item in list) - start with an empty
            # Stats object
            sum_stats = sum((data[1] for data in group_stats), Stats())

            out_sig = sum_stats.get_signal()
            setattr(out_sig, "group", group)
            out_sigs.append(out_sig)

        if out_sigs:
            self.notify_signals(out_sigs)

    def trim_old_values(self, group_stats, ctime):
        """ Remove any "old" saved values for a given list """
        self.logger.debug("Trimming old values - had {} items".format(
            len(group_stats)))
        group_stats[:] = [
            data for data in group_stats
            if data[0] > ctime - self.averaging_interval().total_seconds()]
        self.logger.debug("Now has {} items".format(len(group_stats)))
