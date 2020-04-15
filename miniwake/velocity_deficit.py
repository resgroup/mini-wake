import math
import os
import os.path

from scipy import integrate
from math import sqrt
from scipy import interpolate

from numpy import isnan
from numpy import linspace
from numpy import array
from numpy import save as save_np
from numpy import load as load_np
from numpy import zeros

velocity_deficit_look_up = None


def calculate_shape(normalized_position):
    if abs(normalized_position) > 2.0:
        # shape factor is less than 0.0001% beyond 2.0
        return 0.0
    else:
        return math.exp(-3.56 * (normalized_position ** 2.0))


def calculate_width(thrust_coefficient, velocity_deficit):

    return math.sqrt(3.56 * thrust_coefficient / (8.0 * velocity_deficit * (1.0 - 0.5 * velocity_deficit)))


class AndersonSimplifiedSolution:

    K1 = 0.015
    KAPPA = 0.40

    def __init__(
            self,
            free_stream_velocity,
            thrust_coefficient,
            ambient_turbulence):
        
        self.free_stream_velocity = free_stream_velocity
        self.thrust_coefficient = thrust_coefficient
        self.ambient_turbulence = ambient_turbulence
        self.ambient_eddy_visocity = self.calculate_ambient_eddy_visocity(ambient_turbulence)

        self.initial_normalised_distance_downstream = 2.0
        self.initial_centre_line_deficit = self.calculate_initial_centre_line_deficit()
        self.initial_center_line_velocity = self.center_line_velocity(self.initial_centre_line_deficit)

    def F(self, normalized_downwind_distance):

        # from Ainslie, 1988
        if normalized_downwind_distance >= 5.5:
            return 1.0
        else:
            return 0.65 + self.real_cubed_root((normalized_downwind_distance - 4.5) / 23.32)

    def real_cubed_root(self, value):
        abs_root = abs(value) ** (1.0 / 3.0)
        if value < 0:
            return -abs_root
        else:
            return abs_root

    def calculate_initial_centre_line_deficit(self):
        # initial wake deficit = Dm (from Aimslie, 1988)
        # note formula apdated so that ambient turbulence (I0) is a fraction note a percentage i.e. divid by 10 not 1000
        return self.thrust_coefficient - 0.05 - (16.0 * self.thrust_coefficient - 0.5) * self.ambient_turbulence / 10.0

    def b(self, velocity_deficit):
        return calculate_width(self.thrust_coefficient, velocity_deficit)

    def epsilon(
            self,
            normalised_distance_downwind,
            center_line_velocity):

        # eddy-viscosity (from Aimslie, 1988)
        
        velocity_deficit = self.center_line_deficit(center_line_velocity)
        b = self.b(velocity_deficit)

        # note: Anderson's paper doesn't explicitly say that shear term should be divided by wind speed,
        # but this makes sense to make the units consistent when it's added to the ambient term
        shear_eddy_viscosity = AndersonSimplifiedSolution.K1 * b * (self.free_stream_velocity - center_line_velocity) / self.free_stream_velocity
        
        filter_term = self.F(normalised_distance_downwind)

        return  filter_term * (shear_eddy_viscosity + self.ambient_eddy_visocity)

    def calculate_ambient_eddy_visocity(self, ambient_turbulence):
        # Km = ambient turbulence contribution to eddy viscosity
        # note formula apdated so that ambient turbulence (I0) is a fraction note a percentage i.e. no need to divide by 100
        return AndersonSimplifiedSolution.KAPPA * AndersonSimplifiedSolution.KAPPA * ambient_turbulence

    def center_line_velocity(self, center_line_deficit):
        # Uc = U0 * (1-DM)
        return self.free_stream_velocity * (1.0 - center_line_deficit)

    def center_line_deficit(self, center_line_velocity):
        # D = 1-Uc/U0
        return 1.0 - center_line_velocity / self.free_stream_velocity

    def derivative_of_center_line_velocity_wrt_distance(
            self,
            normalised_distance_downwind,
            center_line_velocity):

        # dUc / dx i.e. first derivative of center line velocity w.r.t. normalised distance downwind
        # simplified solution to the eddy viscosity model - 01327-000202 (from Anderson, 2009)

        epsilon = self.epsilon(normalised_distance_downwind, center_line_velocity)

        # note original paper has a little mistake in that the solution implies a non-dimensional velocity, but this is not stated explicitly
        uc = center_line_velocity / self.free_stream_velocity

        derivative = 16.0 * epsilon * (uc**3.0 - uc**2.0 - uc + 1.0) / (uc * self.thrust_coefficient)

        derivative *= self.free_stream_velocity

        return derivative

    def __call__(
            self,
            normalised_distance_downwind,
            center_line_velocity):

        if len(center_line_velocity) != 1:
            raise Exception("One-dimensional y-argument expected")

        return [self.derivative_of_center_line_velocity_wrt_distance(normalised_distance_downwind, center_line_velocity[0])]


