import numpy as np
import matplotlib.pyplot as plt

from models import inverted_pendulum_walker as model


params = model.generate_params()

timestep = 1e-3
sim_time = 5.0

section_theta = 0.0


def poincare_section_crossed(previous_state, next_state):
    previous_theta = previous_state[0]
    next_theta = next_state[0]

    return (previous_theta < section_theta and next_theta >= section_theta)


def simulate_poincare(initial_state, alpha):
    local_params = params.copy()
    local_params["angle_of_attack"] = alpha

    n_timesteps = round(sim_time / timestep)

    state = np.asarray(initial_state, dtype=float).copy()

    poincare_velocities = []

    for index in range(n_timesteps):
        next_state = state + timestep * model.dynamics(index * timestep, state, local_params,)

        # Check for Poincaré-section crossing
        if poincare_section_crossed(state, next_state):
            print(f"Crossing at t = {index * timestep:.3f}, "f"theta_dot = {next_state[1]:.4f}")
            poincare_velocities.append(next_state[1])

        # Check for impact
        if model.event_guard(state, next_state, local_params):
            print(f"Impact at t = {index * timestep:.3f}, "f"theta = {next_state[0]:.4f}")

            next_state = model.event_dynamics(next_state, local_params,)

        state = next_state

    return np.array(poincare_velocities)



if __name__ == "__main__":

    alpha = params["angle_of_attack"]

    initial_state = [0.0, 1.0]

    poincare_velocities = simulate_poincare(initial_state, alpha,)

    print("Poincaré section:")
    print(poincare_velocities)