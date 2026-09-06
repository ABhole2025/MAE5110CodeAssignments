import matplotlib.pyplot as plt
import numpy as np
import rimless_wheel as model

from integrators import rk4


def angle_difference(a, b):
    return (a - b + np.pi) % (2 * np.pi) - np.pi

params = model.generate_params()

params["slope_angle"] = np.deg2rad(20)

params["num_spokes"] = 8

# State-space grid
alpha = np.pi / params["num_spokes"]
gamma = params["slope_angle"]

theta_values = np.linspace(0, 2*np.pi, 360, endpoint=False)

theta_dot_values = np.linspace(0, 18, 360)

results = -np.ones(
    (len(theta_values), len(theta_dot_values))
)


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
            wheel_state = model.spoke_reset(wheel_state, params)

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

unclassified_states = []

for i, theta in enumerate(theta_values):
    print(f"Row {i + 1}/{len(theta_values)}")

    for j, theta_dot in enumerate(theta_dot_values):
        initial_state = np.array([theta, theta_dot])

        classification = classify_state(
            initial_state,
            params,
            time_step=0.005,
            total_time=20.0
        )

        results[i, j] = classification

        if classification == -1 and abs(angle_difference(theta, -gamma)) > 1e-6:  # noqa: SIM102
            if len(unclassified_states) < 20:
                unclassified_states.append(initial_state.copy())

print("Number of equilibrium points:", np.sum(results == 0))
print("Number of limit-cycle points:", np.sum(results == 1))
print("Number of unclassified points:", np.sum(results == -1))


print("\nExample unclassified states:")

for state in unclassified_states:
    print(
        "theta =",
        np.rad2deg(state[0]),
        "theta_dot =",
        state[1]
    )


from matplotlib.colors import ListedColormap

cmap = ListedColormap([
    "gray",    # -1 = unclassified
    "blue",    #  0 = equilibrium
    "orange"   #  1 = limit cycle
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
plt.title("Rimless Wheel Region of Attraction")

cbar = plt.colorbar(
    ticks=[0, 1, 2]
)

cbar.ax.set_yticklabels([
    "Unclassified",
    "Equilibrium",
    "Limit cycle"
])

cbar.set_label("Attractor")

plt.savefig("Rimless Wheel RoA.png", dpi=300)
plt.close()