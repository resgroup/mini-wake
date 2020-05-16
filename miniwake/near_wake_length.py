import math


def calculate_ambient_turbulence_wake_erosion_rate(turbulence):

    # Equate 19 (from p440)
    # An Experimental analysis of wind turbine wakes, P.E.J. Vermeulen, Wind Energy Systems August 26-29, 1980.

    if turbulence < 0.02:
        return 5.0 * turbulence
    else:
        return 2.5 * turbulence + 0.05


def calculate_angular_velocity(rpm):
    return rpm * (2.0 * math.pi / 60.0)


def calculate_flow_field_ratio(thrust_coefficient):
    # here flow field ratio is the ratio of the unpeturbed velocity to the (constant) velocity in the potential core
    # ref Equations 7 and 8 in Vermeulen 1980
    # m = Uinf / U2

    if thrust_coefficient > 0.8888:
        return 3.0
    else:
        return 1.0 / math.sqrt(1.0 - thrust_coefficient)


def calculate_mechanical_turbulence_wake_erosion_rate(
        number_of_blades,
        tip_speed_ratio):

    return 0.012 * number_of_blades * tip_speed_ratio


def calculate_n(flow_field_ratio):

    A = 0.214
    B = 0.144
    C = 0.134
    D = 0.124

    c1 = math.sqrt(A + B * flow_field_ratio)
    c2 = math.sqrt(C + D * flow_field_ratio)

    return c1 * (1.0 - c2) / ((1.0 - c1) * c2)


def calculate_radius_of_inviscid_expanded_rotor_disk(
        diameter,
        flow_field_ratio):

    # ref Equation 9 in Vermeulen 1980
    radius = 0.5 * diameter

    return radius * math.sqrt((flow_field_ratio + 1.0) / 2.0)


def calculate_shear_generated_turbulence_wake_erosion_rate(flow_field_ratio):
    return (1.0 - flow_field_ratio) * math.sqrt(1.49 + flow_field_ratio) / (9.76 * (1.0 + flow_field_ratio))


def calculate_tip_speed_ratio(
        angular_velocity,
        radius, velocity):
    return (angular_velocity * radius) / velocity


def calculate_total_wake_erosion_rate(
        ambient_turbulence_wake_erosion_rate,
        shear_generated_turbulence_wake_erosion_rate,
        mechanical_turbulence_wake_erosion_rate):

    return math.sqrt(ambient_turbulence_wake_erosion_rate ** 2.0 + shear_generated_turbulence_wake_erosion_rate ** 2.0 + mechanical_turbulence_wake_erosion_rate ** 2.0)


def calculate_radius(diameter):
    return diameter * 0.5


def generic_rpm(diameter):
    return 1600 / diameter


def calculate_near_wake_length(
        diameter,
        thrust_coefficient,
        rpm,
        number_of_blades,
        velocity,
        turbulence_intensity):

    if rpm is None:
        rpm = generic_rpm(diameter)

    # The near wake length is the distance after which the potential core is completely eroded

    flow_field_ratio = calculate_flow_field_ratio(thrust_coefficient)
    tip_speed_ratio = calculate_tip_speed_ratio(calculate_angular_velocity(rpm), calculate_radius(diameter), velocity)

    return calculate_n(flow_field_ratio) * calculate_radius_of_inviscid_expanded_rotor_disk(diameter, flow_field_ratio) \
           / calculate_total_wake_erosion_rate(
                calculate_ambient_turbulence_wake_erosion_rate(turbulence_intensity),
                calculate_shear_generated_turbulence_wake_erosion_rate(flow_field_ratio),
                calculate_mechanical_turbulence_wake_erosion_rate(number_of_blades, tip_speed_ratio))