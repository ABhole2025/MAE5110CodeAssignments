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
Sanity Check 1: Plotted angle (theta) vs time just to get a general sense of movement and whether it matched the Idea I had in my head. For instance, a wheel staying stationary would be a striaght line, while a rolling wheel would have a periodic sawtooth plot as the angle resets after each impact.

-------------------------------------------------------------------------

2. (note for -pi to pi, 0 to 18, 101x101: Number of equilibrium points: 0
Number of limit-cycle points: 9235
Number of unclassified points: 966)

(note for 0 to 2pi, 0 to 18, 360x360: Number of equilibrium points: 1
Number of limit-cycle points: 12599
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

============================================================
Slope SWEEP SUMMARY
============================================================
Slope = 5
  Equilibrium:      0 (  0.00%)
  Limit cycle:   8909 ( 89.09%)
  Unclassified:  1091 ( 10.91%)

Slope = 10
  Equilibrium:      0 (  0.00%)
  Limit cycle:   8960 ( 89.60%)
  Unclassified:  1040 ( 10.40%)

Slope = 15
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9005 ( 90.05%)
  Unclassified:   995 (  9.95%)

Slope = 20
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9055 ( 90.55%)
  Unclassified:   945 (  9.45%)

Slope = 25
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9101 ( 91.01%)
  Unclassified:   899 (  8.99%)

Slope = 30
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9147 ( 91.47%)
  Unclassified:   853 (  8.53%)

Slope = 35
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9200 ( 92.00%)
  Unclassified:   800 (  8.00%)



============================================================
Number of spokes SWEEP SUMMARY
============================================================
Number of spokes = 6
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9054 ( 90.54%)
  Unclassified:   946 (  9.46%)

Number of spokes = 7
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9055 ( 90.55%)
  Unclassified:   945 (  9.45%)

Number of spokes = 8
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9055 ( 90.55%)
  Unclassified:   945 (  9.45%)

Number of spokes = 9
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9055 ( 90.55%)
  Unclassified:   945 (  9.45%)

Number of spokes = 10
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9055 ( 90.55%)
  Unclassified:   945 (  9.45%)

Number of spokes = 11
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9055 ( 90.55%)
  Unclassified:   945 (  9.45%)

Number of spokes = 12
  Equilibrium:      0 (  0.00%)
  Limit cycle:   9055 ( 90.55%)
  Unclassified:   945 (  9.45%)

-------------------------------------------------------------------------

