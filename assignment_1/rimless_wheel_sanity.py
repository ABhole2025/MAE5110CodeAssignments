import matplotlib.pyplot as plt
import numpy as np
import rimless_wheel as model

# ============================================================
# Sanity Check 1: Full rimless-wheel simulation
# ============================================================

params = model.generate_params()
params["slope_angle"] = np.deg2rad(10)

initial_state = np.array([np.deg2rad(0.5), 2.0])

times, angles, angular_velocities = model.simulate_rimless_wheel(
    initial_state,
    params,
    time_step=0.001,
    total_time=10.0
)

plt.figure()
plt.plot(times, angles)
plt.xlabel("Time (s)")
plt.ylabel(r"$\theta$ (rad)")
plt.title("Rimless Wheel Angle")
plt.grid()
plt.savefig("Rimless Wheel Angle.png")
plt.close()


# ============================================================
# Sanity Check 2: Impact/reset
# ============================================================

alpha = np.pi / params["num_spokes"]
gamma = params["slope_angle"]

impact_angle = -gamma + 2 * alpha

# Artificial pre-impact state
theta_dot_before = 2.0
before = np.array([impact_angle, theta_dot_before])

# Apply the reset
after = model.spoke_reset(before, params)

# Calculate expected values
expected_theta = impact_angle - 2 * alpha
expected_theta_dot = theta_dot_before * np.cos(2 * alpha)

print("\nImpact/reset sanity check:")

print(
    f"Before: theta = {np.rad2deg(before[0]):.2f}°, "
    f"theta_dot = {before[1]:.3f} rad/s"
)

print(
    f"After:  theta = {np.rad2deg(after[0]):.2f}°, "
    f"theta_dot = {after[1]:.3f} rad/s"
)

print(
    f"Expected theta = {np.rad2deg(expected_theta):.2f}°"
)

print(
    f"Expected theta_dot = {expected_theta_dot:.3f} rad/s"
)


# ============================================================
# Sanity Check 3: Slope-angle sweep
# ============================================================

plt.figure()

for gamma_deg in [0, 50, 89]:

    params = model.generate_params()
    params["slope_angle"] = np.deg2rad(gamma_deg)

    initial_state = np.array([0.0, 2.0])

    times, angles, angular_velocities = model.simulate_rimless_wheel(
        initial_state,
        params,
        time_step=0.001,
        total_time=10.0
    )

    # Convert theta to angle measured from the slope normal
    normal_angle = angles + params["slope_angle"]

    plt.plot(
        times,
        angles,
        label=f"{gamma_deg}°: theta (global vertical)"
    )

    plt.plot(
        times,
        normal_angle,
        "--",
        label=f"{gamma_deg}°: angle from normal"
    )

plt.xlabel("Time (s)")
plt.ylabel("Angle (rad)")
plt.title("Rimless Wheel: Global Angle and Slope-Normal Angle")
plt.legend()
plt.grid()
plt.savefig("Rimless Wheel Slope Sweep.png")
plt.close()