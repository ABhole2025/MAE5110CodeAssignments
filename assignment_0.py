import time
start = time.time()

import matplotlib.pyplot as plt
import numpy as np

from integrators import explicit_euler, rk4
from models import pendulum as model

# Basic simulation of the pendulum
params = {
    "gravity": 9.81,  # gravity m/s^2)
    "length": 1,  # rod length (m)
    "mass": 0.2,  # point mass at end of rod (kg)
    "damping_coeff": 0.0,  # damping coefficient (kg*m^2/s)
}

# some set-up
initial_state = np.array([np.pi / 4, 0.0])

timestep = 1e-5
sim_time = 5.0

n_timesteps = int(sim_time / timestep) + 1
time_traj = np.arange(n_timesteps) * timestep
state_traj = np.zeros((2, n_timesteps))
state_traj[:, 0] = initial_state

# simulation loop
for step, t in enumerate(time_traj[:-1]):
    state_traj[:, step + 1] = state_traj[:, step] + timestep * model.dynamics(
        t, state_traj[:, step], params
    )

# sanity check the energies: since there is no actuation, and no damping, total energy should stay
# constant. If we turn on the damping coefficient, it should slowly bleed out energy until it comes to
# a stand-still.

potential_energy, kinetic_energy = model.calculate_energy(state_traj, params)

plt.figure()
plt.plot(time_traj, potential_energy, label="Potential energy")
plt.plot(time_traj, kinetic_energy, label="Kinetic energy")
plt.plot(time_traj, potential_energy + kinetic_energy, label="Total energy")
plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")
plt.title("Pendulum energy - default (euler)")
plt.legend()
plt.tight_layout()
plt.savefig("Pendulum energy - default (euler).png")
plt.close()

plt.figure()
plt.plot(state_traj[0, :], state_traj[1, :])
plt.xlabel("Angle (rad)")
plt.ylabel("Angular velocity (rad/s)")
plt.title("Default Euler: Phase portrait")
plt.tight_layout()
plt.savefig("Default Euler: Phase portrait.png")
plt.close()

def run_simulation(timestep, integrator, sim_time=5.0):

    n_timesteps = int(sim_time / timestep) + 1
    time_traj = np.arange(n_timesteps) * timestep

    state_traj = np.zeros((2, n_timesteps))
    state_traj[:, 0] = initial_state

    for step, t in enumerate(time_traj[:-1]):
        state_traj[:, step + 1] = integrator(t, state_traj[:, step], timestep, model.dynamics, params
        )

    potential_energy, kinetic_energy = model.calculate_energy(state_traj, params)
    return state_traj, time_traj, potential_energy, kinetic_energy


timesteps_for_sweep = [
    1e-4, 2e-4, 5e-4,
    1e-3, 2e-3, 5e-3,
    1e-2, 2e-2, 5e-2,
    1e-1]

# euler sweep

def is_stable(dt, integrator, tol=0.01):
    state_traj, time_traj, PE, KE = run_simulation(dt, integrator)
    E = PE + KE
    E0 = E[0]
    drift = np.max(np.abs(E - E0)) / E0
    return drift < tol

stable_euler = []

for dt in timesteps_for_sweep:
    if is_stable(dt, explicit_euler):
        stable_euler.append(dt)

dt_euler_max = max(stable_euler)
print("Euler largest stable dt:", dt_euler_max)

'''
#plot of euler sweep
plt.figure()
for dt in timesteps_for_sweep:
    state_traj, time_traj, PE, KE = run_simulation(dt, explicit_euler)
    plt.plot(time_traj, PE + KE, label=f"dt={dt}")
plt.legend()
plt.savefig("euler sweep.png")
plt.close()
'''

# RK4
dt_rk4 = 1e-5
state_traj, time_traj, PE, KE = run_simulation(dt_rk4, rk4)

plt.figure()
plt.plot(time_traj, PE, label="Potential")
plt.plot(time_traj, KE, label="Kinetic")
plt.plot(time_traj, PE + KE, label="Total")
plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")
plt.title("Basic RK4: Energy")
plt.legend()
plt.tight_layout()
plt.savefig("Basic RK4: Energy.png")
plt.close()

plt.figure()
plt.plot(state_traj[0, :], state_traj[1, :])
plt.xlabel("Angle (rad)")
plt.ylabel("Angular velocity (rad/s)")
plt.title("Basic RK4: Phase portrait")
plt.tight_layout()
plt.savefig("Basic RK4: Phase portrait.png")
plt.close()


# RK4 SWEEP
stable_rk4 = []
for dt in timesteps_for_sweep:
    if is_stable(dt, rk4):
        stable_rk4.append(dt)

dt_rk4_max = max(stable_rk4)
print("RK4 largest stable dt:", dt_rk4_max)

'''
#plot of rk4 sweep
plt.figure()
for dt in timesteps_for_sweep:
    state_traj, time_traj, PE, KE = run_simulation(dt, rk4)
    plt.plot(time_traj, PE + KE, label=f"dt={dt}")
plt.legend()
plt.savefig("rk4 sweep.png")
plt.close()
'''


#timing the methods
import timeit

# Same timestep for both
dt_same = 1e-4

time_euler_same = timeit.timeit(
    stmt="run_simulation(dt_same, explicit_euler)",
    setup="from __main__ import run_simulation, explicit_euler, dt_same",
    number=1)

time_rk4_same = timeit.timeit(
    stmt="run_simulation(dt_same, rk4)",
    setup="from __main__ import run_simulation, rk4, dt_same",
    number=1)

print("\n=== TIMEIT: Same dt ===")
print(f"Euler (dt={dt_same}): {time_euler_same:.4f} seconds")
print(f"RK4   (dt={dt_same}): {time_rk4_same:.4f} seconds")


# Largest stable timestep for each
dt_euler = dt_euler_max
dt_rk4 = dt_rk4_max

time_euler_max = timeit.timeit(
    stmt="run_simulation(dt_euler, explicit_euler)",
    setup="from __main__ import run_simulation, explicit_euler, dt_euler",
    number=1)

time_rk4_max = timeit.timeit(
    stmt="run_simulation(dt_rk4, rk4)",
    setup="from __main__ import run_simulation, rk4, dt_rk4",
    number=1)

print("\n=== TIMEIT: Each integrator's largest stable dt ===")
print(f"Euler (dt={dt_euler}): {time_euler_max:.4f} seconds")
print(f"RK4   (dt={dt_rk4}): {time_rk4_max:.4f} seconds")

print("Total runtime:", time.time() - start)



def plot_relative_energy_error(integrator, name):
    plt.figure()
    for dt in timesteps_for_sweep:
        state_traj, time_traj, PE, KE = run_simulation(dt, integrator)
        E = PE + KE
        E0 = E[0]
        rel_err = (E - E0) / E0
        plt.plot(time_traj, rel_err, label=f"dt={dt}")
    plt.xlabel("Time (s)")
    plt.ylabel("Relative energy error")
    plt.title(f"{name}: Relative Energy Error")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{name} relative energy error.png")
    plt.close()

plot_relative_energy_error(explicit_euler, "Euler")
plot_relative_energy_error(rk4, "RK4")
