import matplotlib.pyplot as plt

import numpy as np

import rimless_wheel_1 as model


# ============================================================
# Parameters
# ============================================================

params = model.generate_params()

params["slope_angle"] = np.deg2rad(10)

params["num_spokes"] = 8

alpha = np.pi / params["num_spokes"]

gamma = params["slope_angle"]


# ============================================================
# State-space grid
# ============================================================

theta_values = np.linspace(gamma - alpha,gamma + alpha,100)

theta_dot_values = np.linspace(-5,5,40)

results = -np.ones((len(theta_values), len(theta_dot_values)))


# ============================================================
# Simulate and record impact velocities
# ============================================================

def get_impact_velocities(initial_state,params,time_step,total_time):

    """
    Simulate the rimless wheel using the adaptive
    event-aware simulation and return the angular
    velocity immediately before each impact.
    """

    (times,angles,angular_velocities,impact_velocities) = model.simulate_rimless_wheel(initial_state,params,time_step,total_time)

    return (np.array(impact_velocities),np.column_stack((angles,angular_velocities)))


# ============================================================
# Classify initial condition
# ============================================================

def classify_state(initial_state,params,time_step,total_time):

    """
    Classify an initial condition as:

        -1 = unclassified
        0 = stable fixed point
        1 = stable limit cycle
    """

    impact_velocities, state_history = get_impact_velocities(initial_state,params,time_step,total_time)


    # ========================================================
    # Check for convergence to a fixed point
    # ========================================================


    num_tail_states = int(0.2 * len(state_history))

    tail_states = state_history[-num_tail_states:]

    theta_tail = tail_states[:, 0]

    theta_dot_tail = tail_states[:, 1]

    theta_range = (np.max(theta_tail) - np.min(theta_tail))

    theta_dot_range = (np.max(theta_dot_tail) - np.min(theta_dot_tail))

    if (theta_range < 0.01and theta_dot_range < 0.01and np.max(np.abs(theta_dot_tail)) < 0.01):

        return 0


    # ========================================================
    # Check for convergence to a periodic rolling gait
    # ========================================================

    # Need at least 10 impacts to establish a gait

    if len(impact_velocities) < 10:

        return -1

    # Use the final 10 impact velocities

    tail = impact_velocities[-10:]

    # Check whether the impact velocity has converged

    if np.max(tail) - np.min(tail) < 0.05:

        return 1

    return -1


# ============================================================
# Brute-force state-space sweep
# ============================================================

unclassified_states = []

for i, theta in enumerate(theta_values):

    print(f"Row {i + 1}/{len(theta_values)}")

    for j, theta_dot in enumerate(theta_dot_values):

        initial_state = np.array([theta,theta_dot])

        classification = classify_state(initial_state,params,time_step=0.01,total_time=20.0)

        results[i, j] = classification

        if (classification == -1 and len(unclassified_states) < 20):

            unclassified_states.append(initial_state.copy())


# ============================================================
# Results
# ============================================================

print("Number of stable fixed-point points:",np.sum(results == 0))

print("Number of periodic rolling gait points:",np.sum(results == 1))

print("Number of unclassified points:",np.sum(results == -1))


print("\nExample unclassified states:")

for state in unclassified_states:

    print("theta =",np.rad2deg(state[0]),"theta_dot =",state[1])


# ============================================================
# Plot
# ============================================================

from matplotlib.colors import ListedColormap

cmap = ListedColormap([
    "gray",       # -1 = unclassified
    "blue",       #  0 = stable fixed point
    "orange"      #  1 = periodic rolling gait
])

plot_results = results + 1

plt.figure(figsize=(9, 7))

plt.imshow(
    plot_results.T,
    origin="lower",
    extent=[
        np.rad2deg(theta_values[0]),
        np.rad2deg(theta_values[-1]),
        theta_dot_values[0],
        theta_dot_values[-1]
    ],
    aspect="auto",
    cmap=cmap,
    vmin=0,
    vmax=2
)

plt.xlabel(r"$\theta$ (degrees)")

plt.ylabel(r"$\dot{\theta}$ (rad/s)")

plt.title(
    "Rimless Wheel State-Space Classification"
)

cbar = plt.colorbar(
    ticks=[0, 1, 2]
)

cbar.ax.set_yticklabels([
    "Unclassified",
    "Stable fixed point",
    "Stable limit cycle"
])

cbar.set_label("Behavior")

plt.savefig(
    "Rimless_Wheel_RoA.png",
    dpi=300
)

plt.close()