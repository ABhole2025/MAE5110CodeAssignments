import numpy as np
import matplotlib.pyplot as plt
from integrators import rk4

def rimless_wheel_continuous(t, state, params):
    """
    Continuous dynamics of the rimless wheel when pivoting on stance spoke.
    state = [theta, theta_dot]
    """
    #theta is angle from upright vertical. theta_dot is angular velocity
    theta, theta_dot = state #theta

    g = params["gravity"]
    l = params["spoke_length"]
    gamma = params["slope_angle"]

    # Inverted pendulum dynamics on a slope
    #theta_ddot is angular acceleration
    theta_ddot = (g / l) * np.sin(theta - gamma)

    return np.array([theta_dot, theta_ddot])

def rimless_wheel_energy(state, params):
    """
    Compute kinetic + potential energy for the rimless wheel continuous phase.
    """
    g = params["gravity"]
    l = params["spoke_length"]
    m = 1.0  # mass cancels in dynamics, but needed for energy

    theta, theta_dot = state

    KE = 0.5 * m * (l * theta_dot)**2
    PE = m * g * l * np.cos(theta)

    return KE, PE


def generate_params():
    return {
        "gravity": 9.81,
        "spoke_length": 1.0,
        "slope_angle": 0.1,   # radians
        "num_spokes": 8          # number of spokes
    }

#SANITY CHECKS
# Simulation settings
time_step = 0.001
simulation_duration = 5.0
num_steps = int(simulation_duration / time_step)

#initial conditions and state
initial_angle = 0.2
initial_angular_velocity = 0.0
initial_state = np.array([initial_angle, initial_angular_velocity])

# 1. Continuous dynamics on flat ground - inverted pendulum
flat_ground_params = generate_params()
flat_ground_params["slope_angle"] = 0.0   # for this test we need flat slope

wheel_state = initial_state.copy()
trajectory_flat_ground = np.zeros((num_steps, 2))
current_time = 0.0

for step in range(num_steps):
    trajectory_flat_ground[step] = wheel_state
    wheel_state = rk4(current_time, wheel_state, time_step,
                    rimless_wheel_continuous, flat_ground_params)

    current_time += time_step


# 2. Energy consistency test (flat ground)

energy_params = generate_params()
energy_params["slope_angle"] = 0.0

energy_initial_state = np.array([0.1, 0.5])
wheel_state = energy_initial_state.copy()

total_energy_over_time = np.zeros(num_steps)
current_time = 0.0

for step in range(num_steps):
    KE, PE = rimless_wheel_energy(wheel_state, energy_params)
    total_energy_over_time[step] = KE + PE
    wheel_state = rk4(current_time, wheel_state, time_step,
                        rimless_wheel_continuous, energy_params)
    current_time += time_step

def detect_impact(wheel_state, params):
    """
    Return True if the next spoke hits the ground.
    Impact occurs when the stance spoke angle reaches +alpha.
    """
    angle, angular_velocity = wheel_state

    num_spokes = params["num_spokes"]
    alpha = np.pi / num_spokes   # half the spoke angle

    return angle >= alpha



# 3. Continuous dynamics on a downhill slope
sloped_ground_params = generate_params()

wheel_state = initial_state.copy()
trajectory_sloped_ground = np.zeros((num_steps, 2))
current_time = 0.0

for step in range(num_steps):
    trajectory_sloped_ground[step] = wheel_state
    wheel_state = rk4(current_time, wheel_state, time_step,
                    rimless_wheel_continuous, sloped_ground_params)
    current_time += time_step

#sanity check plots
plt.figure(figsize=(10, 6))
plt.plot(trajectory_flat_ground[:, 0], label="Flat ground")
plt.plot(trajectory_sloped_ground[:, 0], label="Slope = 0.2 rad")
plt.title("Rimless Wheel: Continuous Dynamics Sanity Check")
plt.xlabel("Time step")
plt.ylabel("Angle (theta)")
plt.legend()
plt.grid()
plt.savefig("sanity_continuous_dynamics.png", dpi=300)
plt.close()

plt.figure(figsize=(10, 6))
plt.plot(total_energy_over_time)
plt.title("Rimless Wheel: Energy Consistency (Flat Ground)")
plt.xlabel("Time step")
plt.ylabel("Total Energy")
plt.grid()
plt.savefig("sanity_energy_consistency.png", dpi=300)
plt.close()

print("Saved sanity check PNGs:")
print(" - sanity_continuous_dynamics.png")
print(" - sanity_energy_consistency.png")
