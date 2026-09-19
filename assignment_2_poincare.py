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

    differences = []

    for theta_dot, coarse_alpha in zip(coarse_grid,coarse_policy,):

        if not np.isfinite(coarse_alpha):
            continue

        # Find the closest state in the finer grid
        fine_index = np.argmin(np.abs(fine_grid - theta_dot))

        fine_alpha = fine_policy[fine_index]

        if not np.isfinite(fine_alpha):
            continue

        differences.append(abs(coarse_alpha - fine_alpha))

    if len(differences) == 0:
        return {
            "max_difference": np.nan,
            "mean_difference": np.nan,
            "fraction_large_change": np.nan,
            "num_compared": 0,}

    differences = np.array(differences)

    coarse_alpha_grid = coarse_result["alpha_grid"]

    delta_alpha = (coarse_alpha_grid[1]- coarse_alpha_grid[0])

    fraction_large_change = np.mean(differences > delta_alpha)

    return {
        "max_difference": np.max(differences),
        "mean_difference": np.mean(differences),
        "fraction_large_change": fraction_large_change,
        "num_compared": len(differences),
    }





if __name__ == "__main__":

    # TEST 1: Alpha-grid resolution
    alpha_resolutions = [
        (201, 5),
        (201, 11),
        (201, 21),
        (201, 31),
        (201, 41),
        (201, 61),
        (201, 81),
    ]

    alpha_results = []

    print("\n========================================")
    print("TEST 1: ALPHA-GRID RESOLUTION")
    print("========================================")

    for num_state_points, num_alpha_points in alpha_resolutions:

        result = run_resolution_test(num_state_points,num_alpha_points,)

        alpha_results.append(result)

        print(
            f"\nRunning {num_state_points} state points "
            f"x {num_alpha_points} alpha points")

        print(
            f"Reachable states: "
            f"{result['reachable_states']}/"
            f"{num_state_points}")

    print("\nAlpha-grid policy convergence:")

    alpha_policy_differences = []

    for i in range(len(alpha_results) - 1):

        coarse = alpha_results[i]
        fine = alpha_results[i + 1]

        comparison = compare_policies(coarse,fine,)

        alpha_policy_differences.append(comparison["mean_difference"])

        print(
            f"{coarse['num_alpha_points']} -> "
            f"{fine['num_alpha_points']}: "
            f"mean |Delta alpha| = "
            f"{comparison['mean_difference']:.6f} rad, "
            f"fraction > 1 grid step = "
            f"{comparison['fraction_large_change']:.3f}")


    # TEST 2: State-grid resolution

    fixed_num_alpha_points = 41

    state_resolutions = [
        (21, fixed_num_alpha_points),
        (31, fixed_num_alpha_points),
        (51, fixed_num_alpha_points),
        (81, fixed_num_alpha_points),
        (101, fixed_num_alpha_points),
        (151, fixed_num_alpha_points),
        (201, fixed_num_alpha_points),
        (301, fixed_num_alpha_points),
        (401, fixed_num_alpha_points),
    ]

    state_results = []

    print("\n========================================")
    print("TEST 2: STATE-GRID RESOLUTION")
    print("========================================")

    for num_state_points, num_alpha_points in state_resolutions:

        result = run_resolution_test(num_state_points,num_alpha_points,)

        state_results.append(result)

        print(
            f"\nRunning {num_state_points} state points "
            f"x {num_alpha_points} alpha points")

        print(
            f"Reachable states: "
            f"{result['reachable_states']}/"
            f"{num_state_points}")

        print(
            f"Delta theta_dot: "
            f"{result['delta_theta_dot']:.5f} rad/s")

    print("\nState-grid policy convergence:")

    state_policy_differences = []

    for i in range(len(state_results) - 1):

        coarse = state_results[i]
        fine = state_results[i + 1]

        comparison = compare_policies(coarse,fine,)

        state_policy_differences.append(
            comparison["mean_difference"])

        print(
            f"{coarse['num_state_points']} -> "
            f"{fine['num_state_points']}: "
            f"mean |Delta alpha| = "
            f"{comparison['mean_difference']:.6f} rad, "
            f"fraction > 1 alpha-grid step = "
            f"{comparison['fraction_large_change']:.3f}")



    # Plot

    state_counts = [result["num_state_points"]for result in state_results]

    plt.figure(figsize=(8, 5))

    plt.plot(state_counts[1:],state_policy_differences,marker="o",)

    plt.xlabel("Finer state-grid resolution (number of points)")

    plt.ylabel("Mean |Delta alpha| between resolutions [rad]")

    plt.title("State-Grid Policy Convergence")

    plt.grid(True)

    plt.savefig("state_grid_policy_convergence.png",dpi=300,)

    plt.show()