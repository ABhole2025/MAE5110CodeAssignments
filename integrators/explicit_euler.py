def explicit_euler(dynamics, t, x, dt, params):
    return x + dt * dynamics(t, x, params)