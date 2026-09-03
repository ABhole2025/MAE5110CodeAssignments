import matplotlib.pyplot as plt
import numpy as np

from integrators import rk4


def rimless_wheel_continuous(t, state, params):
    """
    Continuous dynamics of the rimless wheel when pivoting on stance spoke.
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


def generate_params():
    return {
        "gravity": 9.81,
        "spoke_length": 1.0,
        "slope_angle": 2,   # radians
        "num_spokes": 8       # number of spokes
    }


def detect_impact(wheel_state, params):
    """
    Return True if the next spoke hits the ground.
    Impact occurs when the stance spoke angle reaches +alpha.
    """
    angle, angular_velocity = wheel_state
    num_spokes = params["num_spokes"]
    alpha = np.pi / num_spokes
    gamma = params["slope_angle"]

    return angle >= alpha



def spoke_reset(wheel_state, params):
    """
    When a new spoke contacts the ground:
    - angle jumps backward by 2*alpha
    - angular velocity is multiplied by cos(2*alpha)
    """
    angle, angular_velocity = wheel_state

    num_spokes = params["num_spokes"]
    alpha = np.pi / num_spokes

    new_angle = angle - 2 * alpha

    new_angular_velocity = angular_velocity * np.cos(2 * alpha)

    return np.array([new_angle, new_angular_velocity])


def simulate_rimless_wheel(initial_state, params, time_step, total_time):

    pivot_x_current = 0.0
    pivot_y_current = 0.0

    pivot_x = []
    pivot_y = []

    num_steps = int(total_time / time_step)

    times = np.zeros(num_steps)
    angles = np.zeros(num_steps)
    angular_velocities = np.zeros(num_steps)

    wheel_state = initial_state.copy()
    current_time = 0.0

    for step in range(num_steps):

        # Record state
        times[step] = current_time
        angles[step] = wheel_state[0]
        angular_velocities[step] = wheel_state[1]


        if detect_impact(wheel_state, params):
            wheel_state = spoke_reset(wheel_state, params)
            l = params["spoke_length"]
            num_spokes = params["num_spokes"]
            alpha = np.pi / num_spokes
            gamma = params["slope_angle"]

            step = 2 * l * np.sin(alpha)

            pivot_x_current += step * np.sin(gamma)
            pivot_y_current -= step * np.cos(gamma)



        wheel_state = rk4(current_time, wheel_state, time_step,
                        rimless_wheel_continuous, params)

        num_spokes = params["num_spokes"]
        alpha = np.pi / num_spokes

        theta = wheel_state[0]

        while theta > alpha:
            theta -= 2*alpha
        while theta < -alpha:
            theta += 2*alpha

        wheel_state[0] = theta

        pivot_x.append(pivot_x_current)
        pivot_y.append(pivot_y_current)


        current_time += time_step

    return times, angles, angular_velocities, pivot_x, pivot_y

#Sanity checks
params = generate_params()
params["slope_angle"] = 0.0   # flat ground

initial_state = np.array([0.0, 1.5])

times, angles, angular_velocities, px, py = simulate_rimless_wheel(
    initial_state, params, time_step=0.001, total_time=10.0
)

plt.plot(times, angles)
plt.title("Sanity Check 1: Flat Ground Sawtooth")
plt.xlabel("Time")
plt.ylabel("Angle (theta)")
plt.savefig("Flat Ground Sawtooth")
plt.close()


params = generate_params()
params["slope_angle"] = 0.2   # downhill

initial_state = np.array([0.2, 1.5])

times, angles, angular_velocities, px, py = simulate_rimless_wheel(
    initial_state, params, time_step=0.001, total_time=10.0
)


plt.plot(times, angles)
plt.title("Sanity Check 2: Downhill Accelerating Sawtooth")
plt.xlabel("Time")
plt.ylabel("Angle (theta)")
plt.grid()
plt.savefig("Downhill Accelerating Sawtooth")
plt.close()


def compute_mass_trajectory(angles, pivot_x, pivot_y, params):
    l = params["spoke_length"]
    x = pivot_x + l * np.sin(angles)
    y = pivot_y + l * np.cos(angles)
    return x, y


times, angles, angular_velocities, px, py = simulate_rimless_wheel(
    initial_state, params, time_step=0.001, total_time=10.0
)

x, y = compute_mass_trajectory(angles, px, py, params)

plt.figure()
plt.plot(x, y)
plt.gca().set_aspect('equal', 'box')
plt.title("Mass Trajectory – Flat Ground")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()
plt.savefig("Flat_Trajectory")
plt.close()

times, angles, angular_velocities, px, py = simulate_rimless_wheel(
    initial_state, params, time_step=0.001, total_time=5.0
)

x, y = compute_mass_trajectory(angles, px, py, params)

plt.figure()
plt.plot(x, y)
plt.gca().set_aspect('equal', 'box')
plt.title("Mass Trajectory – Downhill")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()
plt.savefig("Downhill_Trajectory")
plt.close()

