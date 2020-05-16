import os.path

import numpy as np
from scipy.interpolate import interp1d

from .interpolation import rect_grid_linear
from .velocity_deficit import WakeDeficitIntegrator
from .velocity_deficit import calculate_velocity_deficit


class VelocityDeficitLookUpBuilder:

    def __init__(
            self,
            dist_downwind_step,
            thrust_coefficient_step,
            turbulence_intensity_step,
            max_dist_downwind,
            max_turbulence_intensity,
            max_thrust_coefficient,
            print_messages=False):

        if print_messages:
            print("Building Look-up")

        self.distances = self.steps(
            0,
            max_dist_downwind,
            dist_downwind_step)

        self.cts = self.steps(
            0,
            max_thrust_coefficient,
            thrust_coefficient_step)

        self.turbulences = self.steps(
            0,
            max_turbulence_intensity,
            turbulence_intensity_step)

        values = []

        for ct in self.cts:

            if print_messages:
                print(f"CT={ct:.2f}")

            values_for_ct = []

            for turbulence in self.turbulences:

                if print_messages:
                    print(f"-TI={(turbulence)*100.0:.2f}%")

                values_for_ct.append(self.calculate(
                    self.distances,
                    ct,
                    turbulence))

            values.append(np.array(values_for_ct))

        self.deficits = np.array(values)

    def save(self, folder):
        
        if not os.path.isdir(folder):
            os.mkdir(folder)

        np.save(os.path.join(folder, "thrust_cofficients.npy"), self.cts)
        np.save(os.path.join(folder, "turbulences.npy"), self.turbulences)
        np.save(os.path.join(folder, "distances.npy"), self.distances)
        np.save(os.path.join(folder, "deficits.npy"), self.deficits)

    def calculate(self, distances, ct, turbulence):
        
        if ct <= 0.0:
            return np.zeros(distances.shape)

        integrator = WakeDeficitIntegrator(
            thrust_coefficient=ct,
            turbulence=turbulence,
            maximum_distance_downstream=distances[-1])

        x = [0, integrator.normalised_distance_downstream]
        y = [integrator.velocity_deficit, integrator.velocity_deficit]

        while integrator.normalised_distance_downstream < distances[-1]:
            integrator.step()
            x.append(integrator.normalised_distance_downstream)
            y.append(integrator.velocity_deficit)

        values = interp1d(x, y, kind='linear')(distances)

        return values

    def steps(self, start, stop, step):
        return np.linspace(
            start=start,
            stop=stop,
            num=self.calculate_num(start, stop, step)
        )

    def calculate_num(self, start, stop, step):
        return int(round((stop-start) / step, 0)) + 1


class VelocityDeficitLookUp:

    def __init__(self, look_up_folder, interpolation_method=rect_grid_linear):

        cts = np.load(os.path.join(look_up_folder, "thrust_cofficients.npy"))
        turbulences = np.load(os.path.join(look_up_folder, "turbulences.npy"))
        distances = np.load(os.path.join(look_up_folder, "distances.npy"))
        deficits = np.load(os.path.join(look_up_folder, "deficits.npy"))

        self.max_turbulence = turbulences[-1]

        self.interpolate = interpolation_method(
            cts,
            turbulences,
            distances,
            deficits)

    def __call__(
            self,
            thrust_coefficient,
            normalized_distance_downwind,
            turbulence):

        return self.interpolate((
            thrust_coefficient,
            turbulence,
            normalized_distance_downwind))


