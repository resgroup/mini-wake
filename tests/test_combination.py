import pytest

from miniwake.combination import RSSMaxAutoVelocityDeficitCombiner


def test_velicity_deficit_combination():

    combiner = RSSMaxAutoVelocityDeficitCombiner()

    combiner.add(value=0.1, normalised_distance_upwind=3.0, normalised_lateral_distance=0.0)

    assert combiner.combined_value() == 0.1

    combiner.add(value=0.05, normalised_distance_upwind=7.0, normalised_lateral_distance=0.0)

    assert combiner.closest_normalised_distance_upwind == 3.0

    assert combiner.combined_value() == 0.1