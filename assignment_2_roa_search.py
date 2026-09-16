from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from assignment_2_control import feedback_linearizing_controller
from models import inverted_pendulum_walker as model

params = {
    "gravity": 9.81,          # m/s^2
    "length": 1.0,             # m
    "mass": 1.0,               # kg
    "incline": 0.06,           # rad
    "angle_of_attack": np.pi / 8,   # rad
    "ankle_torque": 0.0,       # N m
}

kp = 4.0
kd = 2.0

# As this RoA is for the torque feedback only we keep alpha constant
alpha_min = np.pi / 8
params["angle_of_attack"] = alpha_min

# ------------------------------------------------------------
# Simulation settings
timestep = 1e-3
sim_time = 3.0

# Initial-condition grid.
resolution = 101 #odd number ensures 0,0 is included
theta_grid = np.linspace(-0.15, 0.07, resolution)
theta_dot_grid = np.linspace(-0.25, 0.35, resolution)

# A trajectory is classified as "stable" if its final states are
# close to the upright equilibrium.
tail_fraction = 0.20
theta_tolerance = 0.01
theta_dot_tolerance = 0.01

max_abs_theta = 2.0
max_abs_theta_dot = 10.0
# ------------------------------------------------------------


# simulation

def simulate_standing_controller(initial_state):
    local_params = params.copy()

    n_timesteps = round(sim_time / timestep)
    tail_length = max(1, round(tail_fraction * n_timesteps))

    state = np.asarray(initial_state, dtype=float).copy()

    tail_states = np.zeros((tail_length, 2))

    for index in range(n_timesteps):
        ankle_torque = feedback_linearizing_controller(state, local_params, kp, kd,)

        local_params["ankle_torque"] = ankle_torque

        next_state = state + timestep * model.dynamics(index * timestep, state, local_params,)

        # Stop early if the trajectory clearly leaves the local region.
        if (
            not np.all(np.isfinite(next_state))
            or abs(next_state[0]) > max_abs_theta
            or abs(next_state[1]) > max_abs_theta_dot
        ):
            return False

        state = next_state

        if index >= n_timesteps - tail_length:
            tail_index = index - (n_timesteps - tail_length)
            tail_states[tail_index] = state

    return (np.max(np.abs(tail_states[:, 0])) < theta_tolerance
        and np.max(np.abs(tail_states[:, 1])) < theta_dot_tolerance)



def classify_initial_condition(initial_condition):
    row, column, theta_dot_initial, theta_initial = initial_condition
    stable = simulate_standing_controller([theta_initial, theta_dot_initial])
    return row, column, stable



# RoA grid search

if __name__ == "__main__":
    initial_conditions = [(row, column, theta_dot_initial, theta_initial,)
        for row, theta_dot_initial in enumerate(theta_dot_grid)
        for column, theta_initial in enumerate(theta_grid)]

    stable_grid = np.zeros((len(theta_dot_grid), len(theta_grid)), dtype=bool,)

    with ProcessPoolExecutor() as executor:
        results = executor.map(classify_initial_condition, initial_conditions,)

        for count, (row, column, stable) in enumerate(results, start=1):
            stable_grid[row, column] = stable

            if count % 500 == 0:
                print(f"Completed {count}/{len(initial_conditions)} states")



    # Plot

    theta_mesh, theta_dot_mesh = np.meshgrid(theta_grid, theta_dot_grid,)

    plt.figure(figsize=(8, 6))

    binary_cmap = ListedColormap(["lightcoral", "lightgreen",])

    plt.pcolormesh(theta_mesh, theta_dot_mesh, stable_grid.astype(int), cmap=binary_cmap, vmin=0, vmax=1,shading="nearest",)

    plt.xlabel(r"$\theta$ [rad]")
    plt.ylabel(r"$\dot{\theta}$ [rad/s]")
    plt.title("Estimated RoA of the feedback-linearizing standing controller")

    colorbar = plt.colorbar(ticks=[0, 1],)

    colorbar.ax.set_yticklabels(["Not stable", "Stable",])

    plt.tight_layout()
    plt.savefig("Estimated_RoA_of_the_feedback-linearizing_standing_controller", dpi=300,)
    plt.show()
