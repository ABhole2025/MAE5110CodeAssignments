import matplotlib.pyplot as plt
import numpy as np

from integrators import rk4


def generate_params():
    return {
        "gravity": 9.81,
        "spoke_length": 1.0,
        "slope_angle": np.deg2rad(20),  # 20 degrees, converted to radians
        "num_spokes": 8
    }

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

    return theta >= impact_angle


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



# Sanity Checks

params = generate_params()
params["slope_angle"] = np.deg2rad(10)

initial_state = np.array([np.deg2rad(0.5), 2])

# Run simulation
times, angles, angular_velocities = simulate_rimless_wheel(
    initial_state,
    params,
    time_step=0.001,
    total_time=5.0
)

# Plot angle vs time
plt.plot(times, angles)
plt.xlabel("Time (s)")
plt.ylabel("Theta (rad)")
plt.title("Rimless Wheel Angle")
plt.savefig("Rimless Wheel Angle")
plt.close()



# Impact/reset check

alpha = np.pi / params["num_spokes"]
gamma = params["slope_angle"]

impact_angle = -gamma + 2 * alpha

# Artificial pre-impact state
theta_dot_before = 2.0
before = np.array([impact_angle, theta_dot_before])

# Apply impact reset
after = spoke_reset(before, params)

print("\nImpact reset sanity check:")
print(f"Before: theta = {np.rad2deg(before[0]):.2f}°, "
        f"theta_dot = {before[1]:.3f} rad/s")

print(f"After:  theta = {np.rad2deg(after[0]):.2f}°, "
        f"theta_dot = {after[1]:.3f} rad/s")

# Expected values
expected_theta = impact_angle - 2 * alpha
expected_theta_dot = theta_dot_before * np.cos(2 * alpha)

print(f"Expected theta = {np.rad2deg(expected_theta):.2f}°")
print(f"Expected theta_dot = {expected_theta_dot:.3f} rad/s")



# slope angle sweep
for gamma_deg in [0, 50, 89]:
    params = generate_params()
    params["slope_angle"] = np.deg2rad(gamma_deg)

    initial_state_sweep = np.array([np.deg2rad(0), 2])

    times, angles, angular_velocities = simulate_rimless_wheel(
        initial_state_sweep,
        params,
        time_step=0.001,
        total_time=5.0
    )

    # Angle relative to the slope normal
    normal_angle = angles + params["slope_angle"]

    plt.plot(times, angles, label=f"{gamma_deg}°: theta (global vertical)")
    plt.plot(times, normal_angle, "--",
            label=f"{gamma_deg}°: angle from normal")

plt.xlabel("Time (s)")
plt.ylabel("Angle (rad)")
plt.title("Rimless Wheel: Global Angle and Angle Relative to Slope Normal")
plt.savefig("Rimless Wheel: Global Angle and Angle Relative to Slope Normal")
plt.close()
