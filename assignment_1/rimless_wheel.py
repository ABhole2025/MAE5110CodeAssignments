import matplotlib.pyplot as plt
import numpy as np

from integrators import rk4


def rimless_wheel_continuous(t, state, params):
    """
    Continuous dynamics of the rimless wheel while pivoting
    on the stance spoke.
    """
    theta, theta_dot = state

    g = params["gravity"]
    l = params["spoke_length"]
    gamma = params["slope_angle"]

    # Equation of motion
    theta_ddot = (g / l) * np.sin(theta+gamma)

    return np.array([theta_dot, theta_ddot])


def generate_params():
    return {
        "gravity": 9.81,
        "spoke_length": 1.0,
        "slope_angle": np.deg2rad(20),  # 20 degrees, converted to radians
        "num_spokes": 8
    }


def detect_impact(wheel_state, params):
    """
    Return True when the stance spoke reaches the impact angle +alpha.
    """
    theta, theta_dot = wheel_state

    num_spokes = params["num_spokes"]
    alpha = np.pi / num_spokes

    return theta >= alpha


def spoke_reset(wheel_state, params):
    """
    Reset dynamics at impact.

    The new stance spoke is 2*alpha away from the old one,
    so the coordinate changes by -2*alpha.

    Angular momentum conservation gives:
        theta_dot_plus = theta_dot_minus * cos(2*alpha)
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

        # Record the current state
        times[step] = current_time
        angles[step] = wheel_state[0]
        angular_velocities[step] = wheel_state[1]

        # Check for an impact
        if detect_impact(wheel_state, params):
            wheel_state = spoke_reset(wheel_state, params)

        # Integrate the continuous dynamics
        wheel_state = rk4(
            current_time,
            wheel_state,
            time_step,
            rimless_wheel_continuous,
            params
        )

        current_time += time_step

    return times, angles, angular_velocities


params = generate_params()
params["slope_angle"] = np.deg2rad(40)

initial_state = np.array([np.deg2rad(0), 0.0])

times, angles, angular_velocities = simulate_rimless_wheel(
    initial_state,
    params,
    time_step=0.001,
    total_time=2.0
)

plt.plot(times, angles)
plt.xlabel("Time (s)")
plt.ylabel("Theta (rad)")
plt.title("Rimless Wheel Angle")
plt.savefig("Rimless Wheel Angle")
plt.close()

'''
params = generate_params()

alpha = np.pi / params["num_spokes"]

before = np.array([alpha, 2.0])
after = spoke_reset(before, params)

print("Before:", before)
print("After:", after)
'''
'''
for N in [4, 8, 16]:
    params = generate_params()
    params["num_spokes"] = N

    alpha = np.pi / N

    print("N =", N, "alpha =", alpha)
'''

