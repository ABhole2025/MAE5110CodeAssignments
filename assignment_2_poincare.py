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

    with ProcessPoolExecutor() as executor:
        results = executor.map(simulate_state_action,[task[0] for task in tasks],[task[1] for task in tasks],)

        for theta_dot_initial, alpha, theta_dot_next in results:
            state_index = np.argmin(np.abs(state_grid - theta_dot_initial))

            alpha_index = np.argmin(np.abs(alpha_grid - alpha))

            if theta_dot_next is not None:
                table[state_index, alpha_index] = theta_dot_next

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


def run_resolution_test(num_state_points, num_alpha_points):

    print(f"\nRunning {num_state_points} state points "f"x {num_alpha_points} alpha points")

    state_grid, alpha_grid = make_grids(num_state_points,num_alpha_points,)

    state_action_table = build_state_action_table(state_grid,alpha_grid,)

    steps_to_roa, best_alpha = find_steps_to_roa(
        state_action_table,
        state_grid,
        alpha_grid,)

    reachable = steps_to_roa >= 0

    delta_theta_dot = (state_grid[1] - state_grid[0])

    # Physical range of states that are reachable
    if np.any(reachable):

        reachable_theta_dot_min = (state_grid[reachable].min())

        reachable_theta_dot_max = (state_grid[reachable].max())

    else:

        reachable_theta_dot_min = np.nan
        reachable_theta_dot_max = np.nan

    return {
        "num_state_points": num_state_points,
        "num_alpha_points": num_alpha_points,

        "total_pairs": (state_action_table.size),

        "returning_pairs": np.sum(np.isfinite(state_action_table)),

        "return_fraction": np.mean(np.isfinite(state_action_table)),

        "reachable_states": np.sum(reachable),

        "max_steps": (np.max(steps_to_roa[reachable])if np.any(reachable)else -1),

        "steps_to_roa": steps_to_roa,
        "best_alpha": best_alpha,
        "state_grid": state_grid,
        "alpha_grid": alpha_grid,

        "delta_theta_dot": delta_theta_dot,

        "reachable_theta_dot_min":
            reachable_theta_dot_min,

        "reachable_theta_dot_max":
            reachable_theta_dot_max,
    }


def compare_policies(coarse_result, fine_result):

    coarse_grid = coarse_result["state_grid"]
    coarse_policy = coarse_result["best_alpha"]

    fine_grid = fine_result["state_grid"]
    fine_policy = fine_result["best_alpha"]

    # Only compare states for which both
    # policies have a defined action.
    differences = []

    for i, theta_dot in enumerate(
        coarse_grid):

        coarse_alpha = coarse_policy[i]

        if not np.isfinite(coarse_alpha):
            continue

        # Find the closest state in the finer grid
        fine_index = np.argmin(
            np.abs(fine_grid- theta_dot))

        fine_alpha = fine_policy[fine_index]

        if not np.isfinite(fine_alpha):
            continue

        differences.append(abs(coarse_alpha- fine_alpha))

    if len(differences) == 0:
        return np.nan

    return np.max(differences)


if __name__ == "__main__":

    resolutions = [
        (21, 21),
        (31, 21),
        (51, 21),
        (81, 21),
        (101, 21),
        (151, 21),
        (201, 21),
        (301, 21),
        (401, 21),
    ]

    results = []

    for num_state_points, num_alpha_points in resolutions:

        result = run_resolution_test(
            num_state_points,
            num_alpha_points,
        )

        results.append(result)

        print(
            f"Reachable states: "
            f"{result['reachable_states']}/"
            f"{num_state_points}"
        )

        print(
            f"Delta theta_dot: "
            f"{result['delta_theta_dot']:.5f} "
            f"rad/s"
        )

        print(
            f"Reachable theta_dot range: "
            f"{result['reachable_theta_dot_min']:.5f} "
            f"to "
            f"{result['reachable_theta_dot_max']:.5f} "
            f"rad/s"
        )

    # ---------------------------------------------------------
    # Compare each resolution with the next finer resolution
    # ---------------------------------------------------------

    policy_differences = []

    print("\nPolicy convergence:")

    for i in range(len(results) - 1):

        coarse = results[i]
        fine = results[i + 1]

        max_difference = compare_policies(
            coarse,
            fine,
        )

        policy_differences.append(
            max_difference
        )

        print(
            f"{coarse['num_state_points']} -> "
            f"{fine['num_state_points']}: "
            f"max |Delta alpha| = "
            f"{max_difference:.6f} rad"
        )

    # ---------------------------------------------------------
    # Plot policy convergence
    # ---------------------------------------------------------

    state_resolution = [
        results[i]["num_state_points"]
        for i in range(len(results) - 1)
    ]

    plt.figure(figsize=(8, 5))

    plt.plot(
        state_resolution,
        policy_differences,
        marker="o",
    )

    plt.xlabel(
        "Number of state grid points"
    )

    plt.ylabel(
        "Maximum |Δα| between resolutions [rad]"
    )

    plt.title(
        "State-Grid Policy Convergence"
    )

    plt.grid(True)

    plt.savefig(
        "state_grid_policy_convergence.png",
        dpi=300,
    )

    plt.show()

    # ---------------------------------------------------------
    # Plot reachable boundaries
    # ---------------------------------------------------------

    reachable_min = [
        result[
            "reachable_theta_dot_min"
        ]
        for result in results
    ]

    reachable_max = [
        result[
            "reachable_theta_dot_max"
        ]
        for result in results
    ]

    plt.figure(figsize=(8, 5))

    plt.plot(
        state_counts := [
            result["num_state_points"]
            for result in results
        ],
        reachable_min,
        marker="o",
        label="Minimum reachable θ̇",
    )

    plt.plot(
        state_counts,
        reachable_max,
        marker="o",
        label="Maximum reachable θ̇",
    )

    plt.xlabel(
        "Number of state grid points"
    )

    plt.ylabel(
        "θ̇ [rad/s]"
    )

    plt.title(
        "Reachable State Boundary vs. Resolution"
    )

    plt.legend()
    plt.grid(True)

    plt.savefig(
        "state_grid_reachable_boundary.png",
        dpi=300,
    )

    plt.show()