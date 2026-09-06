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

# ---------------------------------------------------------
# Floquet multiplier sweep: slope angle
# ---------------------------------------------------------

g = params["gravity"]
l = params["spoke_length"]
N = params["num_spokes"]

alpha = np.pi / N

slope_angles_deg = np.arange(5, 36, 5)

floquet_values = []

epsilon = 0.01
time_step = 0.001

for slope_deg in slope_angles_deg:

    print(f"Sweeping slope = {slope_deg} degrees")

    # Update slope
    params["slope_angle"] = np.deg2rad(slope_deg)

    # Theoretical pre-impact fixed point
    v_minus_star = np.sqrt(
        2 * g / (l * (1 + np.cos(2 * alpha)))
    )

    # Convert to post-impact fixed point
    v_plus_star = (
        v_minus_star
        * np.cos(2 * alpha)
    )

    # Perturb post-impact velocity
    v_plus_low = v_plus_star - epsilon
    v_plus_high = v_plus_star + epsilon

    # Simulate one step from each perturbation
    v_next_low = get_next_post_impact_velocity(
        v_plus_low,
        params,
        time_step
    )

    v_next_high = get_next_post_impact_velocity(
        v_plus_high,
        params,
        time_step
    )

    # Finite-difference estimate of return-map slope
    floquet = (
        v_next_high - v_next_low
    ) / (2 * epsilon)

    floquet_values.append(floquet)

    print(f"  Fixed point: {v_minus_star:.4f} rad/s")
    print(f"  Floquet multiplier: {floquet:.6f}")


plt.figure(figsize=(7, 5))

plt.plot(
    slope_angles_deg,
    floquet_values,
    "o-",
    label="Floquet multiplier"
)

plt.xlabel("Slope inclination (degrees)")
plt.ylabel("Floquet multiplier")
plt.title("Floquet Multiplier vs. Slope Inclination")

plt.ylim(0.45, 0.55)

plt.grid(True)
plt.legend()

plt.savefig(
    "Floquet vs Slope.png",
    dpi=300
)

plt.close()

# ---------------------------------------------------------
# Floquet multiplier sweep: number of spokes
# ---------------------------------------------------------

params["slope_angle"] = np.deg2rad(20)

spoke_numbers = np.arange(6, 13)

floquet_values_spokes = []

epsilon = 0.01
time_step = 0.001

for N in spoke_numbers:

    print(f"Sweeping N = {N} spokes")

    # Update number of spokes
    params["num_spokes"] = N

    # Geometry
    alpha = np.pi / N

    # Theoretical pre-impact fixed point
    v_minus_star = np.sqrt(
        2 * g / (
            l * (1 + np.cos(2 * alpha))
        )
    )

    # Post-impact fixed point
    v_plus_star = (
        v_minus_star
        * np.cos(2 * alpha)
    )

    # Perturb post-impact velocity
    v_plus_low = v_plus_star - epsilon
    v_plus_high = v_plus_star + epsilon

    # Simulate one step from each perturbation
    v_next_low = get_next_post_impact_velocity(
        v_plus_low,
        params,
        time_step
    )

    v_next_high = get_next_post_impact_velocity(
        v_plus_high,
        params,
        time_step
    )

    # Estimate Floquet multiplier
    floquet = (
        v_next_high - v_next_low
    ) / (2 * epsilon)

    floquet_values_spokes.append(floquet)

    print(f"  Fixed point: {v_minus_star:.4f} rad/s")
    print(f"  Floquet multiplier: {floquet:.6f}")


# ---------------------------------------------------------
# Plot results
# ---------------------------------------------------------

plt.figure(figsize=(7, 5))

plt.plot(
    spoke_numbers,
    floquet_values_spokes,
    "o-",
    label="Numerical Floquet multiplier"
)

plt.xlabel("Number of spokes")
plt.ylabel("Floquet multiplier")
plt.title("Floquet Multiplier vs. Number of Spokes")

plt.grid(True)
plt.legend()

plt.savefig(
    "Floquet vs Number of Spokes.png",
    dpi=300
)

plt.close()