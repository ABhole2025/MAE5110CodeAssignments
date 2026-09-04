import matplotlib.pyplot as plt
import numpy as np
import rimless_wheel as model

# Sanity Check 1: Angle vs time plot

params = model.generate_params()
params["slope_angle"] = np.deg2rad(20)

initial_state = np.array([np.deg2rad(25), 0])

times, angles, angular_velocities = model.simulate_rimless_wheel(
    initial_state,
    params,
    time_step=0.001,
    total_time=20.0
)

print("theta:", np.rad2deg(angles[:10]))
print("theta_dot:", angular_velocities[:10])

plt.figure()
plt.plot(times, angles)
plt.xlabel("Time (s)")
plt.ylabel(r"$\theta$ (rad)")
plt.title("Rimless Wheel Angle")
plt.grid()
plt.savefig("Rimless Wheel Angle.png")
plt.close()


# Sanity Check 2: theta vs theta_dot

plt.figure()

plt.plot(angles, angular_velocities)

plt.xlabel(r"$\theta$ (rad)")
plt.ylabel(r"$\dot{\theta}$ (rad/s)")
plt.title("Rimless Wheel Phase Portrait")
plt.grid()

plt.savefig("Rimless Wheel Phase Portrait.png")
plt.close()

'''
initial_conditions = [
    (20, 0),
    (24, 0),
    (25, 0),
    (26, 0),
    (30, 0),]

plt.figure()

for theta_deg, theta_dot in initial_conditions:
    params = model.generate_params()

    initial_state = np.array([
        np.deg2rad(theta_deg),
        theta_dot
    ])

    times, angles, angular_velocities = model.simulate_rimless_wheel(
        initial_state,
        params,
        time_step=0.001,
        total_time=20.0
    )

    plt.plot(
        np.rad2deg(angles),
        angular_velocities,
        label=f"({theta_deg}°, {theta_dot})"
    )

plt.xlabel(r"$\theta$ (degrees)")
plt.ylabel(r"$\dot{\theta}$ (rad/s)")
plt.title("Rimless Wheel Phase Portrait")
plt.legend()
plt.grid()
plt.savefig("Rimless Wheel Phase Portrait sweep.png")
plt.close()

'''

'''
# Sanity Check 3: Slope angle sweep

plt.figure()

for gamma_deg in [0, 50, 89]:

    params = model.generate_params()
    params["slope_angle"] = np.deg2rad(gamma_deg)

    initial_state = np.array([0.0, 2.0])

    times, angles, angular_velocities = model.simulate_rimless_wheel(
        initial_state,
        params,
        time_step=0.001,
        total_time=10.0
    )

    # Convert theta to angle measured from the slope normal
    normal_angle = angles + params["slope_angle"]

    plt.plot(
        times,
        angles,
        label=f"{gamma_deg}°: theta (global vertical)"
    )

    plt.plot(
        times,
        normal_angle,
        "--",
        label=f"{gamma_deg}°: angle from normal"
    )

plt.xlabel("Time (s)")
plt.ylabel("Angle (rad)")
plt.title("Rimless Wheel: Global Angle and Slope-Normal Angle")
plt.legend()
plt.grid()
plt.savefig("Rimless Wheel Slope Sweep.png")
plt.close()
'''