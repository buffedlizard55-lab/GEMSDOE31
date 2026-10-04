import numpy as np
import pytest

from gemsdoe31.runtime import StackedStatic


def test_stacked_static_reads_base_and_appended_rows_without_copying():
    base = np.arange(12, dtype=np.float32).reshape(3, 4)
    extra = (100 + np.arange(8, dtype=np.float32)).reshape(2, 4)
    stacked = StackedStatic(base, extra)

    assert stacked.shape == (5, 4)
    assert stacked.ndim == 2
    assert stacked.dtype == np.dtype(np.float32)
    assert np.array_equal(stacked[0], base[0])
    assert np.array_equal(stacked[3], extra[0])
    assert stacked[4, 2] == extra[1, 2]
    assert np.array_equal(stacked[1:5:2, [3, 1]], np.stack([base[1, [3, 1]], extra[0, [3, 1]]]))
    assert np.array_equal(stacked[:, 2], np.concatenate([base[:, 2], extra[:, 2]]))


def test_stacked_static_requires_aligned_feature_matrices():
    with pytest.raises(ValueError, match="must align"):
        StackedStatic(np.zeros((2, 3)), np.zeros((1, 4)))


def test_stacked_static_rejects_out_of_range_row():
    stacked = StackedStatic(np.zeros((2, 3)), np.zeros((1, 3)))
    with pytest.raises(IndexError):
        stacked[3]
