import matplotlib.pyplot as plt
import numpy as np
import rimless_wheel as model

from integrators import rk4

params = model.generate_params()

params["slope_angle"] = np.deg2rad(20)
params["num_spokes"] = 8

alpha = np.pi / params["num_spokes"]
gamma = params["slope_angle"]

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



def get_next_post_impact_velocity(post_impact_velocity, params, time_step):
    """
    Start immediately after impact and simulate one step.
    Return the post-impact velocity at the next impact.
    """

    gamma = params["slope_angle"]

    # Immediately after impact, the new stance spoke is aligned
    # with the ground normal.
    wheel_state = np.array([
        -gamma,
        post_impact_velocity
    ])

    current_time = 0.0

    while True:

        # Check whether we have reached the next impact
        if model.detect_impact(wheel_state, params):

            # Apply impact reset
            wheel_state = model.spoke_reset(wheel_state, params)

            # Return the new post-impact velocity
            return wheel_state[1]

        # Integrate one timestep
        wheel_state = rk4(
            current_time,
            wheel_state,
            time_step,
            model.rimless_wheel_continuous,
            params
        )

        current_time += time_step


'''text break'''


initial_state = np.array([
    np.deg2rad(25), 0])

impact_velocities = get_impact_velocities(
    initial_state,
    params,
    time_step=0.001,
    total_time=100.0
)

print("Number of impacts:", len(impact_velocities))
print("Impact velocities:")
print(impact_velocities)

v_current = impact_velocities[:-1]
v_next = impact_velocities[1:]

# Find the fixed point: where v_next is closest to v_current
fixed_point_index = np.argmin(np.abs(v_next - v_current))

v_minus_star = v_current[fixed_point_index]

print("Pre-impact fixed point:", v_minus_star, "rad/s")

# Convert the pre-impact fixed point to the post-impact fixed point
v_plus_star = v_minus_star * np.cos(2 * alpha)

print("Post-impact fixed point:", v_plus_star, "rad/s")

# Small perturbation
epsilon = 0.01

v_plus_low = v_plus_star - epsilon
v_plus_high = v_plus_star + epsilon

# Simulate one step from each perturbed state
v_next_low = get_next_post_impact_velocity(
    v_plus_low,
    params,
    time_step=0.001
)

v_next_high = get_next_post_impact_velocity(
    v_plus_high,
    params,
    time_step=0.001
)

print("Perturbed post-impact velocities:")
print("Low:", v_plus_low, "->", v_next_low)
print("High:", v_plus_high, "->", v_next_high)


floquet_multiplier = (
    v_next_high - v_next_low
) / (2 * epsilon)

print("Estimated Floquet multiplier:", floquet_multiplier)


'''text break'''


plt.figure(figsize=(7, 7))

plt.plot(
    v_current,
    v_next,
    "o",
    markersize=4,
    label="Return map"
)

# Identity line
v = np.linspace(
    min(v_current.min(), v_next.min()),
    max(v_current.max(), v_next.max()),
    100
)

plt.plot(
    v,
    v,
    "--",
    label=r"$y=x$"
)

plt.plot(
    v_minus_star,
    v_minus_star,
    "ro",
    markersize=8,
    label=f"Fixed point = {v_minus_star:.3f} rad/s"
)

plt.xlabel(r"Current impact velocity $\dot{\theta}_k^-$ (rad/s)")
plt.ylabel(r"Next impact velocity $\dot{\theta}_{k+1}^-$ (rad/s)")
plt.title("Rimless Wheel Return Map")

plt.legend()
plt.grid(True)

plt.savefig("Rimless Wheel Return Map.png", dpi=300)
plt.close()