class WakeDeficitIntegrator:

    MAXIMUM_DISTANCE_DOWNSTREAM = 1000.0

    def __init__(
            self,
            thrust_coefficient,
            turbulence,
            maximum_distance_downstream=None,
            first_step=0.1,
            max_step=0.1):

        if maximum_distance_downstream is None:
            maximum_distance_downstream = WakeDeficitIntegrator.MAXIMUM_DISTANCE_DOWNSTREAM

        self.free_stream_velocity = 10.0 #initial velocity, arbitary assumption as later normalised
        self.maximum_distance_downstream = maximum_distance_downstream

        self.f = AndersonSimplifiedSolution(
            self.free_stream_velocity,
            thrust_coefficient,
            turbulence)

        self.integrator = integrate.RK45(
            self.f,
            t0=self.f.initial_normalised_distance_downstream,
            y0=[self.f.initial_center_line_velocity],
            t_bound=self.maximum_distance_downstream,
            first_step=first_step,
            max_step=max_step)

        self.normalised_distance_downstream = self.f.initial_normalised_distance_downstream
        self.velocity_deficit = self.f.center_line_deficit(self.f.initial_center_line_velocity)

    def step(self):
        self.integrator.step()
        self.normalised_distance_downstream = self.integrator.t
        self.velocity_deficit = self.f.center_line_deficit(self.integrator.y[0])

    def within_bound(self):
        return (self.normalised_distance_downstream < self.maximum_distance_downstream)


def calculate_velocity_deficit(
        thrust_coefficient,
        normalized_distance_downwind,
        turbulence):

    normalized_distance_downwind = max([2.0, normalized_distance_downwind])
    thrust_coefficient = min([1.0, thrust_coefficient])

    if velocity_deficit_look_up is not None:
        solution = velocity_deficit_look_up(
                    thrust_coefficient=thrust_coefficient,
                    normalized_distance_downwind=normalized_distance_downwind,
                    turbulence=turbulence)
    else:
        solution = solve_velocity_deficit(
                            thrust_coefficient,
                            normalized_distance_downwind,
                            turbulence)

    return max([solution, 0])


def solve_velocity_deficit(
        thrust_coefficient,
        normalized_distance_downwind,
        turbulence):

    """Calculates center line velocity deficit with main solution on demand.
       This could be increased in speed by solving a lookup-table of values once and interpolating
    """

    integrator = WakeDeficitIntegrator(
        thrust_coefficient=thrust_coefficient,
        turbulence=turbulence,
        maximum_distance_downstream=100.0)

    if normalized_distance_downwind <= integrator.normalised_distance_downstream:
        return integrator.velocity_deficit
    elif normalized_distance_downwind > integrator.maximum_distance_downstream:
        return 0.0
            
    x = [None, integrator.normalised_distance_downstream]
    y = [None, integrator.velocity_deficit]

    # integrate until we step past target value
    while integrator.normalised_distance_downstream < normalized_distance_downwind:
        x = [x[1], None]
        y = [y[1], None]
        integrator.step()
        x[1] = integrator.normalised_distance_downstream
        y[1] = integrator.velocity_deficit

    value = interpolate.interp1d(x, y, kind='linear')(normalized_distance_downwind)

    if isnan(value):
        raise Exception("Deficit evalated as Nan") 
    
    return float(value)


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

        self.distances = self.steps(0, max_dist_downwind, dist_downwind_step)
        self.cts = self.steps(0, max_thrust_coefficient, thrust_coefficient_step)
        self.turbulences = self.steps(0, max_turbulence_intensity, turbulence_intensity_step)

        values = []

        for ct in self.cts:

            if print_messages:
                print(f"CT={ct:.2f}")

            values_for_ct = []

            for turbulence in self.turbulences:

                if print_messages:
                    print(f"-TI={(turbulence)*100.0:.2f}%")

                values_for_ct.append(self.calculate(self.distances, ct, turbulence))

            values.append(array(values_for_ct))

        self.deficits = array(values)

    def save(self, folder):
        
        if not os.path.isdir(folder):
            os.mkdir(folder)

        save_np(os.path.join(folder, "thrust_cofficients.npy"), self.cts)
        save_np(os.path.join(folder, "turbulences.npy"), self.turbulences)
        save_np(os.path.join(folder, "distances.npy"), self.distances)
        save_np(os.path.join(folder, "deficits.npy"), self.deficits)

    def calculate(self, distances, ct, turbulence):
        
        if ct <= 0.0:
            return zeros(distances.shape)

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

        values = interpolate.interp1d(x, y, kind='linear')(distances)

        return values

    def steps(self, start, stop, step):
        return linspace(
            start=start,
            stop=stop,
            num=self.calculate_num(start, stop, step)
        )

    def calculate_num(self, start, stop, step):
        return int(round((stop-start) / step, 0))+ 1


class VelocityDeficitLookUp:

    def __init__(self, look_up_folder):

        cts = load_np(os.path.join(look_up_folder, "thrust_cofficients.npy"))
        turbulences = load_np(os.path.join(look_up_folder, "turbulences.npy"))
        distances = load_np(os.path.join(look_up_folder, "distances.npy"))
        deficits = load_np(os.path.join(look_up_folder, "deficits.npy"))

        self.interpolate = interpolate.RegularGridInterpolator(
                points=(cts, turbulences, distances),
                values=deficits,
                method='linear',
                bounds_error=True
            )

    def __call__(
            self,
            thrust_coefficient,
            normalized_distance_downwind,
            turbulence):

        return self.interpolate(
                    (thrust_coefficient,
                    turbulence,
                    normalized_distance_downwind))


if __name__ == "__main__":

    rebuild = False
    lookup_path = os.path.join(os.path.dirname(__file__), "look_up")

    if rebuild:

        look_up_builder = VelocityDeficitLookUpBuilder(
                            dist_downwind_step=0.1,
                            thrust_coefficient_step=0.1,
                            turbulence_intensity_step=0.1,
                            max_dist_downwind=1000.0,
                            max_turbulence_intensity=0.4,
                            max_thrust_coefficient=1.0,
                            print_messages=True)

        look_up_builder.save(lookup_path)

    look_up = VelocityDeficitLookUp(lookup_path)

    print(look_up(0.4, 10, 0.2))
    print(calculate_velocity_deficit(0.4, 10, 0.2))

    print("Done")