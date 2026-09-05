import matplotlib.pyplot as plt
import numpy as np
import rimless_wheel as model

from integrators import rk4


params = model.generate_params()

params["slope_angle"] = np.deg2rad(20)

params["num_spokes"] = 8

# State-space grid
alpha = np.pi / params["num_spokes"]
gamma = params["slope_angle"]

theta_values = np.linspace(
    -gamma,
    2 * alpha - gamma,
    100
)

theta_dot_values = np.linspace(-5.0, 5.0, 100)

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


'''
initial_state = np.array([
    -params["slope_angle"],
    0.0
])

impact_velocities = get_impact_velocities(
    initial_state,
    params,
    time_step=0.005,
    total_time=20.0
)

print(impact_velocities)
'''


def classify_state(initial_state, params, time_step, total_time):

    gamma = params["slope_angle"]

    theta0, theta_dot0 = initial_state

    # Check for the equilibrium
    if (
        abs(theta0 + gamma) < 1e-3
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


'''
# Test equilibrium
equilibrium_state = np.array([
    -params["slope_angle"],
    0.0
])

print(
    "Equilibrium:",
    classify_state(
        equilibrium_state,
        params,
        0.005,
        20.0
    )
)


# Test a walking initial condition
walking_state = np.array([
    np.deg2rad(20),
    0.0
])

print(
    "Walking:",
    classify_state(
        walking_state,
        params,
        0.005,
        20.0
    )
)
'''

for i, theta in enumerate(theta_values):
    for j, theta_dot in enumerate(theta_dot_values):

        initial_state = np.array([
            theta,
            theta_dot
        ])

        results[i, j] = classify_state(
            initial_state,
            params,
            time_step=0.005,
            total_time=20.0
        )

print("Number of equilibrium points:", np.sum(results == 0))
print("Number of limit-cycle points:", np.sum(results == 1))
print("Number of unclassified points:", np.sum(results == -1))