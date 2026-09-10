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

## 1. Sanity Checks

## 1. Sanity Checks

### Model Notes

For the current model, I use the following angle convention:

* $\theta$ is measured from the **global upward vertical**.
* Positive $\theta$ is counterclockwise, while negative $\theta$ is clockwise.
* The downhill direction of the slope is clockwise.
* The slope angle is denoted by $\gamma$.
* The angle between adjacent spokes is $2\alpha$, where

  $$
  \alpha = \frac{\pi}{N}.
  $$

With this convention, the continuous dynamics while a single spoke is in contact with the ground are

$$
\ddot{\theta}
=
-\frac{g}{l}\sin(\theta+\gamma).
$$

Therefore, the continuous-time state-space dynamics are

$$
\dot{\theta} = \dot{\theta},
\qquad
\ddot{\theta}
=
-\frac{g}{l}\sin(\theta+\gamma).
$$

The $\gamma$ term appears because $\theta$ is measured relative to the **global vertical**, rather than relative to the slope normal.

#### Impact and Reset

An impact occurs when the next spoke reaches the slope. The pre-impact stance-spoke angle is

$$
\theta^- = -\gamma-\alpha.
$$

At this instant, the adjacent spoke becomes the new stance spoke. The new stance spoke is at $+\alpha$ relative to the global vertical, so the angular coordinate is shifted by

$$
\gamma+2\alpha.
$$

So the angle reset is

$$
\theta^+
=
\theta^-+\gamma+2\alpha.
$$

The new spoke then begins its trajectory at

$$
\theta^+ = \alpha.
$$

The angular velocity is reset using conservation of angular momentum about the new contact point:

$$
\dot{\theta}^+
=
\dot{\theta}^-\cos(2\alpha).
$$

Therefore, the complete impact/reset map used in the simulation is

$$
\boxed{
\theta^+ = \theta^-+\gamma+2\alpha,
\qquad
\dot{\theta}^+ =
\dot{\theta}^-\cos(2\alpha)
}
$$

These continuous dynamics and discrete impact/reset dynamics together define the hybrid rimless-wheel model used in the simulation.

### 1.1 Angle vs. Time

I first plotted the stance-spoke angle $\theta$ versus time to get a general sense of the wheel's motion and verify that the simulation behaved as expected. For a stationary wheel, I would expect $\theta$ to remain approximately constant. In contrast, a rolling rimless wheel should produce a periodic sawtooth-like trajectory: during each stance phase, $\theta$ evolves continuously until the next spoke reaches the slope, at which point the stance spoke switches and the angle is reset.

The figure below shows (example)

![Initial conditions (10 degrees, -5 rad/s)](Rimless_Wheel_Angle_assgn_1.png)

### 1.2 Phase Portrait

I also plotted the trajectory in state space, using $\theta$ and $\dot{\theta}$ as the state variables. The initial condition for this test was $(\theta,\dot{\theta})=(10^\circ,0)$.

![Initial conditions (10 degrees, -5 rad/s)](Rimless_Wheel_Phase_Portrait_assgn_1.png)

The phase portrait provides an additional qualitative check of the simulated dynamics by showing how angular position and angular velocity evolve together during the continuous stance phase and across discrete impacts. The repeated trajectory associated with successive impacts also provides a visual indication of the wheel approaching its periodic rolling gait.

-------------------------------------------------------------------------

2. Region of Attraction

I estimated the region of attraction (RoA) by simulating a grid of initial conditions and classifying each trajectory according to its long-term behavior. A trajectory was classified as converging to the walking limit cycle if its final five impact velocities differed by less than \(0.05\) rad/s. I also distinguished trajectories exhibiting bounded rocking behavior from those that remained unclassified.

For the \(20^\circ\) slope and \(N=8\) spokes, I used a \(100\times100\) grid of initial conditions with

$$ \theta\in[-\pi,\pi) $$

and

$$ \dot{\theta}\in[-10,10]\text{ rad/s}. $$

The simulation produced:

Equilibrium: 0 points
Bounded rocking: 120 points
Limit cycle: 6,624 points
Unclassified: 3,256 points

![RoA 100x100](RoA_with_bounded.png)

The resulting classification shows a large region of initial conditions that converge to the periodic walking gait, along with a smaller region exhibiting bounded rocking behavior. The unclassified region consists of trajectories that did not satisfy either classification criterion within the simulation time and therefore cannot automatically be interpreted as unstable or divergent.

The equilibrium of the continuous dynamics occurs at

$$ (\theta,\dot{\theta})=(-\gamma,0). $$

For the \(20^\circ\) slope used here,

$$ (\theta,\dot{\theta})=(-20^\circ,0). $$

This equilibrium is not asymptotically stable. Instead, it lies within the portion of the state space that leads to bounded rocking behavior.

The equilibrium itself does not appear as one of the classified equilibrium points in the \(100\times100\) grid because the finite grid does not necessarily contain the exact state \(\theta=-\gamma,\dot{\theta}=0\). The resolution of the grid was not made finer than 100x100 due to computing constraints.
-------------------------------------------------------------------------

3. Return Map and Floquet Multiplier

