import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

import rimless_wheel_1 as model


# ============================================================
# Simulate and record impact velocities
# ============================================================

def get_impact_velocities(
    initial_state,
    params,
    time_step,
    total_time
):
    """
    Simulate the rimless wheel using the adaptive
    event-aware simulation and return the angular
    velocity immediately before each impact.
    """

    (
        times,
        angles,
        angular_velocities,
        impact_velocities
    ) = model.simulate_rimless_wheel(
        initial_state,
        params,
        time_step,
        total_time
    )

    return (
        np.array(impact_velocities),
        np.column_stack((
            angles,
            angular_velocities
        ))
    )


# ============================================================
# Classify initial condition
# ============================================================

def classify_state(
    initial_state,
    params,
    time_step,
    total_time
):
    """
    Classify an initial condition as:

        -1 = unclassified
        0 = stable fixed point
        1 = stable limit cycle
    """

    impact_velocities, state_history = get_impact_velocities(
        initial_state,
        params,
        time_step,
        total_time
    )

    # ========================================================
    # Check for convergence to a fixed point
    # ========================================================

    num_tail_states = int(
        0.2 * len(state_history)
    )

    tail_states = state_history[-num_tail_states:]

    theta_tail = tail_states[:, 0]
    theta_dot_tail = tail_states[:, 1]

    theta_range = (
        np.max(theta_tail) -
        np.min(theta_tail)
    )

    theta_dot_range = (
        np.max(theta_dot_tail) -
        np.min(theta_dot_tail)
    )

    if (
        theta_range < 0.01
        and theta_dot_range < 0.01
        and np.max(np.abs(theta_dot_tail)) < 0.01
    ):
        return 0

    # ========================================================
    # Check for convergence to a periodic rolling gait
    # ========================================================

    if len(impact_velocities) < 10:
        return -1

    tail = impact_velocities[-10:]

    if np.max(tail) - np.min(tail) < 0.05:
        return 1

    return -1


# ============================================================
# Compute RoA classification over a state-space grid
# ============================================================

def compute_roa(
    params,
    theta_values,
    theta_dot_values
):
    """
    Compute the behavioral classification over
    the entire state-space grid.
    """

    results = -np.ones(
        (
            len(theta_values),
            len(theta_dot_values)
        )
    )

    for i, theta in enumerate(theta_values):

        print(
            f"Row {i + 1}/{len(theta_values)}"
        )

        for j, theta_dot in enumerate(theta_dot_values):

            initial_state = np.array([
                theta,
                theta_dot
            ])

            classification = classify_state(
                initial_state,
                params,
                time_step=0.01,
                total_time=20.0
            )

            results[i, j] = classification

    return results


# ============================================================
# Print sweep summary
# ============================================================

def print_sweep_summary(
    parameter_values,
    results_list,
    parameter_name
):
    """
    Print summary statistics for an entire
    parameter sweep.
    """

    print("\n")
    print("============================================================")
    print(f"{parameter_name} SWEEP SUMMARY")
    print("============================================================")

    total_states = results_list[0].size

    for value, results in zip(
        parameter_values,
        results_list
    ):

        num_fixed_point = np.sum(
            results == 0
        )

        num_limit_cycle = np.sum(
            results == 1
        )

        num_unclassified = np.sum(
            results == -1
        )

        fixed_point_percent = (
            100 * num_fixed_point / total_states
        )

        limit_cycle_percent = (
            100 * num_limit_cycle / total_states
        )

        unclassified_percent = (
            100 * num_unclassified / total_states
        )

        print(
            f"{parameter_name} = {value}"
        )

        print(
            f"  Stable fixed point: "
            f"{num_fixed_point:5d} "
            f"({fixed_point_percent:6.2f}%)"
        )

        print(
            f"  Stable limit cycle: "
            f"{num_limit_cycle:5d} "
            f"({limit_cycle_percent:6.2f}%)"
        )

        print(
            f"  Unclassified:       "
            f"{num_unclassified:5d} "
            f"({unclassified_percent:6.2f}%)"
        )

        print()


params = model.generate_params()

params["slope_angle"] = np.deg2rad(18)

params["num_spokes"] = 8

alpha = np.pi / params["num_spokes"]

gamma = params["slope_angle"]

# ============================================================
# State-space grid
# ============================================================

# Fixed initial-condition grid for all sweeps
theta_values = np.linspace(
    np.deg2rad(18) - np.pi / 8,
    np.deg2rad(18) + np.pi / 8,
    100
)

theta_dot_values = np.linspace(
    -5,
    5,
    100
)

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
    "gray",       # -1 = unclassified
    "blue",       #  0 = stable fixed point
    "orange"      #  1 = stable limit cycle
])


# ============================================================
# SWEEP 1: Slope inclination
# ============================================================

slope_angles_deg = np.arange(
    5,
    36,
    5
)

slope_results = []

for slope_deg in slope_angles_deg:

    print("\n===================================")
    print(f"Slope = {slope_deg} degrees")
    print("===================================")

    params["slope_angle"] = np.deg2rad(
        slope_deg
    )

    params["num_spokes"] = 8

    results = compute_roa(
        params,
        theta_values,
        theta_dot_values
    )

    slope_results.append(results)


# ============================================================
# Console summary: slope sweep
# ============================================================

print_sweep_summary(
    slope_angles_deg,
    slope_results,
    "Slope"
)


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

    plot_results = (
        slope_results[k] + 1
    )

    im = ax.imshow(
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
    ticks=[0, 1, 2],
    shrink=0.85,
    pad=0.03
)

cbar.ax.set_yticklabels([
    "Unclassified",
    "Stable fixed point",
    "Stable limit cycle"
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
    "s11_RoA_Slope_Sweep.png",
    dpi=300
)

plt.close()

print("\nSlope sweep complete.")
print("Saved: RoA Slope Sweep.png")


# ============================================================
# SWEEP 2: Number of spokes
# ============================================================

spoke_numbers = np.arange(
    6,
    13
)

spoke_results = []

for num_spokes in spoke_numbers:

    print("\n===================================")
    print(
        f"Number of spokes = {num_spokes}"
    )
    print("===================================")

    params["slope_angle"] = np.deg2rad(20)

    params["num_spokes"] = num_spokes

    results = compute_roa(
        params,
        theta_values,
        theta_dot_values
    )

    spoke_results.append(results)


# ============================================================
# Console summary: spoke sweep
# ============================================================

print_sweep_summary(
    spoke_numbers,
    spoke_results,
    "Number of spokes"
)


# ============================================================
# Plot spoke sweep
# ============================================================

fig, axes = plt.subplots(
    2,
    4,
    figsize=(17, 8)
)

axes = axes.flatten()

for k, num_spokes in enumerate(
    spoke_numbers
):

    ax = axes[k]

    plot_results = (
        spoke_results[k] + 1
    )

    im = ax.imshow(
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

    ax.set_title(
        f"N = {num_spokes} spokes"
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
    ticks=[0, 1, 2],
    shrink=0.85,
    pad=0.03
)

cbar.ax.set_yticklabels([
    "Unclassified",
    "Stable fixed point",
    "Stable limit cycle"
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
    "s11_RoA_Spoke_Sweep.png",
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