import time
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import numpy as np

from models import inverted_pendulum_walker as model

params = model.generate_params()

roa_data = np.load("standing_roa.npz")

stable_grid = roa_data["stable_grid"]
roa_theta_grid = roa_data["theta_grid"]
roa_theta_dot_grid = roa_data["theta_dot_grid"]

timestep = 1e-3
sim_time = 5.0

section_theta = 0.0

g = params["gravity"]
l = params["length"]

theta_dot_max = np.sqrt(2 * g / l)

def make_grids(num_state_points, num_alpha_points):
    state_grid = np.linspace(0.0,theta_dot_max,num_state_points,)

    alpha_grid = np.linspace(np.pi / 8,np.pi / 7,num_alpha_points,)

    return state_grid, alpha_grid

def poincare_section_crossed(previous_state, next_state):
    previous_theta = previous_state[0]
    next_theta = next_state[0]

    return (previous_theta < section_theta and next_theta >= section_theta)


def simulate_one_step(theta_dot_initial, alpha):
    local_params = params.copy()
    local_params["angle_of_attack"] = alpha

    n_timesteps = round(sim_time / timestep)

    # Start on the Poincaré section
    state = np.array([section_theta, theta_dot_initial], dtype=float)

    for index in range(n_timesteps):
        next_state = state + timestep * model.dynamics(index * timestep, state, local_params,)

        # Check for impact
        if model.event_guard(state, next_state, local_params):
            next_state = model.event_dynamics(next_state, local_params,)

        # Check for the next Poincaré-section crossing
        if poincare_section_crossed(state, next_state):
            return next_state[1]

        state = next_state

    # No return to the Poincaré section
    return None


def simulate_state_action(theta_dot_initial, alpha):
    theta_dot_next = simulate_one_step(theta_dot_initial,alpha,)

    return theta_dot_initial, alpha, theta_dot_next


def in_roa(theta_dot):
    # Outside the range that was actually simulated
    if theta_dot < roa_theta_dot_grid.min():
        return False

    if theta_dot > roa_theta_dot_grid.max():
        return False

    # theta = 0 is Poincaré section
    theta_index = np.argmin(np.abs(roa_theta_grid - section_theta))

    # Find closest theta_dot grid point
    theta_dot_index = np.argmin(np.abs(roa_theta_dot_grid - theta_dot))

    return stable_grid[theta_dot_index, theta_index]


