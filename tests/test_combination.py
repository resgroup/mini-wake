import pytest

from wake_combiner import RSSAndMaximumAutoWC


def test_rss_and_maximum_auto_wc():

    combiner = RSSAndMaximumAutoWC()

    combiner.add(value=0.1, normalised_distance_upwind=3.0, normalised_lateral_distance=0.0)
    
    assert combiner.value == 0.1

    combiner.add(value=0.05, normalised_distance_upwind=7.0, normalised_lateral_distance=0.0)

    assert combiner.closest_normalised_distance_upwind == 3.0

    assert combiner.value == 0.1
