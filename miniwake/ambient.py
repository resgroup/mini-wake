
class FixedAmbientConditions:

    def __init__(self, fixed_velocity, fixed_turbulence):
        self.fixed_velocity = fixed_velocity
        self.fixed_turbulence = fixed_turbulence

    def get_bin(self, direction, reference_velocity):
        return self

    def get_velocity(self, turbine_name):
        return self.fixed_velocity

    def get_turbulence(self, turbine_name):
        return self.fixed_turbulence