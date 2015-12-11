from unittest.mock import MagicMock
from time import sleep, time as _time
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from ..stats_data import Stats
from ..reduce_stream_block import ReduceStream


class TestReduceStream(NIOBlockTestCase):

    def test_groups_properly(self):
        """ Tests that incoming signals are bucketed properly """
        blk = ReduceStream()
        self.configure_block(blk, {
            "value": "{{ $value }}",
            "group_by": "{{ $group }}"
        })

        blk.process_signals([Signal({
            "group": "A", "value": 5
        })])
        blk.process_signals([Signal({
            "group": "B", "value": 7
        })])
        # Test a list of signals too
        blk.process_signals([Signal({
            "group": "A", "value": 9
        }), Signal({
            "group": "B", "value": 4
        }), Signal({
            "group": "A", "value": 3
        })])

        # Should have 2 groups
        self.assertEqual(len(blk._stats_values), 2)
        # Group A should have 2 records even though 3 signals came through
        # because the second set was a list that should be consolidated
        self.assertEqual(len(blk._stats_values['A']), 2)
        self.assertEqual(blk._stats_values['A'][0][1]._count, 1)
        self.assertEqual(blk._stats_values['A'][0][1]._sum, 5)
        self.assertEqual(blk._stats_values['A'][1][1]._count, 2)
        self.assertEqual(blk._stats_values['A'][1][1]._sum, 9 + 3)
        # Group B should have 2 records
        self.assertEqual(len(blk._stats_values['B']), 2)
        self.assertEqual(blk._stats_values['B'][0][1]._count, 1)
        self.assertEqual(blk._stats_values['B'][0][1]._sum, 7)
        self.assertEqual(blk._stats_values['B'][1][1]._count, 1)
        self.assertEqual(blk._stats_values['B'][1][1]._sum, 4)

    def test_drop_old_stats(self):
        """ Tests that during a report old data is not included """
        blk = ReduceStream()
        self.configure_block(blk, {
            "averaging_interval": {"seconds": 5}
        })
        now = _time()
        my_stats = Stats()
        my_stats.register_value(3)
        my_stats.register_value(5)

        blk._stats_values['groupA'] = [
            (now - 10, my_stats),  # too old
            (now - 3, my_stats),
            (now - 1, my_stats)]

        blk._stats_values['groupB'] = [
            (now - 10, my_stats)]  # too old

        blk.report_stats()
        # One signal for each group that has current data
        self.assert_num_signals_notified(1)
        # The signal should only consist of two of the stats, not all 3
        self.assertEqual(self.last_notified['default'][0].count, 4)
        self.assertEqual(self.last_notified['default'][0].sum, 16)
        self.assertEqual(self.last_notified['default'][0].group, 'groupA')

        # Make sure that the empty group got deleted too
        self.assertEqual(len(blk._stats_values), 1)

    def test_report_scheduled(self):
        """ Test that the block will report periodically """
        blk = ReduceStream()
        self.configure_block(blk, {
            "report_interval": {"microseconds": 300000}
        })
        blk.report_stats = MagicMock(wraps=blk.report_stats)
        blk.start()
        # After 1 second, we should have had at least 2 report hits but since
        # no signals came in, none should be notified
        sleep(1)
        self.assertGreater(blk.report_stats.call_count, 1)
        self.assert_num_signals_notified(0)
        blk.stop()
