
def percentage_point_change(previous_value, current_value):
    return current_value - previous_value


def test_inflation_change_across_zero():
    previous = -0.600648300123685
    current = 0.211466568022607

    change = percentage_point_change(previous, current)

    assert round(change, 2) == 0.81


def test_gdp_growth_change_during_contraction():
    previous = 7.93695013588524
    current = -3.55572193406549

    change = percentage_point_change(previous, current)

    assert round(change, 2) == -11.49
