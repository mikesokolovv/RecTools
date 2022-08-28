import numpy as np
import pytest

from rectools.utils import fast_isin, fast_isin_for_sorted_test_elements
from rectools.utils.array_set_ops import fast_2d_int_unique


@pytest.mark.parametrize(
    "arr",
    (
        np.array([], dtype=int).reshape((0, 2)),
        np.array([[1, 10]]),
        np.array([[1, 10], [2, 20]]),
        np.array([[1, 10], [1, 10]]),
        np.array([[1, 10], [2, 20], [1, 10], [2, 20]]),
        np.array([[1], [2], [1]]),
        np.array([[1, 2, 3], [1, 2, 3], [10, 20, 30]]),
    )
)
def test_fast_2d_int_unique(arr: np.ndarray) -> None:
    actual_unq, actual_inv = fast_2d_int_unique(arr)
    expected_unq, expected_inv = np.unique(arr, axis=0, return_inverse=True)
    np.testing.assert_equal(actual_unq, expected_unq)
    np.testing.assert_equal(actual_inv, expected_inv)


@pytest.mark.parametrize(
    "elements,test_elements,expected",
    (
        (np.array([2, 6, 4]), np.array([2, 5, 4, 1]), np.array([True, False, True])),
        (np.array(["2", "6", "4"]), np.array(["2", "5", "4", "1"]), np.array([True, False, True])),
        (np.array([2, 6, 4], dtype="O"), np.array([2, 5, 4, 1], dtype="O"), np.array([True, False, True])),
        (np.array([2, 6, 4]), np.array([2, 5, 4, 1], dtype="O"), np.array([True, False, True])),
        (np.array([2, 6, 4], dtype="O"), np.array([2, 5, 4, 1]), np.array([True, False, True])),
        (np.array([2, 6, 4]), np.array(["2", "5", "4", "1"]), np.array([False, False, False])),
        (np.array(["2", "6", "4"]), np.array([2, 5, 4, 1]), np.array([False, False, False])),
        (np.array([2, 6, 4]), np.array(["2", "5", "4", "1"], dtype="O"), np.array([False, False, False])),
        (np.array([2, 6, 4], dtype="O"), np.array(["2", "5", "4", "1"], dtype="O"), np.array([False, False, False])),
        (np.array(["2", "6", "4"], dtype="O"), np.array([2, 5, 4, 1]), np.array([False, False, False])),
        (np.array([]), np.array([]), np.array([])),
        (np.array([]), np.array([2, 5, 4]), np.array([])),
        (np.array([2, 6, 4]), np.array([]), np.array([False, False, False])),
    ),
)
def test_fast_isin(elements: np.ndarray, test_elements: np.ndarray, expected: np.ndarray) -> None:
    actual = fast_isin(elements, test_elements)
    np.testing.assert_array_equal(actual, expected)


class TestFastIsinForSortedTestElements:
    @pytest.mark.parametrize("invert", (True, False))
    def test_when_arrays_not_empty(self, invert: bool) -> None:
        actual = fast_isin_for_sorted_test_elements(
            np.array([10, 7, 3, 8, 4, 12]),
            np.array([4, 6, 8, 10]),
            invert=invert,
        )
        expected = np.array([True, False, False, True, True, False])
        if invert:
            expected = ~expected
        np.testing.assert_array_equal(actual, expected)

    def test_for_empty_elements(self) -> None:
        actual = fast_isin_for_sorted_test_elements(np.array([]), np.array([4, 8, 10]))
        np.testing.assert_array_equal(actual, np.array([]))

    def test_output_for_empty_test_elements(self) -> None:
        actual = fast_isin_for_sorted_test_elements(np.array([10, 6]), np.array([]))
        np.testing.assert_array_equal(actual, np.array([False, False]))
