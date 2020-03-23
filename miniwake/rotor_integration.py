import math


class VelocityDeficitIntegrator:

    def __init__(self, number_of_sections=12):

        self.number_of_sections = number_of_sections
        self.one_over_sections = 1.0 / float(self.number_of_sections)

        self.theta_step = 2.0 * math.pi * self.one_over_sections

        self.effective_faction = 0.75 * 0.5

    def calculate(self,
                  downwind_rotor_diameter,
                  wake_integral):

        effective_radius = self.effective_faction * downwind_rotor_diameter

        combined_value = 0.0

        for i in range(self.number_of_sections):

            theta = i * self.theta_step

            lateral_offset = math.sin(theta) * effective_radius
            vertical_offset = math.sin(theta) * effective_radius

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
