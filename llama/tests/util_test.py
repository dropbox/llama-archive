"""Unittests for util lib."""

from llama import util
import pytest  # noqa


class TestUtil(object):

    def test_mean(self):
        """Test ``util.mean()``"""
        items = [2, 4, 6, 8, 10]
        expected = 6
        result = util.mean(items)
        assert expected == result

    def test_array_split(self):
        """Test ``util.array_split()``"""
        items = range(90)
        expected_lengths = (50, 40)

        batches = util.array_split(items, 50)
        for idx, batch in enumerate(batches):
            assert len(batch) == expected_lengths[idx]
