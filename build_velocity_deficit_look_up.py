import os
import os.path

from miniwake.velocity_deficit_look_up import VelocityDeficitLookUpBuilder
from miniwake.velocity_deficit_look_up import VelocityDeficitLookUp
from miniwake.velocity_deficit import calculate_velocity_deficit


if __name__ == "__main__":

    rebuild = False

    lookup_path = os.path.join(os.path.dirname(__file__), "look_up")

    if not os.path.isdir(lookup_path):
        rebuild = True
        os.mkdir(lookup_path)

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