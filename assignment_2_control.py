import matplotlib.pyplot as plt
import numpy as np


def feedback_linearizing_controller(state, params, kp, kd):
    theta, theta_dot = state

    gravity = params["gravity"]
    mass = params["mass"]
    length = params["length"]

    gravity_cancellation = -mass * gravity * length * np.sin(theta)
    stabilizing_term = -mass * length**2 * (kp * theta + kd * theta_dot)

    ankle_torque = gravity_cancellation + stabilizing_term

    torque_min = -0.1 * mass * gravity * length
    torque_max = 0.05 * mass * gravity * length

    return np.clip(ankle_torque, torque_min, torque_max)

