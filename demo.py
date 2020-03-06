from miniwake import SingleWake

upwind_diameter = 76.0
upwind_thrust_coefficient = 0.4
upwind_rpm = 17.0
upwind_velocity = 9.
amient_turbulence_intensity = 0.1
upwind_local_turbulence_intensity = amient_turbulence_intensity

single_wake = miniwake.SingleWake(ambient_turbulence_intensity=amient_turbulence_intensity,
                                   upwind_diameter=upwind_diameter,
                                   upwind_thrust_coefficient=upwind_thrust_coefficient,
                                   upwind_velocity=upwind_velocity,
                                   upwind_local_turbulence_intensity=upwind_local_turbulence_intensity,
                                   upwind_rpm=upwind_rpm,
                                   apply_meander=True)

wake = single_wake.calculate(upwind_diameter * 4.0)

print(wake.velocity_deficit(distance_from_wake_center=0.0))
print(wake.added_turbulence(distance_from_wake_center=0.0))
