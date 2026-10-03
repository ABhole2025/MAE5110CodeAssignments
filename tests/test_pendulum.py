import numpy as np

from models import pendulum


def test_energy_conservation():
    params = pendulum.generate_params()
    params["damping_coeff"] = 0.0
    params["torque"] = 0.0

    state = np.array([0.5, 0.0])
    dt = 1e-4

    initial_kinetic, initial_potential = pendulum.calculate_energy(state, params)
    initial_energy = initial_kinetic + initial_potential

    for _ in range(100):
        state = state + dt * pendulum.dynamics(0.0, state, params)

    final_kinetic, final_potential = pendulum.calculate_energy(state, params)
    final_energy = final_kinetic + final_potential

    assert np.isclose(final_energy, initial_energy, rtol=1e-3)


def test_torque():
    params = pendulum.generate_params()
    params["damping_coeff"] = 0.0
    params["torque"] = 1.0

    state = np.array([0.0, 0.0])

    state_derivative = pendulum.dynamics(0.0, state, params)

    expected_acceleration = (
        params["torque"] / (params["mass"] * params["length"] ** 2)
    )

    assert np.isclose(state_derivative[1], expected_acceleration)


def test_damping():
    params = pendulum.generate_params()
    params["gravity"] = 0.0
    params["torque"] = 0.0
    params["damping_coeff"] = 0.1

    state = np.array([0.0, 1.0])

    state_derivative = pendulum.dynamics(0.0, state, params)

    expected_acceleration = (
        -params["damping_coeff"] * state[1]
        / (params["mass"] * params["length"] ** 2)
    )

    assert np.isclose(state_derivative[1], expected_acceleration)