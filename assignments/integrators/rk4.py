def rk4(t, x, dt, dynamics, params):
    k1 = dynamics(t, x, params)
    k2 = dynamics(t + dt/2, x + dt/2 * k1, params)
    k3 = dynamics(t + dt/2, x + dt/2 * k2, params)
    k4 = dynamics(t + dt, x + dt * k3, params)

    return x + dt/6 * (k1 + 2*k2 + 2*k3 + k4)

