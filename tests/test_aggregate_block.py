import statistics

from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..aggregate_block import Aggregate


def get_stats(data):
    stats = {
        'count': len(data),
        'sum': sum(data),
        'average': statistics.mean(data),
        'min': min(data),
        'max': max(data),
        'group': None
    }
    return stats


def get_data(*args):
    data = range(*args)
    many_sigs = [Signal({'value': n}) for n in data]
    one_sig = [Signal({'value': list(data)})]
    stats = get_stats(data)
    return many_sigs, one_sig, stats


class TestAggregate(NIOBlockTestCase):

    def test_reduce_many(self):
        """ Test that we can reduce many signals """
        sigs, *_, stats = get_data(100)

        blk = Aggregate()
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        blk.process_signals(sigs)
        self.assertEqual(
            stats, self.last_notified[DEFAULT_TERMINAL][0].to_dict())
        blk.stop()

    def test_reduce_list(self):
        _, sigs, stats = get_data(100)

        blk = Aggregate()
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        blk.process_signals(sigs)
        self.assertEqual(
            stats, self.last_notified[DEFAULT_TERMINAL][0].to_dict())
        blk.stop()

    def test_reduce_none(self):
        blk = Aggregate()
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        blk.process_signals([])
        self.assertEqual(0, len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    def test_reduce_one(self):
        blk = Aggregate()
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        sigs, *_, stats = get_data(0, 1)
        blk.process_signals(sigs)
        self.assertEqual(
            stats, self.last_notified[DEFAULT_TERMINAL][0].to_dict())

        sigs, *_, stats = get_data(10, 11)
        blk.process_signals(sigs)
        self.assertEqual(
            stats, self.last_notified[DEFAULT_TERMINAL][1].to_dict())
        blk.stop()

    def test_reduce_nonsigs(self):
        blk = Aggregate()
        config = {'value': '{{$.value}}'}
        self.configure_block(blk, config)
        blk.start()
        sigs, *_, stats = get_data(0, 100)
        sigs.append(Signal({"not_value": 10000}))
        blk.process_signals(sigs)
        self.assertEqual(
            stats, self.last_notified[DEFAULT_TERMINAL][0].to_dict())

        blk.stop()
