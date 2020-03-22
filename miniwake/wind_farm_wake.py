from .turbine_wake import TurbineWake
from .rotor_integration import VelocityDeficitIntegrator
from .rotor_integration import AddedTurbulenceIntegrator


class WindFarmWake:

    def __init__(
            self,
            turbines,
            ambient_velocity,
            ambient_turbulence,
            velocity_deficit_integrator=VelocityDeficitIntegrator(),
            added_turbulence_integrator=AddedTurbulenceIntegrator(),
            apply_meander=True):

        self.ambient_velocity = ambient_velocity
        self.ambient_turbulence = ambient_turbulence
        self.velocity_deficit_integrator = velocity_deficit_integrator
        self.added_turbulence_integrator = added_turbulence_integrator
        self.apply_meander = apply_meander

        self.turbine_wakes = self.calculate(turbines)

    def calculate(self, turbines):
        
        turbine_wakes = []

        for i in range(len(turbines)):
        
            wake = TurbineWake(
                        turbines[i],
                        self.ambient_velocity,
                        self.ambient_turbulence,
                        velocity_deficit_integrator=self.velocity_deficit_integrator,
                        added_turbulence_integrator=self.added_turbulence_integrator, 
                        apply_meander=self.apply_meander
                    )

            if len(turbine_wakes) > 0:
                if wake.x < turbine_wakes[-1].x:
                    raise Exception("Wakes must be added in order upwind to downwind")

            for j in range(i):
                wake.add_wake(turbine_wakes[j])

            wake.calculate()

            turbine_wakes.append(wake)

        return turbine_wakes