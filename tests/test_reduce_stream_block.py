from unittest.mock import MagicMock
from time import sleep
from nio.util.support.block_test_case import NIOBlockTestCase
from ..reduce_stream_block import ReduceStream


class TestReduceStream(NIOBlockTestCase):

    def signals_notified(self, signals, output_id='default'):
        self._signals = signals

    def test_stream_signals(self):
        """ Test that the block notifies properly when signals come in """
        blk = ReduceStream()
        self.configure_block(blk, {
            "averaging_interval": {"seconds": 5},
            "report_interval": {"seconds": 2},
            "value": "{{ $value }}",
            "group_by": "{{ $group }}"
        })
        blk.start()

        # TODO: Add test

        blk.stop()

    def test_no_signals_default(self):
        """ Test that the block doesn't notify if it has no groups """
        blk = ReduceStream()
        self.configure_block(blk, {
            "averaging_interval": {"seconds": 5},
            "report_interval": {"microseconds": 300000},
            "value": "{{ $value }}"
        })
        blk.report_stats = MagicMock(wraps=blk.report_stats)
        blk.start()
        # After 1 second, we should have had at least 2 report hits but since
        # no signals came in, none should be notified
        sleep(1)
        self.assertGreater(blk.report_stats.call_count, 1)
        self.assert_num_signals_notified(0)
        blk.stop()
