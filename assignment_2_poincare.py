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

# Initial resolution -- to be tested
num_state_points = 51
num_alpha_points = 21

state_grid = np.linspace(0.0,theta_dot_max,num_state_points,)

alpha_grid = np.linspace(np.pi / 8,np.pi / 7,num_alpha_points,)

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

        # Check for the NEXT Poincaré-section crossing
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


def build_state_action_table():
    table = np.full((num_state_points, num_alpha_points),np.nan,)

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



if __name__ == "__main__":

    state_action_table = build_state_action_table()

    np.savez("poincare_state_action.npz",state_action_table=state_action_table,state_grid=state_grid,alpha_grid=alpha_grid,)

    plt.figure(figsize=(8, 6))

    plt.imshow(
        state_action_table,
        origin="lower",
        aspect="auto",
        extent=[
            alpha_grid[0],
            alpha_grid[-1],
            state_grid[0],
            state_grid[-1],],)

    plt.colorbar(label=r"$\dot{\theta}_{k+1}$ (rad/s)")

    plt.xlabel(r"$\alpha$ (rad)")
    plt.ylabel(r"$\dot{\theta}_k$ (rad/s)")
    plt.title("Poincaré State-Action Map")

    plt.savefig("Poincaré State-Action Map")
    plt.show()


