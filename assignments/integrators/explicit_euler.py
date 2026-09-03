def explicit_euler(t, x, dt, dynamics, params):
    return x + dt * dynamics(t, x, params)
