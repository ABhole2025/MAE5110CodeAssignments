import matplotlib.pyplot as plt
import numpy as np
import rimless_wheel as model

from integrators import rk4

params = model.generate_params()

params["slope_angle"] = np.deg2rad(10)

params["num_spokes"] = 8


# State-space grid
theta_values = np.linspace(-np.pi, np.pi, 50)
theta_dot_values = np.linspace(-5.0, 5.0, 50)

results = np.zeros(
    (len(theta_values), len(theta_dot_values))
)

def get_impact_velocities(initial_state, params, time_step, total_time):
    """
    Simulate the rimless wheel and record the angular velocity
    immediately before each impact.
    """

    num_steps = int(total_time / time_step)

    wheel_state = initial_state.copy()
    impact_velocities = []

    current_time = 0.0

    for step in range(num_steps):

        if detect_impact(wheel_state, params):
            # Record velocity immediately before impact
            impact_velocities.append(wheel_state[1])

            # Apply impact reset
            wheel_state = spoke_reset(wheel_state, params)

        wheel_state = rk4(
            current_time,
            wheel_state,
            time_step,
            rimless_wheel_continuous,
            params
        )

        current_time += time_step

    return np.array(impact_velocities)