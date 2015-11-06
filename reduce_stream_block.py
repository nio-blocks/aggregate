from collections import defaultdict
from time import time as _time
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import TimeDeltaProperty
from nio.modules.threading import Lock
from nio.modules.scheduler import Job
from .stats_data import Stats
from .reduce_block import Reduce


@Discoverable(DiscoverableType.block)
class ReduceStream(Reduce):

    report_interval = TimeDeltaProperty(
        default={"seconds": 1}, title="Report Interval")
    averaging_interval = TimeDeltaProperty(
        default={"seconds": 5}, title="Averaging Interval")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._stats_values = defaultdict(list)
        self._stats_locks = defaultdict(Lock)

    def start(self):
        super().start()
        self._start_time = _time()
        self._job = Job(self.report_stats, self.report_interval, True)

    def stop(self):
        if self._job:
            self._job.cancel()
        super().stop()

    def process_group(self, signals, group):
        stats = Stats()
        for signal in signals:
            self._process_signal_for_stats(signal, stats)
        with self._stats_locks[group]:
            self._stats_values[group].append((_time(), stats))

    def report_stats(self):
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

            # Sum every Stats (after the first), using the first one as
            # the starting point
            out_sigs.append(
                sum([data[1] for data in group_stats[1:]], group_stats[0][1])
                .get_signal())

        if out_sigs:
            self.notify_signals(out_sigs)

    def trim_old_values(self, group_stats, ctime):
        """ Remove any "old" saved values for a given list """
        self._logger.debug("Trimming old values - had {} items".format(
            len(group_stats)))
        group_stats[:] = [
            data for data in group_stats
            if data[0] > ctime - self.averaging_interval.total_seconds()]
        self._logger.debug("Now has {} items".format(len(group_stats)))
