import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

import rimless_wheel as model
from integrators import rk4


def angle_difference(a, b):
    return (a - b + np.pi) % (2 * np.pi) - np.pi

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

            impact_velocities.append(wheel_state[1])


            wheel_state = model.spoke_reset(wheel_state,params)

        wheel_state = rk4(current_time, wheel_state, time_step, model.rimless_wheel_continuous, params)

        current_time += time_step

    return np.array(impact_velocities)


# ============================================================
# Classify initial condition
# ============================================================

def classify_state(initial_state, params, time_step, total_time):
    """
    Classification:

        -1 = unclassified
        0 = equilibrium
        1 = bounded rocking
        2 = periodic rolling gait
    """

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
    # It therefore remains on the same spoke and rocks around
    # the equilibrium.
    # --------------------------------------------------------

    E = stance_energy(initial_state, params)

    E_impact = impact_energy(params)

    if E < E_impact:
        return 1

    # --------------------------------------------------------
    # 2 = periodic rolling gait
    #
    # The trajectory has enough energy to reach impact.
    # --------------------------------------------------------

    impact_velocities = get_impact_velocities(initial_state, params, time_step, total_time)

    if len(impact_velocities) < 5:
        return -1

    tail = impact_velocities[-5:]

    if np.max(tail) - np.min(tail) < 0.05:
        return 2

    return -1


# ============================================================
# Compute RoA classification over a state-space grid
# ============================================================

def compute_roa(params, theta_values, theta_dot_values):
    """
    Compute the behavioral classification over the
    entire state-space grid.
    """

    results = -np.ones((len(theta_values),len(theta_dot_values)))

    for i, theta in enumerate(theta_values):

        print(f"Row {i + 1}/{len(theta_values)}")

        for j, theta_dot in enumerate(theta_dot_values):

            initial_state = np.array([theta, theta_dot])

            classification = classify_state(initial_state, params, time_step=0.005, total_time=20.0)

            results[i, j] = classification

    return results


# ============================================================
# Print sweep summary
# ============================================================

def print_sweep_summary(parameter_values, results_list, parameter_name):
    """
    Print summary statistics for an entire parameter sweep.
    """

    print("\n\n")
    print("============================================================")
    print(f"{parameter_name} SWEEP SUMMARY")
    print("============================================================")

    total_states = results_list[0].size

    for value, results in zip(parameter_values, results_list):

        num_equilibrium = np.sum(results == 0)

        num_bounded_rocking = np.sum(results == 1)

        num_limit_cycle = np.sum(results == 2)

        num_unclassified = np.sum(results == -1)

        equilibrium_percent = (100 * num_equilibrium / total_states)

        bounded_rocking_percent = (100 * num_bounded_rocking / total_states)

        limit_cycle_percent = (100 * num_limit_cycle / total_states)

        unclassified_percent = (100 * num_unclassified / total_states)

        print(f"{parameter_name} = {value}")

        print(f"  Equilibrium:      " f"{num_equilibrium:5d} " f"({equilibrium_percent:6.2f}%)")

        print(f"  Bounded rocking:  " f"{num_bounded_rocking:5d} " f"({bounded_rocking_percent:6.2f}%)")

        print(f"  Limit cycle:      " f"{num_limit_cycle:5d} " f"({limit_cycle_percent:6.2f}%)")

        print(f"  Unclassified:     " f"{num_unclassified:5d} " f"({unclassified_percent:6.2f}%)")

        print()


# ============================================================
# State-space grid
# ============================================================

theta_values = np.linspace(-np.pi, np.pi, 100, endpoint=False)

theta_dot_values = np.linspace( -10, 10, 100)


# ============================================================
# Initial parameters
# ============================================================

params = model.generate_params()

params["slope_angle"] = np.deg2rad(20)
params["num_spokes"] = 8


# ============================================================
# Color map
# ============================================================

cmap = ListedColormap([
    "gray",      # -1 = unclassified
    "blue",      #  0 = equilibrium
    "green",     #  1 = bounded rocking
    "orange"     #  2 = limit cycle
])


# ============================================================
# SWEEP 1: Slope inclination
# ============================================================

slope_angles_deg = np.arange(5,36,5)

slope_results = []

for slope_deg in slope_angles_deg:

    print("\n===================================")
    print(f"Slope = {slope_deg} degrees")
    print("===================================")

    params["slope_angle"] = np.deg2rad(
        slope_deg)

    params["num_spokes"] = 8

    results = compute_roa(params, theta_values, theta_dot_values)

    slope_results.append(results)


