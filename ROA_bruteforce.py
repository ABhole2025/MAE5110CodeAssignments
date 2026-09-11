import matplotlib.pyplot as plt
import numpy as np

import rimless_wheel as model
from integrators import rk4


def angle_difference(a, b):
    return (a - b + np.pi) % (2 * np.pi) - np.pi


# ============================================================
# Parameters
# ============================================================

params = model.generate_params()
params["slope_angle"] = np.deg2rad(20)
params["num_spokes"] = 8

alpha = np.pi / params["num_spokes"]
gamma = params["slope_angle"]

g = params["gravity"]
l = params["spoke_length"]


# ============================================================
# State-space grid
# ============================================================

theta_values = np.linspace(-np.pi, np.pi, 50, endpoint=False)
theta_dot_values = np.linspace(-10, 10, 50)

results = -np.ones(
    (len(theta_values), len(theta_dot_values)))


# ============================================================
# Energy of the continuous stance dynamics
# ============================================================

def stance_energy(state, params):
    theta, theta_dot = state

    g = params["gravity"]
    l = params["spoke_length"]
    gamma = params["slope_angle"]

    return (0.5 * theta_dot**2 - (g / l) * np.cos(theta + gamma))

# ============================================================
# Energy required to reach impact
# ============================================================

def impact_energy(params):
    alpha = np.pi / params["num_spokes"]

    g = params["gravity"]
    l = params["spoke_length"]

    return -(g / l) * np.cos(alpha)


# ============================================================
# Simulate and record impact velocities
# ============================================================

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

        if model.detect_impact(wheel_state, params):

            # Record velocity immediately before impact
            impact_velocities.append(wheel_state[1])

            wheel_state = model.spoke_reset(
                wheel_state,
                params
            )

        wheel_state = rk4(
            current_time,
            wheel_state,
            time_step,
            model.rimless_wheel_continuous,
            params
        )

        current_time += time_step

    return np.array(impact_velocities)


# ============================================================
# Classify initial condition
# ============================================================

def classify_state(initial_state, params, time_step, total_time):

    gamma = params["slope_angle"]

    theta0, theta_dot0 = initial_state

    # --------------------------------------------------------
    # 0 = equilibrium
    # --------------------------------------------------------

    if (abs(angle_difference(theta0, -gamma)) < 1e-3
        and abs(theta_dot0) < 1e-3):
        return 0

    # --------------------------------------------------------
    # 1 = bounded rocking
    #
    # If the initial energy is below the energy required to
    # reach the impact angle, the trajectory cannot impact.
    # Therefore it remains on the same spoke and rocks around
    # the equilibrium.
    # --------------------------------------------------------

    E = stance_energy(initial_state, params)
    E_impact = impact_energy(params)

    if E < E_impact:
        return 1

    # --------------------------------------------------------
    # 2 = periodic rolling gait
    #
    # This state has enough energy to reach impact.
    # --------------------------------------------------------

    impact_velocities = get_impact_velocities(initial_state, params, time_step, total_time)

    # Not enough impacts to establish a gait
    if len(impact_velocities) < 5:
        return -1

    # Look at final few impact velocities
    tail = impact_velocities[-5:]

    # Check convergence to the same pre-impact velocity
    if np.max(tail) - np.min(tail) < 0.05:
        return 2

    return -1


# ============================================================
# Brute-force state-space sweep
# ============================================================

unclassified_states = []

for i, theta in enumerate(theta_values):

    print(f"Row {i + 1}/{len(theta_values)}")

    for j, theta_dot in enumerate(theta_dot_values):

        initial_state = np.array([theta, theta_dot])

        classification = classify_state(initial_state, params, time_step=0.005, total_time=20.0)

        results[i, j] = classification

        if (classification == -1
            and len(unclassified_states) < 20):
            unclassified_states.append(initial_state.copy())


# ============================================================
# Results
# ============================================================

print("Number of equilibrium points:", np.sum(results == 0))

print("Number of bounded-rocking points:",np.sum(results == 1))

print("Number of limit-cycle points:",np.sum(results == 2))

print("Number of unclassified points:",np.sum(results == -1))


print("\nExample unclassified states:")

for state in unclassified_states:

    print("theta =", np.rad2deg(state[0]), "theta_dot =", state[1])


# ============================================================
# Plot
# ============================================================

from matplotlib.colors import ListedColormap

cmap = ListedColormap([
    "gray",      # -1 = unclassified
    "blue",      #  0 = equilibrium
    "green",     #  1 = bounded rocking
    "orange"     #  2 = periodic rolling gait
])


plot_results = results + 1

plt.figure(figsize=(9, 7))

plt.imshow(
    plot_results.T,
    origin="lower",
    extent=[
        -180,
        180,
        theta_dot_values[0],
        theta_dot_values[-1]
    ],
    aspect="auto",
    cmap=cmap,
    vmin=0,
    vmax=3
)

plt.xlabel(r"$\theta$ (degrees)")
plt.ylabel(r"$\dot{\theta}$ (rad/s)")
plt.title("Rimless Wheel State-Space Classification")

cbar = plt.colorbar(
    ticks=[0, 1, 2, 3]
)

cbar.ax.set_yticklabels([
    "Unclassified",
    "Equilibrium",
    "Bounded rocking",
    "Periodic rolling gait"
])

cbar.set_label("Behavior")

plt.savefig(
    "Rimless Wheel RoA.png",
    dpi=300
)

plt.close()