import pytest

from src.economics.trade import hhi_from_shares


def test_hhi_for_two_equal_partners():
    assert hhi_from_shares([0.5, 0.5]) == pytest.approx(0.5)


def test_hhi_rejects_shares_that_do_not_sum_to_one():
    with pytest.raises(ValueError, match="sum to approximately"):
        hhi_from_shares([0.2, 0.2])
