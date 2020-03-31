# mini-wake

[![Build status](https://ci.appveyor.com/api/projects/status/ojclr0weuw5siax2?svg=true)](https://ci.appveyor.com/project/RESSoftwareTeam/mini-wake)

[![codecov](https://codecov.io/gh/resgroup/mini-wake/branch/master/graph/badge.svg)](https://codecov.io/gh/resgroup/mini-wake)

An open-source, light weight, fast to run, easy to understand  &amp; carefully crafted implementation of the Ainslie eddy viscosity wake model and associated sub-models

## Example Usage

```python
from miniwake import SingleWake

upwind_diameter = 76.0
upwind_thrust_coefficient = 0.4
upwind_rpm = 17.0
upwind_velocity = 9.
ambient_turbulence_intensity = 0.1
upwind_local_turbulence_intensity = ambient_turbulence_intensity

single_wake = miniwake.SingleWake(
	ambient_turbulence_intensity=ambient_turbulence_intensity,
	upwind_diameter=upwind_diameter,
	upwind_thrust_coefficient=upwind_thrust_coefficient,
	upwind_velocity=upwind_velocity,
	upwind_local_turbulence_intensity=upwind_local_turbulence_intensity,
	upwind_rpm=upwind_rpm,
	apply_meander=True)

wake = single_wake.calculate(upwind_diameter * 4.0)

print(wake.velocity_deficit(distance_from_wake_center=0.0))
print(wake.added_turbulence(distance_from_wake_center=0.0))
```

## Releasing

Any push to master will release the latest version of the package to the PyPi server. If the version number hasn't changed, then it won't overwrite existing files, so won't normally cause problems, but it is still best avoided. 