def build_state_action_table(state_grid, alpha_grid):
    table = np.full((len(state_grid), len(alpha_grid)),np.nan,)

    tasks = [(theta_dot_initial, alpha)
        for theta_dot_initial in state_grid
        for alpha in alpha_grid]

    total_tasks = len(tasks)
    completed = 0

    print(f"  Simulating {total_tasks:,} "f"state-action pairs...")

    start_time = time.time()

    with ProcessPoolExecutor() as executor:
        results = executor.map(simulate_state_action,[task[0] for task in tasks],[task[1] for task in tasks],)

        for theta_dot_initial, alpha, theta_dot_next in results:
            state_index = np.argmin(np.abs(state_grid - theta_dot_initial))

            alpha_index = np.argmin(np.abs(alpha_grid - alpha))

            if theta_dot_next is not None:
                table[state_index, alpha_index] = theta_dot_next

            completed += 1
            # Print every 5%
            if (completed % max(1, total_tasks // 20) == 0 or completed == total_tasks):

                percent = (100 * completed / total_tasks)

                elapsed = time.time() - start_time

                print(
                    f"\r  Progress: "
                    f"{percent:5.1f}% "
                    f"({completed:,}/{total_tasks:,}) "
                    f"Elapsed: {elapsed / 60:.1f} min",
                    end="",
                    flush=True,)

    print()

    return table


def find_steps_to_roa(state_action_table, state_grid, alpha_grid):

    steps_to_roa = np.full(len(state_grid), -1, dtype=int)
    best_alpha = np.full(len(state_grid), np.nan)

    for state_index, theta_dot in enumerate(state_grid):

        if in_roa(theta_dot):
            steps_to_roa[state_index] = 0

    current_step = 0

    while True:
        newly_reachable = 0

        for state_index in range(len(state_grid)):

            if steps_to_roa[state_index] != -1:
                continue

            for alpha_index, alpha in enumerate(alpha_grid):

                theta_dot_next = state_action_table[state_index, alpha_index]

                if not np.isfinite(theta_dot_next):
                    continue

                next_state_index = np.argmin(np.abs(state_grid - theta_dot_next))

                if steps_to_roa[next_state_index] == current_step:

                    steps_to_roa[state_index] = current_step + 1
                    best_alpha[state_index] = alpha

                    newly_reachable += 1
                    break

        if newly_reachable == 0:
            break

        current_step += 1

    return steps_to_roa, best_alpha


def simulate_controlled_trajectory(initial_theta_dot,initial_index,state_grid,alpha_grid,best_alpha,steps_to_roa,):
    """
    Simulate the walker while applying the Poincare policy.

    Returns the complete continuous trajectory and the
    Poincare-section crossing locations.
    """

    state = np.array([section_theta, initial_theta_dot],dtype=float,)

    time_values = [0.0]
    theta_values = [state[0]]
    theta_dot_values = [state[1]]

    section_states = [(0.0, state[0], state[1])]

    current_index = initial_index
    current_time = 0.0

    number_of_steps = steps_to_roa[initial_index]

    for step in range(number_of_steps):

        alpha = best_alpha[current_index]

        local_params = params.copy()
        local_params["angle_of_attack"] = alpha

        for _ in range(round(sim_time / timestep)):

            next_state = (state+ timestep* model.dynamics(current_time,state,local_params,))

            # Apply impact dynamics
            if model.event_guard(state,next_state,local_params,):
                next_state = model.event_dynamics(next_state,local_params,)

            current_time += timestep

            time_values.append(current_time)
            theta_values.append(next_state[0])
            theta_dot_values.append(next_state[1])

            # Check for next Poincare crossing
            if poincare_section_crossed(state,next_state,):

                state = next_state

                section_states.append((current_time,state[0],state[1],))

                # Find nearest state-grid point
                current_index = np.argmin(np.abs(state_grid - state[1]))

                break

            state = next_state

    return (
        np.array(time_values),
        np.array(theta_values),
        np.array(theta_dot_values),
        np.array(section_states),)



if __name__ == "__main__":
    alpha_range = np.pi / 7 - np.pi / 8

    num_state_points = 361
    num_alpha_points = 73

    print("\n========================================")
    print("FINAL POINCARE GRID")
    print("========================================")

    print(
        f"Using {num_state_points} state points x "
        f"{num_alpha_points} alpha points")

    state_grid, alpha_grid = make_grids(num_state_points,num_alpha_points,)

    state_action_table = build_state_action_table(state_grid,alpha_grid,)

    steps_to_roa, best_alpha = find_steps_to_roa(state_action_table,state_grid,alpha_grid,)



    # Trajectory

    target_theta_dot = 4.05

    initial_index = np.argmin(np.abs(state_grid - target_theta_dot))

    initial_theta_dot = state_grid[initial_index]

    print(
        f"\nSelected initial condition: "
        f"theta_dot = {initial_theta_dot:.6f} rad/s"
    )

    print(
        f"Steps to RoA = "
        f"{steps_to_roa[initial_index]}")

    time_values, theta_values, theta_dot_values, section_states = (
        simulate_controlled_trajectory(
            initial_theta_dot,
            initial_index,
            state_grid,
            alpha_grid,
            best_alpha,
            steps_to_roa,))

    #PLOT trajectory
    plt.figure(figsize=(8, 5))

    plt.plot(
        theta_values,
        theta_dot_values,
        linewidth=1.5,
        label="Walker trajectory",
    )

    plt.scatter(
        section_states[:, 1],
        section_states[:, 2],
        zorder=3,
        label="Poincaré crossings",
    )

    plt.xlabel(r"$\theta$ [rad]")
    plt.ylabel(r"$\dot{\theta}$ [rad/s]")

    plt.title(
        "Controlled Walker Trajectory to the RoA"
    )

    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        "trajectory_to_roa.png",
        dpi=300,
    )

    plt.show()


    # Plot number of steps to reach the RoA
    reachable = steps_to_roa >= 0

    plt.figure(figsize=(8, 5))

    plt.scatter(
        state_grid[reachable],
        steps_to_roa[reachable],
    )

    plt.xlabel(r"Initial $\dot{\theta}$ [rad/s]")
    plt.ylabel("Steps to reach RoA")
    plt.title("Steps Required to Reach the Region of Attraction")
    plt.grid(True)

    plt.savefig(
        "steps_to_roa.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()