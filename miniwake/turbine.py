
class FixedThrustCurve:
    
    def __init__(self, value):
        self.value = value
    
    def __call__(self, velocity):
        return self.value


class Turbine:

    def __init__(
            self,
            name,
            x,
            y,
            hub_height,
            diameter,
            rotational_speed_rpm,
            thrust_curve,
            number_of_blades=3
            ):

        self.name = name
        self.x = x
        self.y = y
        self.hub_height = hub_height
        self.diameter = diameter
        self.number_of_blades = number_of_blades
        self.rotational_speed_rpm = rotational_speed_rpm
        self.thrust_curve = thrust_curve

    def clone_at_new_location(self, x, y):
        return Turbine(
            name=self.name,
            x=x,
            y=y,
            hub_height=self.hub_height,
            diameter=self.diameter,
            number_of_blades=self.number_of_blades,
            rotational_speed_rpm=self.rotational_speed_rpm,
            thrust_curve=self.thrust_curve
        )