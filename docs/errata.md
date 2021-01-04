The original paper (page 2) has a little mistake in that the solution implies a non-dimensional velocity, but this is not stated explicitly therefore it is necessary to enure the input values are appropriately normalised i.e.

uc = center_line_velocity_mps / free_stream_velocity_mps

duc_dx = 16.0 * epsilon * (uc**3.0 - uc**2.0 - uc + 1.0) / (uc * thrust_coefficient)

duc_dx_mps *= free_stream_velocity_mps


