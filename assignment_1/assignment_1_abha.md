Abha Bhole
MAE 4110
-------------------------------------------------------------------------
Assignment 1 Deliverable - A markdown file reporting:

1. an explanation of your sanity checks, including what you expected and what happened; (5 pts)

2. a state-space plot showing the RoA of every stable attractor, including fixed points and limit cycles; (5 pts)

3. your one-dimensional return-map plot, with its fixed point and the identity line clearly marked; and (5 pts)

4. visualization and discussion of how the slope and number of spokes affects the RoA and local convergence (10 pts)

-------------------------------------------------------------------------
-------------------------------------------------------------------------

1.

-------------------------------------------------------------------------

2. (note for -pi to pi, 0 to 18, 101x101: Number of equilibrium points: 0
Number of limit-cycle points: 9235
Number of unclassified points: 966)

(note for 0 to 2pi, 0 to 18, 360x360: Number of equilibrium points: 1
Number of limit-cycle points: 129600
Number of unclassified points: 0)

-------------------------------------------------------------------------

3. (N=8, Slope=20 degrees, initial_state = np.array([
    np.deg2rad(25), 0]))

Pre-impact fixed point: 3.393514872020504 rad/s
Post-impact fixed point: 2.3995773780630976 rad/s
Perturbed post-impact velocities:
Low: 2.389577378063098 -> 2.3943976217546945
High: 2.4095773780630974 -> 2.403994583035602
Estimated Floquet multiplier: 0.47984806404537395

-------------------------------------------------------------------------

4.

The Floquet multiplier remained essentially constant as slope inclination was varied from 5° to 35°. The numerical value was approximately 0.480



-------------------------------------------------------------------------

