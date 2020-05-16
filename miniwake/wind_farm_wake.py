from .turbine_wake import TurbineWake
from .rotor_integration import VelocityDeficitIntegrator
from .rotor_integration import AddedTurbulenceIntegrator


class WindFarmWake:

    def __init__(
            self,
            turbines,
            ambient_conditions,
            velocity_deficit_integrator=VelocityDeficitIntegrator(),
            added_turbulence_integrator=AddedTurbulenceIntegrator(),
            apply_meander=True,
            apply_added_turbulence=True):

        self.ambient_conditions = ambient_conditions
        
        self.velocity_deficit_integrator = velocity_deficit_integrator
        self.added_turbulence_integrator = added_turbulence_integrator
        
        self.apply_meander = apply_meander
        self.apply_added_turbulence = apply_added_turbulence

        self.turbine_wakes = self.calculate(turbines)

    def calculate(self, turbines):

        turbine_wakes = []

        for i in range(len(turbines)):
            # print(turbines[i].name)
            wake = TurbineWake(
                        turbines[i],
                        self.ambient_conditions.get_velocity(turbines[i].name),
                        self.ambient_conditions.get_turbulence(turbines[i].name),
                        velocity_deficit_integrator=self.velocity_deficit_integrator,
                        added_turbulence_integrator=self.added_turbulence_integrator, 
                        apply_meander=self.apply_meander,
                        apply_added_turbulence=self.apply_added_turbulence,
                    )

            if len(turbine_wakes) > 0:
                if wake.x < turbine_wakes[-1].x:
                    raise Exception("Wakes must be added in order upwind to downwind")

            for j in range(i):
                # print("-", j, turbine_wakes[j].name)
                wake.add_wake(turbine_wakes[j])

            wake.calculate()

            turbine_wakes.append(wake)

        return turbine_wakes