For \(N=8\) spokes and a slope angle of \(20^\circ\), I constructed a one-dimensional return map using the angular velocity immediately after each impact as the Poincaré-section variable. The trajectory was simulated until the post-impact velocity converged to a fixed point.

The simulation began from

$$ (\theta,\dot{\theta})=(20^\circ,0). $$

The return map converged to the theoretical post-impact fixed point

$$ \dot{\theta}^{+*}=-1.913409\text{ rad/s}. $$

Using a perturbation of

$$ \epsilon=0.01, $$

the return-map values were

$$ P(x^*-\epsilon)=-1.918250, $$

and

$$ P(x^*+\epsilon)=-1.908324. $$

The Floquet multiplier was

$$ \lambda = \frac{P(x^*+\epsilon)-P(x^*-\epsilon)} {2\epsilon} = 0.496331. $$

![Return map](assgn_1_Rimless_Wheel_Return_Map.png)

Because

$$ \lambda=0.496331<1, $$

the walking limit cycle is locally asymptotically stable. A perturbation from the periodic gait is therefore reduced from one step to the next.

indicating that the simulated motion has reached the expected periodic walking gait.

The pre-impact and post-impact angular velocities are related by the impact map

$$ \dot{\theta}^{+} = \dot{\theta}^{-}\cos(2\alpha), $$

where

$$ \alpha=\frac{\pi}{N}. $$

For \(N=8\),

$$ \alpha=22.5^\circ, $$

so

$$ \dot{\theta}^{-*} = \frac{\dot{\theta}^{+*}}{\cos(45^\circ)} \approx-2.7060\text{ rad/s}. $$

Therefore, the periodic gait has approximately

$$ \boxed{\dot{\theta}^{-*}=-2.7060\text{ rad/s}} $$

immediately before impact and

$$ \boxed{\dot{\theta}^{+*}=-1.9134\text{ rad/s}} $$

immediately after impact.

The negative sign is consistent with the chosen coordinate convention: clockwise rotation corresponds to downhill motion.

-------------------------------------------------------------------------
## 4. Return Map and RoA Sweeps

### Slope Sweep
Slope Sweep

I varied the slope angle from \(5^\circ\) to \(35^\circ\) while keeping the number of spokes fixed at \(N=8\). For each slope, I computed the pre-impact fixed point, post-impact fixed point, and Floquet multiplier.

|  Slope angle | Pre-impact fixed point (rad/s) | Post-impact fixed point (rad/s) | Floquet multiplier |
| -----------: | -----------------------------: | ------------------------------: | -----------------: |
|  \(5^\circ\) |                        -1.2028 |                         -0.8505 |           0.503190 |
| \(10^\circ\) |                        -1.7772 |                         -1.2567 |           0.493510 |
| \(15^\circ\) |                        -2.2631 |                         -1.6003 |           0.508878 |
| \(20^\circ\) |                        -2.7060 |                         -1.9134 |           0.496331 |
| \(25^\circ\) |                        -3.1214 |                         -2.2071 |           0.501953 |
| \(30^\circ\) |                        -3.5164 |                         -2.4865 |           0.508047 |
| \(35^\circ\) |                        -3.8948 |                         -2.7540 |           0.492653 |

The fixed-point angular velocity increases in magnitude as the slope angle increases. This is consistent with the greater gravitational component driving the wheel downhill on steeper slopes.

In contrast, the Floquet multiplier remains close to \(0.5\) throughout the sweep. All values remain well below one, indicating that the walking gait remains locally asymptotically stable across the tested slope range. The relatively small variation in the multiplier also suggests that the local convergence rate is not strongly affected by slope angle over this range.

![Slope sweep for Floquet multiplier](assgn_1_Floquet_vs_Slope.png)




(THIS ROA STUFF IS OLD AND NEEDS TO BU EPDATED LEAVE IT FOR NOW)
Each sweep used a $101\times101$ grid, for a total of 10,201 initial conditions.

| Slope angle | Equilibrium | Limit cycle | Unclassified |
|---:|---:|---:|---:|
| $5^\circ$  | 0 (0.00%) | 8,909 (89.09%) | 1,091 (10.91%) |
| $10^\circ$ | 0 (0.00%) | 8,960 (89.60%) | 1,040 (10.40%) |
| $15^\circ$ | 0 (0.00%) | 9,005 (90.05%) | 995 (9.95%) |
| $20^\circ$ | 0 (0.00%) | 9,055 (90.55%) | 945 (9.45%) |
| $25^\circ$ | 0 (0.00%) | 9,101 (91.01%) | 899 (8.99%) |
| $30^\circ$ | 0 (0.00%) | 9,147 (91.47%) | 853 (8.53%) |
| $35^\circ$ | 0 (0.00%) | 9,200 (92.00%) | 800 (8.00%) |

As the slope angle increased, the fraction of initial conditions classified as converging to the limit cycle increased from $89.09\%$ to $92.00\%$, while the unclassified fraction decreased from $10.91\%$ to $8.00\%$.

Increasing the slope slightly increased the region classified as belonging to the walking limit cycle over the sampled state space. However, the Floquet multiplier remained approximately $0.480$, indicating that the slope had little effect on the local convergence rate of the limit cycle.

