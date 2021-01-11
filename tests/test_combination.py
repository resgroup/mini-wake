import pytest

from miniwake.combination import RSSMaxAutoVelocityDeficitCombiner, WeightedAverageRSSLinearVelocityDeficitCombiner, StraightAverageRSSLinearVelocityDeficitCombiner


def test_velicity_deficit_combination():

    combiner = RSSMaxAutoVelocityDeficitCombiner()
    combiner1 = WeightedAverageRSSLinearVelocityDeficitCombiner()
    combiner2 = StraightAverageRSSLinearVelocityDeficitCombiner()

    combiner.add(value=0.1, normalised_distance_upwind=3.0, normalised_lateral_distance=0.0)
    combiner1.add(value=0.1, normalised_distance_upwind=3.0, normalised_lateral_distance=0.0)
    combiner2.add(value=0.1, normalised_distance_upwind=3.0, normalised_lateral_distance=0.0)

    assert combiner.combined_value() == 0.1
    assert abs(combiner1.combined_value() - 0.1) < 1E-6
    assert abs(combiner2.combined_value() - 0.1) < 1E-6

    combiner.add(value=0.05, normalised_distance_upwind=7.0, normalised_lateral_distance=0.0)
    combiner1.add(value=0.05, normalised_distance_upwind=7.0, normalised_lateral_distance=0.0)
    combiner2.add(value=0.05, normalised_distance_upwind=7.0, normalised_lateral_distance=0.0)

    assert combiner.closest_normalised_distance_upwind == 3.0

    assert combiner.combined_value() == 0.1
    assert abs(combiner1.combined_value() - 0.1232623) < 1E-6
    assert abs(combiner2.combined_value() - 0.1309017) < 1E-6

