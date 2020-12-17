from miniwake import SingleWake
from miniwake.turbine import Turbine
from miniwake.turbine import FixedThrustCurve

import numpy as np
import matplotlib.pyplot as plt

upwind_turbine = Turbine(name="T1",
                         x=0.0,
                         y=0.0,
                         hub_height=80.0,
                         diameter=76.0,
                         rotational_speed_rpm=17.0,
                         thrust_curve=FixedThrustCurve(0.4))

upwind_velocity = 9.
amient_turbulence_intensity = 0.10
upwind_local_turbulence_intensity = amient_turbulence_intensity

single_wake = SingleWake(ambient_turbulence_intensity=amient_turbulence_intensity,
                         upwind_turbine=upwind_turbine,
                         upwind_velocity=upwind_velocity,
                         upwind_local_turbulence_intensity=upwind_local_turbulence_intensity,
                         apply_meander=True)

downwind_points = 200
crosswind_points = 100

data = np.array((downwind_points, crosswind_points))
cross_sections = []

threshold = 0.0001

threshold_distances = []
threshold_laterals = []

for normalised_downwind in np.linspace(1.0, 1000.0, num=downwind_points):

    downwind_distance = normalised_downwind * upwind_turbine.diameter
    wake = single_wake.calculate(downwind_distance)

    yv = []
    threshold_lateral = None

    for normalised_lateral in np.linspace(0, 50.0, num=100):

        lateral_distance = normalised_lateral * upwind_turbine.diameter
        deficit = wake.velocity_deficit(lateral_distance=lateral_distance, vertical_distance=0.0)

        if deficit < threshold:
            deficit = np.nan
            if threshold_lateral is None:
                threshold_lateral = normalised_lateral

        yv.append(deficit)

    cross_sections.append(np.array(yv))
    threshold_distances.append(normalised_downwind)
    threshold_laterals.append(threshold_lateral)

data = np.array(cross_sections)

x = np.array(threshold_distances, dtype=float)
y = np.array(threshold_laterals, dtype=float)

t = 1.0 + 0.24 * x

xy = np.transpose(np.vstack((x, y)))

np.savetxt(f"out_{amient_turbulence_intensity}.dat", xy)

plt.imshow(data, cmap='viridis')
plt.colorbar()
plt.show()

plt.scatter(x, y, s=20, marker='o')
plt.scatter(x, t, s=20, marker='^')

plt.show()

