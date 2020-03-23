from miniwake import SingleWake
from miniwake.turbine import Turbine
from miniwake.turbine import FixedThrustCurve

import numpy as np
import matplotlib.pyplot as plt

upwind_turbine = Turbine(x=0.0,
                         y=0.0,
                         hub_height=80.0,
                         diameter=76.0,
                         rotational_speed_rpm=17.0,
                         thrust_curve=FixedThrustCurve(0.4))

upwind_velocity = 9.
amient_turbulence_intensity = 0.1
upwind_local_turbulence_intensity = amient_turbulence_intensity

single_wake = SingleWake(ambient_turbulence_intensity=amient_turbulence_intensity,
                         upwind_turbine=upwind_turbine,
                         upwind_velocity=upwind_velocity,
                         upwind_local_turbulence_intensity=upwind_local_turbulence_intensity,
                         apply_meander=True)

wake = single_wake.calculate(upwind_turbine.diameter * 4.0)

x = []
yv = []
yt = []

for normalised_distance in np.linspace(-2.0, 2.0, num=100):
    distance = normalised_distance * upwind_turbine.diameter
    x.append(normalised_distance)
    yv.append(wake.velocity_deficit(lateral_distance=distance))
    yt.append(wake.added_turbulence(lateral_distance=distance))

plt.scatter(x, yv, s=20, marker='o')
plt.scatter(x, yt, s=20, marker='^')

plt.show()
