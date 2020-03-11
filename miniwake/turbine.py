
class FixedThrustCurve:
    
    def __init__(self, value):
        self.value = value
    
    def __call__(self, velocity):
        return self.value


class Turbine:

    def __init__(self, x, y, diameter, rotational_speed_rpm, thrust_curve, number_of_blades=3):
        self.x = x
        self.y = y
        self.diameter = diameter
        self.number_of_blades = number_of_blades
        self.rotational_speed_rpm = rotational_speed_rpm
        self.thrust_curve = thrust_curve
