from miniwake import SingleWake
import numpy as np
import matplotlib.pyplot as plt


upwind_diameter = 76.0
upwind_thrust_coefficient = 0.4
upwind_rpm = 17.0
upwind_velocity = 9.
amient_turbulence_intensity = 0.1
upwind_local_turbulence_intensity = amient_turbulence_intensity

single_wake = SingleWake(ambient_turbulence_intensity=amient_turbulence_intensity,
                         upwind_diameter=upwind_diameter,
                         upwind_thrust_coefficient=upwind_thrust_coefficient,
                         upwind_velocity=upwind_velocity,
                         upwind_local_turbulence_intensity=upwind_local_turbulence_intensity,
                         upwind_rpm=upwind_rpm,
                         apply_meander=True)

wake = single_wake.calculate(upwind_diameter * 4.0)

x = []
yv = []
yt = []

for normalised_distance in np.linspace(-2.0, 2.0, num=100):
    distance = normalised_distance * upwind_diameter
    x.append(normalised_distance)
    yv.append(wake.velocity_deficit(distance_from_wake_center=distance))
    yt.append(wake.added_turbulence(distance_from_wake_center=distance))

plt.scatter(x, yv, s=20, marker='o')
plt.scatter(x, yt, s=20, marker='^')

plt.show()
