
def quarton_added_turbulence(distance_downwind, thrust_coefficient, diameter, near_wake_length, turbulence):

    return 1.1 * thrust_coefficient ** 0.7 * turbulence ** 0.68 / (distance_downwind / near_wake_length) ** 0.57
