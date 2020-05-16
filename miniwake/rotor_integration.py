import math


class RotorCenterIntegrator:

    def calculate(self,
                  downwind_rotor_diameter,
                  wake_integral):

        return wake_integral(0, 0)


class VelocityDeficitIntegrator:

    def __init__(self, number_of_sections=12):

        self.number_of_sections = number_of_sections
        self.one_over_sections = 1.0 / float(self.number_of_sections)

        self.theta_step = 2.0 * math.pi * self.one_over_sections

        self.effective_faction = 0.75 * 0.5

        self.thetas = [i * self.theta_step for i in range(self.number_of_sections)]

        self.laterals = [math.sin(theta) * self.effective_faction for theta in self.thetas]
        self.verticals = [math.cos(theta) * self.effective_faction for theta in self.thetas]

    def calculate(self,
                  downwind_rotor_diameter,
                  wake_integral):

        effective_radius = self.effective_faction * downwind_rotor_diameter

        combined_value = 0.0

        for i in range(self.number_of_sections):

            lateral_offset = self.laterals[i] * downwind_rotor_diameter
            vertical_offset = self.verticals[i] * downwind_rotor_diameter

            combined_value = self.add_value(
                combined_value,
                wake_integral(lateral_offset, vertical_offset))

        return self.finalise(combined_value)

    def add_value(self, combined_value, value):
        return combined_value + value

    def finalise(self, combined_value):
        return combined_value * self.one_over_sections


class AddedTurbulenceIntegrator(VelocityDeficitIntegrator):

    # todo double check this is the right integration logic

    def add_value(self, combined_value, value):
        return max([combined_value, value])

    def finalise(self, combined_value):
        return combined_value
