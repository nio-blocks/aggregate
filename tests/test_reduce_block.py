
import statistics

from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from ..reduce_block import Reduce


def get_stats(data):
    stats = {
        'count': len(data),
        'sum': sum(data),
        'average': statistics.mean(data),
        'min': min(data),
        'max': max(data),
        'group': 'null'
    }
    return stats


def get_data(*args):
    data = range(*args)
    many_sigs = [Signal({'value': n}) for n in data]
    one_sig = [Signal({'value': list(data)})]
    stats = get_stats(data)
    return many_sigs, one_sig, stats


class TestReduce(NIOBlockTestCase):

    def signals_notified(self, signals, output_id='default'):
        self._signals = signals

    def test_reduce_many(self):
        """Test that the simulator simulates and keeps a good interval.

        The simulator starts notifying signals only after a full interval
        has passed. As such, waiting for 2.5 full intervals should have
        notified two sets of signals.
        """
        sigs, *_, stats = get_data(100)

        blk = Reduce()
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        blk.process_signals(sigs)
        self.assertEqual(stats, self._signals[0].to_dict())
        blk.stop()

    def test_reduce_list(self):
        _, sigs, stats = get_data(100)

        blk = Reduce()
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        blk.process_signals(sigs)
        self.assertEqual(stats, self._signals[0].to_dict())
        blk.stop()

    def test_reduce_none(self):
        blk = Reduce()
        self._signals = []
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        blk.process_signals([])
        self.assertEqual(0, len(self._signals))
        blk.stop()

    def test_reduce_one(self):
        blk = Reduce()
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        sigs, *_, stats = get_data(0, 1)
        blk.process_signals(sigs)
        self.assertEqual(stats, self._signals[0].to_dict())

        sigs, *_, stats = get_data(10, 11)
        blk.process_signals(sigs)
        self.assertEqual(stats, self._signals[0].to_dict())
        blk.stop()

    def test_reduce_nonsigs(self):
        blk = Reduce()
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        sigs, *_, stats = get_data(0, 100)
        sigs.append(Signal({"not_value": 10000}))
        blk.process_signals(sigs)
        self.assertEqual(stats, self._signals[0].to_dict())

        blk.stop()
