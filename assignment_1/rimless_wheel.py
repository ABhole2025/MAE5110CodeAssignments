import numpy as np

from integrators import rk4


def generate_params():
    return {
        "gravity": 9.81,
        "spoke_length": 1.0,
        "slope_angle": np.deg2rad(20),
        "num_spokes": 8}

def rimless_wheel_continuous(t, state, params):
    """
    Continuous dynamics of the rimless wheel while pivoting
    on the stance spoke.

    theta is measured from the global upward vertical,
    positive in the downhill direction.
    """
    theta, theta_dot = state

    g = params["gravity"]
    l = params["spoke_length"]
    gamma = params["slope_angle"]

    theta_ddot = (g / l) * np.sin(theta + gamma)

    return np.array([theta_dot, theta_ddot])


def detect_impact(wheel_state, params):
    """
    Detect when the next spoke reaches the ground.
    """
    theta, theta_dot = wheel_state

    num_spokes = params["num_spokes"]
    alpha = np.pi / num_spokes
    gamma = params["slope_angle"]

    impact_angle = -gamma + 2 * alpha

    return theta >= impact_angle and theta_dot > 0


def spoke_reset(wheel_state, params):
    """
    Reset dynamics at impact.
    """
    theta, theta_dot = wheel_state

    num_spokes = params["num_spokes"]
    alpha = np.pi / num_spokes

    new_theta = theta - 2 * alpha
    new_theta_dot = theta_dot * np.cos(2 * alpha)

    return np.array([new_theta, new_theta_dot])


def simulate_rimless_wheel(initial_state, params, time_step, total_time):

    num_steps = int(total_time / time_step)

    times = np.zeros(num_steps)
    angles = np.zeros(num_steps)
    angular_velocities = np.zeros(num_steps)

    wheel_state = initial_state.copy()
    current_time = 0.0

    for step in range(num_steps):

        times[step] = current_time
        angles[step] = wheel_state[0]
        angular_velocities[step] = wheel_state[1]

        if detect_impact(wheel_state, params):
            wheel_state = spoke_reset(wheel_state, params)


        wheel_state = rk4(
            current_time,
            wheel_state,
            time_step,
            rimless_wheel_continuous,
            params)

        wheel_state[0] = (
            (wheel_state[0] + np.pi) % (2 * np.pi) - np.pi)

        current_time += time_step

    return times, angles, angular_velocities


'''
### Running the rimless wheel

Make sure `rimless_wheel.py` and the integrator you will use are in the same directory.

```python
import numpy as np
import rimless_wheel as model

I used rk4.py from 'integrators' which I implemented in assignment 0

i.e.
from integrators import rk4

params = model.generate_params()

initial_state = np.array([np.deg2rad(10),0.0])

times, angles, angular_velocities = model.simulate_rimless_wheel(
    initial_state,
    params,
    time_step=0.001,
    total_time=10.0)
'''