# ============================================================
# Console summary: slope sweep
# ============================================================

print_sweep_summary(slope_angles_deg, slope_results, "Slope")


# ============================================================
# Plot slope sweep
# ============================================================

fig, axes = plt.subplots(
    2,
    4,
    figsize=(17, 8)
)

axes = axes.flatten()

for k, slope_deg in enumerate(
    slope_angles_deg
):

    ax = axes[k]

    plot_results = slope_results[k] + 1

    im = ax.imshow(
        plot_results.T,
        origin="lower",
        extent=[
            -180,
            180,
            -10,
            10
        ],
        aspect="auto",
        cmap=cmap,
        vmin=0,
        vmax=3
    )

    ax.set_title(
        f"Slope = {slope_deg}°"
    )

    ax.set_xlabel(
        r"$\theta$ (degrees)"
    )

    ax.set_ylabel(
        r"$\dot{\theta}$ (rad/s)"
    )

    ax.set_xticks([
        -180,
        -90,
        0,
        90,
        180
    ])

    ax.set_yticks([
        -10,
        -5,
        0,
        5,
        10
    ])


axes[-1].axis("off")


cbar = fig.colorbar(
    im,
    ax=axes,
    ticks=[0, 1, 2, 3],
    shrink=0.85,
    pad=0.03
)

cbar.ax.set_yticklabels([
    "Unclassified",
    "Equilibrium",
    "Bounded rocking",
    "Limit cycle"
])

cbar.set_label(
    "Classification"
)

fig.suptitle(
    "Rimless Wheel RoA vs. Slope Inclination",
    fontsize=16
)

plt.tight_layout()

plt.savefig(
    "RoA%20Slope%20Sweep.png",
    dpi=300
)

plt.close()

print("\nSlope sweep complete.")
print("Saved: RoA Slope Sweep.png")


# ============================================================
# SWEEP 2: Number of spokes
# ============================================================

spoke_numbers = np.arange(6, 13)

spoke_results = []

for N in spoke_numbers:

    print("\n===================================")
    print(f"Number of spokes = {N}")
    print("===================================")

    params["slope_angle"] = np.deg2rad(20)

    params["num_spokes"] = N

    results = compute_roa(params, theta_values, theta_dot_values)

    spoke_results.append(results)


# ============================================================
# Console summary: spoke sweep
# ============================================================

print_sweep_summary(spoke_numbers, spoke_results, "Number of spokes")


# ============================================================
# Plot spoke sweep
# ============================================================

fig, axes = plt.subplots(
    2,
    4,
    figsize=(17, 8)
)

axes = axes.flatten()

for k, N in enumerate(
    spoke_numbers
):

    ax = axes[k]

    plot_results = spoke_results[k] + 1

    im = ax.imshow(
        plot_results.T,
        origin="lower",
        extent=[
            -180,
            180,
            -10,
            10
        ],
        aspect="auto",
        cmap=cmap,
        vmin=0,
        vmax=3
    )

    ax.set_title(
        f"N = {N} spokes"
    )

    ax.set_xlabel(
        r"$\theta$ (degrees)"
    )

    ax.set_ylabel(
        r"$\dot{\theta}$ (rad/s)"
    )

    ax.set_xticks([
        -180,
        -90,
        0,
        90,
        180
    ])

    ax.set_yticks([
        -10,
        -5,
        0,
        5,
        10
    ])


axes[-1].axis("off")


cbar = fig.colorbar(
    im,
    ax=axes,
    ticks=[0, 1, 2, 3],
    shrink=0.85,
    pad=0.03
)

cbar.ax.set_yticklabels([
    "Unclassified",
    "Equilibrium",
    "Bounded rocking",
    "Limit cycle"
])

cbar.set_label(
    "Classification"
)

fig.suptitle(
    "Rimless Wheel RoA vs. Number of Spokes",
    fontsize=16
)

plt.tight_layout()

plt.savefig(
    "RoA%20Spoke%20Sweep.png",
    dpi=300
)

plt.close()

print("\nSpoke sweep complete.")
print("Saved: RoA Spoke Sweep.png")


# ============================================================
# Complete
# ============================================================

print("\n============================================================")
print("ALL RoA SWEEPS COMPLETE")
print("============================================================")