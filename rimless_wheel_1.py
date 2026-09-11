import matplotlib.pyplot as plt
import numpy as np

from integrators import rk4

"""
IMPORTANT note for this model

theta is measured from the global upward vertical.

Positive theta is clockwise; negative theta is counterclockwise.

The downhill slope direction is clockwise.
"""


def generate_params():

    return {
        "gravity": 9.81,
        "spoke_length": 1.0,
        "slope_angle": np.deg2rad(20),
        "num_spokes": 8}


def rimless_wheel_continuous(t, state, params):

    """
    Continuous dynamics of the rimless wheel while pivoting
    on the stance spoke.

    theta is measured from the global upward vertical,
    with positive theta clockwise.
    """

    theta, theta_dot = state

    g = params["gravity"]
    l = params["spoke_length"]

    theta_ddot = (g / l) * np.sin(theta)

    return np.array([theta_dot, theta_ddot])


def detect_impact(wheel_state, params):

    """
    Detect when the next spoke reaches the ground.
    """

    theta, theta_dot = wheel_state

    num_spokes = params["num_spokes"]
    alpha = np.pi / num_spokes
    gamma = params["slope_angle"]

    impact_angle = gamma + alpha

    return theta >= impact_angle and theta_dot > 0


def spoke_reset(wheel_state, params):

    """
    Reset dynamics at impact.
    """

    theta, theta_dot = wheel_state

    num_spokes = params["num_spokes"]
    alpha = np.pi / num_spokes

    new_theta = theta - 2 * alpha
    new_theta_dot = theta_dot * np.cos(2 * alpha)

    return np.array([new_theta, new_theta_dot])


def simulate_rimless_wheel(initial_state,params,time_step,total_time):
    """
    Simulate the rimless wheel using an adaptive timestep.

    time_step is the maximum timestep used during normal
    continuous dynamics.

    When an RK4 step would cross the impact angle, the timestep
    is reduced until the impact is located accurately.

    theta is kept unwrapped internally so that impact detection
    is not affected by angle wrapping.
    """

    # Maximum timestep during normal motion
    max_dt = time_step

    # Smallest timestep allowed near impact
    min_dt = 1e-5

    # Accuracy required for locating impact
    impact_tolerance = 1e-7

    # Impact angle
    alpha = np.pi / params["num_spokes"]
    gamma = params["slope_angle"]
    impact_angle = gamma + alpha

    wheel_state = initial_state.copy()
    current_time = 0.0

    times = []
    angles = []
    angular_velocities = []
    impact_velocities = []

    while current_time < total_time:

        times.append(current_time)
        angles.append(wheel_state[0])
        angular_velocities.append(wheel_state[1])


        if detect_impact(wheel_state, params):


            wheel_state[0] = impact_angle

            impact_velocities.append(wheel_state[1])

            wheel_state = spoke_reset(
            wheel_state,
            params)

            continue

        # ----------------------------------------------------
        # Take a normal large RK4 step
        # ----------------------------------------------------

        dt = min(max_dt, total_time - current_time)

        next_state = rk4(current_time,wheel_state,dt,rimless_wheel_continuous,params)

        crossed_impact = (wheel_state[0] < impact_angle
                        and next_state[0] >= impact_angle
                        and next_state[1] > 0)

        if crossed_impact:

            # ------------------------------------------------
            # Find the impact time by repeatedly halving
            # the timestep.
            # ------------------------------------------------

            low_dt = 0.0
            high_dt = dt

            for _ in range(50):

                mid_dt = 0.5 * (low_dt + high_dt)

                mid_state = rk4(current_time,wheel_state,mid_dt,rimless_wheel_continuous,params)

                if mid_state[0] < impact_angle:
                    low_dt = mid_dt
                else:
                    high_dt = mid_dt

                if (abs(mid_state[0] - impact_angle) < impact_tolerance):
                    break

            impact_dt = high_dt

            wheel_state = rk4(current_time,wheel_state,impact_dt,rimless_wheel_continuous,params)

            current_time += impact_dt

            wheel_state[0] = impact_angle

            times.append(current_time)
            angles.append(wheel_state[0])
            angular_velocities.append(wheel_state[1])

            impact_velocities.append(wheel_state[1])

            wheel_state = spoke_reset(
            wheel_state,
            params)

        else:

            # ------------------------------------------------
            # No impact: accept the normal large RK4 step
            # ------------------------------------------------

            wheel_state = next_state
            current_time += dt

    return (np.array(times),np.array(angles),np.array(angular_velocities),np.array(impact_velocities))


# ============================================================
# SANITY CHECKS
# ============================================================
if __name__ == "__main__":

    # ============================================================
    # Parameters
    # ============================================================

    params = generate_params()

    params["slope_angle"] = np.deg2rad(40)

    # ============================================================
    # Sanity Check 1: Angle vs. time
    # ============================================================

    initial_state = np.array([np.deg2rad(20),0])

    times, angles, angular_velocities, impact_velocities = simulate_rimless_wheel(initial_state,params,time_step=0.001,total_time=10.0)

    print("theta:", np.rad2deg(angles[:10]))
    print("theta_dot:", angular_velocities[:10])

    plt.figure()

    plt.plot(times,angles)

    plt.xlabel("Time (s)")
    plt.ylabel(r"$\theta$ (rad)")
    plt.title("Rimless Wheel Angle")
    plt.grid()

    plt.savefig("Rimless Wheel Angle assgn 1.png")

    plt.close()

    # ============================================================
    # Sanity Check 2: Theta vs. theta_dot
    # ============================================================

    params = generate_params()

    params["slope_angle"] = np.deg2rad(20)

    theta_deg = 20
    theta_dot = 0

    initial_state = np.array([np.deg2rad(theta_deg),theta_dot])

    times, angles, angular_velocities, impact_velocities = simulate_rimless_wheel(initial_state,params,time_step=0.001,total_time=20.0)

    plt.figure()

    plt.plot(np.rad2deg(angles),angular_velocities)

    plt.xlabel(r"$\theta$ (degrees)")
    plt.ylabel(r"$\dot{\theta}$ (rad/s)")

    plt.title(
        f"Rimless Wheel Phase Portrait: "
        f"({theta_deg}°, {theta_dot} rad/s)")

    plt.grid()

    plt.savefig("Rimless Wheel Phase Portrait assgn 1.png")

    plt.close()




