from .wind_farm_wake import WindFarmWake
from miniwake.rotation import rotate_and_sort_turbines as rotate_and_sort


class WindFarm:

    def __init__(
            self,
            turbines,
            ambient_velocity,
            ambient_turbulence,
            velocity_integrator,
            turbulence_integrator,
            apply_meander):

        self.turbines = turbines
        self.ambient_velocity = ambient_velocity
        self.ambient_turbulence = ambient_turbulence

        self.validate_unique_turbine_names()
        self.transformed_turbines_cache = {}

        self.velocity_integrator = velocity_integrator
        self.turbulence_integrator = turbulence_integrator
        self.apply_meander = apply_meander

    def validate_unique_turbine_names(self):

        names = {}

        for turbine in self.turbines:

            if turbine.name in names:
                raise Exception(f"Non-unique turbine name {turbine.name}")

            names[turbine.name] = turbine.name

    def calculate(self, direction, reference_ambient_velocity):

        if direction not in self.transformed_turbines_cache:
            transformed_turbines = rotate_and_sort(direction, self.turbines)
            self.transformed_turbines_cache[direction] = transformed_turbines
        else:
            transformed_turbines = self.transformed_turbines[direction]

        wind_farm_wake = WindFarmWake(
                    transformed_turbines,
                    ambient_velocity=self.ambient_velocity.get_bin(direction, reference_ambient_velocity),
                    ambient_turbulence=self.ambient_turbulence.get_bin(direction, reference_ambient_velocity),
                    velocity_deficit_integrator=self.velocity_integrator,
                    added_turbulence_integrator=self.turbulence_integrator,
                    apply_meander=self.apply_meander)

        return self.restore_original_order(wind_farm_wake.turbine_wakes)

    def restore_original_order(self, turbine_wakes):

        # reorder turbines to original order
        wake_dict = {}

        for turbine_wake in turbine_wakes:
            wake_dict[turbine_wake.name] = turbine_wake

        original_order_wakes = []

        for turbine in self.turbines:
            original_order_wakes.append(wake_dict[turbine.name])

        return original_order_wakes
