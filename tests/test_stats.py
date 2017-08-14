from nio.testing.block_test_case import NIOBlockTestCase

from ..stats_data import Stats


class TestStats(NIOBlockTestCase):

    def test_stats_add(self):
        """Test that stats are properly added together """
        stats1 = Stats()
        stats2 = Stats()

        stats1.register_value(1)
        stats1.register_value(2)
        stats1.register_value(3)

        stats2.register_value(4)
        stats2.register_value(9)

        stats_sum = (stats1 + stats2).get_signal()
        self.assertEqual(stats_sum.count, 5)
        self.assertEqual(stats_sum.sum, 19)
        self.assertEqual(stats_sum.average, 19 / 5)
        self.assertEqual(stats_sum.min, 1)
        self.assertEqual(stats_sum.max, 9)

    def test_stats_empty_add(self):
        """Test that stats are properly added together """
        stats_data = Stats()
        stats_empty = Stats()

        stats_data.register_value(1)
        stats_data.register_value(2)
        stats_data.register_value(3)

        # Make sure the sum of an empty works both ways
        self.assertDictEqual(
            (stats_data + stats_empty)._get_dict(),
            stats_data._get_dict())
        self.assertDictEqual(
            (stats_empty + stats_data)._get_dict(),
            stats_data._get_dict())

        # Make sure the sum of two empties works too
        self.assertDictEqual(
            (stats_empty + stats_empty)._get_dict(),
            stats_empty._get_dict())

    def test_stats_length(self):
        """Test that stats can be lengthified """
        stats_data = Stats()
        stats_empty = Stats()

        stats_data.register_value(1)
        stats_data.register_value(2)
        stats_data.register_value(3)

        self.assertEqual(len(stats_data), 3)
        self.assertEqual(len(stats_empty), 0)
