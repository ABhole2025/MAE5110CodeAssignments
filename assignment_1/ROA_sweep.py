import matplotlib.pyplot as plt
import numpy as np
import rimless_wheel as model

from integrators import rk4
from matplotlib.colors import ListedColormap


def angle_difference(a, b):
    return (a - b + np.pi) % (2 * np.pi) - np.pi


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

            # Apply impact reset
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


def classify_state(initial_state, params, time_step, total_time):

    gamma = params["slope_angle"]

    theta0, theta_dot0 = initial_state

    # Check for the equilibrium
    if (
        abs(angle_difference(theta0, -gamma)) < 1e-3
        and abs(theta_dot0) < 1e-3
    ):
        return 0

    impact_velocities = get_impact_velocities(
        initial_state,
        params,
        time_step,
        total_time
    )

    # If there aren't enough impacts, we can't classify it
    if len(impact_velocities) < 5:
        return -1

    # Look at the final few impact velocities
    tail = impact_velocities[-5:]

    # Check whether they have settled to approximately
    # the same value
    if np.max(tail) - np.min(tail) < 0.05:
        return 1

    return -1


def compute_roa(params, theta_values, theta_dot_values):
    """
    Compute the RoA classification over the entire state-space grid.
    """

    results = -np.ones(
        (len(theta_values), len(theta_dot_values))
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
                time_step=0.005,
                total_time=20.0
            )

            results[i, j] = classification

    return results


# ---------------------------------------------------------
# State-space grid
# ---------------------------------------------------------

theta_values = np.linspace(
    -np.pi,
    np.pi,
    101,
    endpoint=False
)

theta_dot_values = np.linspace(
    0,
    18,
    101
)


# ---------------------------------------------------------
# Initial parameters
# ---------------------------------------------------------

params = model.generate_params()

params["slope_angle"] = np.deg2rad(20)
params["num_spokes"] = 8

# ---------------------------------------------------------
# Sweep slope inclination
# ---------------------------------------------------------

slope_angles_deg = np.arange(5, 36, 5)

slope_results = []

for slope_deg in slope_angles_deg:

    print("\n===================================")
    print(f"Slope = {slope_deg} degrees")
    print("===================================")

    params["slope_angle"] = np.deg2rad(slope_deg)
    params["num_spokes"] = 8

    results = compute_roa(
        params,
        theta_values,
        theta_dot_values
    )

    slope_results.append(results)

# ---------------------------------------------------------
# Plot slope sweep
# ---------------------------------------------------------

cmap = ListedColormap([
    "gray",      # -1 = unclassified
    "blue",      #  0 = equilibrium
    "orange"     #  1 = limit cycle
])

fig, axes = plt.subplots(
    2,
    4,
    figsize=(16, 8),
    sharex=True,
    sharey=True
)

axes = axes.flatten()

for k, slope_deg in enumerate(slope_angles_deg):

    ax = axes[k]

    plot_results = slope_results[k] + 1

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

    ax.set_xlabel(r"$\theta$ (degrees)")
    ax.set_ylabel(r"$\dot{\theta}$ (rad/s)")


# Hide unused 8th subplot
axes[-1].axis("off")


# Shared colorbar
cbar = fig.colorbar(
    im,
    ax=axes.tolist(),
    ticks=[0, 1, 2],
    shrink=0.9
)

cbar.ax.set_yticklabels([
    "Unclassified",
    "Equilibrium",
    "Limit cycle"
])

cbar.set_label("Attractor")


fig.suptitle(
    "Rimless Wheel RoA vs. Slope Inclination",
    fontsize=16
)

plt.tight_layout()

plt.savefig(
    "RoA Slope Sweep.png",
    dpi=300
)

plt.close()