from .turbine_wake import TurbineWake
from .rotor_integration import VelocityDeficitIntegrator
from .rotor_integration import AddedTurbulenceIntegrator
from .combination import WeightedAverageRSSLinearVelocityDeficitCombiner


class WindFarmWake:

    def __init__(
            self,
            turbines,
            ambient_conditions,
            velocity_deficit_integrator=VelocityDeficitIntegrator(),
            added_turbulence_integrator=AddedTurbulenceIntegrator(),
            velocity_deficit_combiner=WeightedAverageRSSLinearVelocityDeficitCombiner(),
            apply_meander=True,
            apply_added_turbulence=True):

        self.ambient_conditions = ambient_conditions

        self.velocity_deficit_integrator = velocity_deficit_integrator
        self.velocity_deficit_combiner = velocity_deficit_combiner
        self.added_turbulence_integrator = added_turbulence_integrator

        self.apply_meander = apply_meander
        self.apply_added_turbulence = apply_added_turbulence

        self.turbine_wakes = self.calculate(turbines)

    def recalculate(self, ambient_conditions):

        self.ambient_conditions = ambient_conditions

        for i in range(len(self.turbine_wakes)):

            wake = self.turbine_wakes[i]

            wake.recalculate(
                self.ambient_conditions.get_velocity(wake.name),
                self.ambient_conditions.get_turbulence(wake.name))

    def calculate(self, turbines):

        turbine_wakes = []

        for i in range(len(turbines)):

            wake = TurbineWake(
                turbines[i],
                self.ambient_conditions.get_velocity(turbines[i].name),
                self.ambient_conditions.get_turbulence(turbines[i].name),
                velocity_deficit_integrator=self.velocity_deficit_integrator,
                velocity_deficit_combiner= self.velocity_deficit_combiner,
                added_turbulence_integrator=self.added_turbulence_integrator, 
                apply_meander=self.apply_meander,
                apply_added_turbulence=self.apply_added_turbulence)

            if len(turbine_wakes) > 0:
                if wake.x < turbine_wakes[-1].x:
                    raise Exception("Wakes must be added in order upwind to downwind")

            for j in range(i):
                wake.add_wake(turbine_wakes[j])

            wake.calculate()

            turbine_wakes.append(wake)

        return turbine_wakes
