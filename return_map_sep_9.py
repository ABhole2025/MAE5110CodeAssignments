import matplotlib.pyplot as plt
import numpy as np

import rimless_wheel_1 as model


# ============================================================
# Parameters
# ============================================================

params = model.generate_params()

params["slope_angle"] = np.deg2rad(20)
params["num_spokes"] = 8

TIME_STEP = 0.001
EPSILON = 0.01


# ============================================================
# Fixed-point calculation
# ============================================================

def theoretical_fixed_point(params):
    """
    Calculate the theoretical post-impact fixed-point velocity.
    """

    g = params["gravity"]
    l = params["spoke_length"]
    gamma = params["slope_angle"]

    alpha = np.pi / params["num_spokes"]

    energy_change = (
        2 * g / l
        * (
            np.cos(gamma - alpha)
            - np.cos(gamma + alpha)
        )
    )

    impact_factor = np.cos(2 * alpha)

    v_plus = (
        impact_factor
        * np.sqrt(
            energy_change
            / (1 - impact_factor**2)
        )
    )

    v_minus = np.sqrt(
        v_plus**2 + energy_change
    )

    return v_plus, v_minus


# ============================================================
# Return map
# ============================================================

def get_next_post_impact_velocity(
    post_impact_velocity,
    params,
    time_step=TIME_STEP
):
    """
    Simulate one stance phase and return the velocity
    immediately after the next impact.
    """

    gamma = params["slope_angle"]
    alpha = np.pi / params["num_spokes"]

    # State immediately after impact
    initial_state = np.array([
        gamma - alpha,
        post_impact_velocity
    ])

    (
        times,
        angles,
        angular_velocities,
        impact_velocities
    ) = model.simulate_rimless_wheel(
        initial_state,
        params,
        time_step=time_step,
        total_time=2.0
    )

    if len(impact_velocities) == 0:
        raise RuntimeError(
            "No impact detected during return-map simulation."
        )

    # Convert pre-impact velocity to post-impact velocity
    v_minus = impact_velocities[0]

    return v_minus * np.cos(2 * alpha)


# ============================================================
# Floquet multiplier
# ============================================================

def calculate_floquet_multiplier(
    v_plus_star,
    params,
    epsilon=EPSILON,
    time_step=TIME_STEP
):
    """
    Estimate the Floquet multiplier using a centered
    finite difference of the return map.
    """

    v_low = v_plus_star - epsilon
    v_high = v_plus_star + epsilon

    next_low = get_next_post_impact_velocity(
        v_low,
        params,
        time_step
    )

    next_high = get_next_post_impact_velocity(
        v_high,
        params,
        time_step
    )

    return (
        next_high - next_low
    ) / (2 * epsilon)


# ============================================================
# Return map at 20 degree slope
# ============================================================

v_plus_star, v_minus_star = theoretical_fixed_point(params)

print("Starting return-map test...")
print("Theoretical pre-impact fixed point =", v_minus_star)
print("Theoretical post-impact fixed point =", v_plus_star)

v_next = get_next_post_impact_velocity(
    v_plus_star,
    params
)

print("Next post-impact velocity =", v_next)


v_plus_values = np.linspace(
    v_plus_star - 1.0,
    v_plus_star + 1.0,
    100
)

v_next_values = np.array([
    get_next_post_impact_velocity(
        v_plus,
        params
    )
    for v_plus in v_plus_values
])


# ============================================================
# Plot return map
# ============================================================

plt.figure(figsize=(7, 5))

plt.plot(
    v_plus_values,
    v_next_values,
    "o-",
    markersize=3,
    label="Return map"
)

plt.plot(
    v_plus_values,
    v_plus_values,
    "--",
    label="Identity line"
)

plt.plot(
    v_plus_star,
    v_plus_star,
    "o",
    markersize=8,
    label="Fixed point"
)

plt.xlabel(r"$v_k^+$ (rad/s)")
plt.ylabel(r"$v_{k+1}^+$ (rad/s)")
plt.title("Rimless Wheel Return Map")

plt.grid(True)
plt.legend()

plt.savefig(
    "assgn_1 Rimless Wheel Return Map.png",
    dpi=300
)

plt.close()


# ============================================================
# Floquet multiplier at 20 degree slope
# ============================================================

floquet = calculate_floquet_multiplier(
    v_plus_star,
    params,
    epsilon=0.01,
    time_step=0.0001
)

print("\nSingle Floquet multiplier calculation")
print("Slope angle:              20 degrees")
print("Number of spokes:         8")
print("Pre-impact fixed point:   ", v_minus_star)
print("Post-impact fixed point:  ", v_plus_star)
print("Perturbation epsilon:     ", EPSILON)
print("Floquet multiplier:       ", floquet)


# ============================================================
# Floquet multiplier sweep: slope angle
# ============================================================

params["num_spokes"] = 8

slope_angles_deg = np.arange(5, 36, 5)

floquet_values = []

for slope_deg in slope_angles_deg:

    print(f"Sweeping slope = {slope_deg} degrees")

    params["slope_angle"] = np.deg2rad(slope_deg)

    v_plus_star, v_minus_star = theoretical_fixed_point(
        params
    )

    floquet = calculate_floquet_multiplier(
        v_plus_star,
        params,
        epsilon=EPSILON,
        time_step=0.0001
    )

    floquet_values.append(floquet)

    print(f"  Pre-impact fixed point:  {v_minus_star:.4f} rad/s")
    print(f"  Post-impact fixed point: {v_plus_star:.4f} rad/s")
    print(f"  Floquet multiplier:      {floquet:.6f}")


# ============================================================
# Plot Floquet multiplier vs. slope
# ============================================================

plt.figure(figsize=(7, 5))

plt.plot(
    slope_angles_deg,
    floquet_values,
    "o-",
    label="Numerical Floquet multiplier"
)

plt.xlabel("Slope inclination (degrees)")
plt.ylabel("Floquet multiplier")
plt.title("Floquet Multiplier vs. Slope Inclination")

plt.grid(True)
plt.legend()

plt.savefig(
    "assgn_1 Floquet vs Slope.png",
    dpi=300
)

plt.close()


# ============================================================
# Floquet multiplier sweep: number of spokes
# ============================================================

params["slope_angle"] = np.deg2rad(20)

spoke_numbers = np.arange(6, 13)

floquet_values_spokes = []

for num_spokes in spoke_numbers:

    print(f"Sweeping N = {num_spokes} spokes")

    params["num_spokes"] = num_spokes

    v_plus_star, v_minus_star = theoretical_fixed_point(
        params
    )

    floquet = calculate_floquet_multiplier(
        v_plus_star,
        params,
        epsilon=EPSILON,
        time_step=0.0001
    )

    floquet_values_spokes.append(floquet)

    print(f"  Pre-impact fixed point:  {v_minus_star:.4f} rad/s")
    print(f"  Post-impact fixed point: {v_plus_star:.4f} rad/s")
    print(f"  Floquet multiplier:      {floquet:.6f}")


# ============================================================
# Plot Floquet multiplier vs. number of spokes
# ============================================================

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
    "assgn_1 Floquet vs Number of Spokes.png",
    dpi=300
)

plt.close()