import matplotlib.pyplot as plt
import numpy as np

import rimless_wheel as model

from integrators import rk4


# ============================================================
# Parameters
# ============================================================

params = model.generate_params()

params["slope_angle"] = np.deg2rad(40)

initial_state = np.array([
    np.deg2rad(-40),
    0])

# ============================================================
# Sanity Check 1: Angle vs. time
# ============================================================

times, angles, angular_velocities = model.simulate_rimless_wheel(
    initial_state,
    params,
    time_step=0.001,
    total_time=5.0
)

print("theta:", np.rad2deg(angles[:10]))
print("theta_dot:", angular_velocities[:10])

plt.figure()

plt.plot(
    times,
    angles)

plt.xlabel("Time (s)")
plt.ylabel(r"$\theta$ (rad)")
plt.title("Rimless Wheel Angle")

plt.grid()

plt.savefig(
    "Rimless Wheel Angle.png")

plt.close()


# ============================================================
# Sanity Check 2: Theta vs. theta_dot
# ============================================================

# Choose ONE initial condition at a time here.
# Change these values when you want to test another state.

params = model.generate_params()
params["slope_angle"] = np.deg2rad(40)

theta_deg = 10
theta_dot = 0

initial_state = np.array([
    np.deg2rad(theta_deg),
    theta_dot])

times, angles, angular_velocities = model.simulate_rimless_wheel(
    initial_state,
    params,
    time_step=0.001,
    total_time=20.0)

plt.figure()

plt.plot(
    np.rad2deg(angles),
    angular_velocities)

plt.xlabel(r"$\theta$ (degrees)")
plt.ylabel(r"$\dot{\theta}$ (rad/s)")
plt.title(
    f"Rimless Wheel Phase Portrait: "
    f"({theta_deg}°, {theta_dot} rad/s)")
plt.grid()
plt.savefig("Rimless Wheel Phase Portrait.png")
plt.close()