![Slope sweep for RoA](assignment_1/RoA%20Slope%20Sweep.png)

============================================================
Slope SWEEP SUMMARY (newest, 100x100, velocity -18 to 18)
============================================================
Slope = 5
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5030 ( 50.30%)
  Unclassified:  4970 ( 49.70%)

Slope = 10
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5081 ( 50.81%)
  Unclassified:  4919 ( 49.19%)

Slope = 15
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5123 ( 51.23%)
  Unclassified:  4877 ( 48.77%)

Slope = 20
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5171 ( 51.71%)
  Unclassified:  4829 ( 48.29%)

Slope = 25
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5221 ( 52.21%)
  Unclassified:  4779 ( 47.79%)

Slope = 30
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5263 ( 52.63%)
  Unclassified:  4737 ( 47.37%)

Slope = 35
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5316 ( 53.16%)
  Unclassified:  4684 ( 46.84%)


### Number of Spokes Sweep
I next varied the number of spokes from \(N=6\) to \(N=12\), keeping the slope angle fixed at \(20^\circ\).

| Number of spokes | Pre-impact fixed point (rad/s) | Post-impact fixed point (rad/s) | Floquet multiplier |
| ---------------: | -----------------------------: | ------------------------------: | -----------------: |
|                6 |                        -2.4166 |                         -1.2083 |           0.258493 |
|                7 |                        -2.5509 |                         -1.5905 |           0.391724 |
|                8 |                        -2.7060 |                         -1.9134 |           0.496331 |
|                9 |                        -2.8716 |                         -2.1997 |           0.592395 |
|               10 |                        -3.0429 |                         -2.4617 |           0.654423 |
|               11 |                        -3.2175 |                         -2.7067 |           0.710822 |
|               12 |                        -3.3939 |                         -2.9392 |           0.752553 |

The number of spokes has a much stronger effect on the Floquet multiplier than the slope angle. As the number of spokes increases, the magnitude of both the pre-impact and post-impact fixed-point velocities increases, while the Floquet multiplier also increases.

For all tested values,

$$ |\lambda|<1, $$

so the walking gait remains locally asymptotically stable. However, the multiplier increases from approximately \(0.258\) for six spokes to \(0.753\) for twelve spokes. Since a larger multiplier closer to one corresponds to slower decay of perturbations, the walking gait becomes less strongly locally stable as the number of spokes increases.

![Slope sweep for Floquet multiplier](assgn_1_Floquet_vs_Number_of_Spokes.png)



(ROA) (THIS ROA STUFF IS OLD AND NEEDS TO BU EPDATED LEAVE IT FOR NOW)

| Number of spokes | Equilibrium | Limit cycle | Unclassified |
|---:|---:|---:|---:|
| 6  | 0 (0.00%) | 9,054 (90.54%) | 946 (9.46%) |
| 7  | 0 (0.00%) | 9,055 (90.55%) | 945 (9.45%) |
| 8  | 0 (0.00%) | 9,055 (90.55%) | 945 (9.45%) |
| 9  | 0 (0.00%) | 9,055 (90.55%) | 945 (9.45%) |
| 10 | 0 (0.00%) | 9,055 (90.55%) | 945 (9.45%) |
| 11 | 0 (0.00%) | 9,055 (90.55%) | 945 (9.45%) |
| 12 | 0 (0.00%) | 9,055 (90.55%) | 945 (9.45%) |

Over the sampled $101\times101$ state-space grid, changing the number of spokes from 6 to 12 produced almost no change in the fraction of states classified as converging to the limit cycle. The classification remained approximately $90.5\%$ limit-cycle states and $9.5\%$ unclassified states. This suggests that the global RoA, as measured by this particular grid and classification criterion, is relatively insensitive to the number of spokes.

However, the number of spokes does affect the local stability of the walking cycle. The Floquet multiplier increased as the number of spokes increased, making $\lambda$ larger and closer to 1. Therefore, although the measured global RoA changed very little in this sweep, increasing the number of spokes causes perturbations to decay more slowly from one step to the next.

![Number of spokes sweep for RoA](assignment_1/RoA%20Spoke%20Sweep.png)

============================================================
Number of spokes SWEEP SUMMARY (latest)
============================================================
Number of spokes = 6
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5170 ( 51.70%)
  Unclassified:  4830 ( 48.30%)

Number of spokes = 7
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5171 ( 51.71%)
  Unclassified:  4829 ( 48.29%)

Number of spokes = 8
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5171 ( 51.71%)
  Unclassified:  4829 ( 48.29%)

Number of spokes = 9
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5171 ( 51.71%)
  Unclassified:  4829 ( 48.29%)

Number of spokes = 10
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5171 ( 51.71%)
  Unclassified:  4829 ( 48.29%)

Number of spokes = 11
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5171 ( 51.71%)
  Unclassified:  4829 ( 48.29%)

Number of spokes = 12
  Equilibrium:      0 (  0.00%)
  Limit cycle:   5171 ( 51.71%)
  Unclassified:  4829 ( 48.29%)