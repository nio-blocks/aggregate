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
        with self._stats_locks(group):
            self._stats_values[group].append((_time(), stats))

    def report_stats(self):
        out_sigs = []
        for group in self._stats_values:
            with self._stats_locks(group):
                self.trim_old_values(group, _time())

                # If they were all old, get rid of the group
                if len(self._stats_values[group]) == 0:
                    del self._stats_values[group]
                    continue

                group_stats = self._stats_values[group]

            out_sigs.append(sum(group_stats).get_signal())
        if out_sigs:
            self.notify_signals(out_sigs)

    def trim_old_values(self, group, ctime):
        """ Remove any "old" saved values for a given group """
        stats_values = self._stats_values[group]
        self._logger.debug("Trimming old values - had {} items".format(
            len(stats_values)))
        stats_values[:] = [
            data for data in stats_values
            if data[0] > ctime - self.averaging_interval.total_seconds()]
        self._logger.debug("Now has {} items".format(len(stats_values)))
