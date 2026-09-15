import matplotlib.pyplot as plt
import numpy as np

from assignment_2_control import feedback_linearizing_controller
from models import inverted_pendulum_walker as model

params = {
    "gravity": 9.81,          # m/s^2
    "length": 1.0,             # m
    "mass": 1.0,               # kg
    "incline": 0.06,           # rad
    "angle_of_attack": np.pi / 8,
    "ankle_torque": 0.0,       # N m
}

kp = 4.0
kd = 2.0

# As this RoA is for the torque feedback only we keep alpha constant
alpha_min = np.pi / 8
params["angle_of_attack"] = alpha_min

