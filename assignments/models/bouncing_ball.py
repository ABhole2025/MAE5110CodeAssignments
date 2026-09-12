import numpy as np

def dynamics(t, state, params):
    """
    Bouncing ball in free fall
    state = [y, v]
    """
    y, v = state
    g = params["gravity"]

    dy = v
    dv = -g

    return np.array([dy, dv])

def collision(state, params):
    """
    if the ball hits the ground while moving downward,
    flip and scale the velocity using the restitution coefficient.
    """
    y, v = state
    restitution = params["restitution"]

    if y <= 0 and v < 0:
        return np.array([0.0, -restitution * v])

    return state

def generate_params():
    return {
        "gravity": 9.81,
        "restitution": 0.8,   # coefficient of restitution (0–1)
        "mass": 1.0
    }

#energy calculation

def calculate_energy(state, params):

    y, v = state
    m = params["mass"]
    g = params["gravity"]

    kinetic = 0.5 * m * v**2
    potential = m * g * y

    return kinetic, potential
