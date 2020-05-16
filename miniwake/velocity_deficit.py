import math
import os
import os.path

from scipy import integrate
from math import sqrt
from scipy import interpolate

from numpy import isnan
from numpy import linspace
from numpy import array
from numpy import zeros

import numpy as np


velocity_deficit_look_up = None


def calculate_shape_at_position_sq(normalized_position_sq):
    if normalized_position_sq > 4.0:
        # shape factor is less than 0.0001% beyond 2.0
        return 0.0
    else:
        return math.exp(-3.56 * normalized_position_sq)


def calculate_shape(normalized_position):
    return calculate_shape_at_position_sq(normalized_position * normalized_position)


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

    if thrust_coefficient < 0.0:
        raise Exception("Negative wake thrust coefficient")

    if turbulence < 0.0:
        raise Exception("Negative wake distance")

    if normalized_distance_downwind < 0.0:
        raise Exception("Negative wake turbulence")
    
    normalized_distance_downwind = max([2.0, normalized_distance_downwind])

    thrust_coefficient = min([1.0, thrust_coefficient])

    if velocity_deficit_look_up is not None:

        if isnan(turbulence):
            raise Exception("Cannot calculate velocity deficit for turbulence=nan")

        # clamp turbulence at maximum of look up
        if turbulence > velocity_deficit_look_up.max_turbulence:
            turbulence = velocity_deficit_look_up.max_turbulence

        # clamp thrust_coefficient to one
        if thrust_coefficient > 1.0:
            thrust_coefficient = 1.0

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


if __name__ == "__main__":
    
    ct = 0.4
    ti = 0.2

    for i in range(10):
        d = float(i)
        print(d, calculate_velocity_deficit(ct, float(i), ti))

    print("Done")
