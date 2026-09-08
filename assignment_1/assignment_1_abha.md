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

### 1.1 Angle vs. Time

I first plotted the stance-spoke angle $\theta$ versus time to get a general sense of the wheel's motion and verify that the simulation behaved as expected. For a stationary wheel, I would expect $\theta$ to remain constant, producing a horizontal line. In contrast, a rolling rimless wheel should produce a periodic sawtooth-like trajectory, since the stance spoke angle increases until impact and then resets when the next spoke becomes the stance spoke.

The figure below shows two example simulations with zero initial angular velocity. The first uses $(\theta,\dot{\theta})=(20^\circ,0)$, while the second uses $(\theta,\dot{\theta})=(-40^\circ,0)$ with a slope angle of $40^\circ$.

![Initial conditions (20^\circ,0)](assignment_1/20_0_angle_time plot.png)
![Initial conditions (-40^\circ,0)](assignment_1/slope_40_minus40_0_angle_time.png)

These plots provide a qualitative check that the continuous dynamics and impact/reset behavior produce the expected rimless-wheel motion.

### 1.2 Phase Portrait

I also plotted the trajectory in state space, using $\theta$ and $\dot{\theta}$ as the state variables. The initial condition for this test was $(\theta,\dot{\theta})=(10^\circ,0)$.

![Initial conditions (10^\circ,0)](assignment_1/phase_10_0_plot.png)

The phase portrait provides an additional qualitative check of the simulated dynamics by showing how angular position and angular velocity evolve together through the continuous and impact phases of the motion.

-------------------------------------------------------------------------

## 2. Region of Attraction

I estimated the region of attraction (RoA) by simulating a grid of initial conditions and classifying each trajectory based on its long-term behavior. A trajectory was classified as converging to the walking limit cycle if its final five impact velocities differed by less than 0.05 rad/s.

For a $101\times101$ grid with $\theta\in[-\pi,\pi)$ and $\dot{\theta}\in[0,18]$ rad/s, the simulation produced:

- Equilibrium: 0 points
- Limit cycle: 9235 points
- Unclassified: 966 points

(assignment_1/Rimless_Wheel_RoA_101x101_minuspi_to_pi.png)

Having run the rimless wheel sim on it's own before this, I found an unstable equlilibium (no movement unless perturbed) at $(\theta,\dot{\theta})=(-\gamma,0)$. For the $20^\circ$ slope used here, this corresponds to approximately $(-20^\circ,0)$. The equilibrium does not appear in the $101\times101$ grid because the finite grid spacing is too coarse sample this exact point. However, a finre grid could not be used due to computing time constraints. Therefore, the absence of an equilibrium point in the classification is a consequence of the grid resolution rather than the equilibrium being absent from the system.

I also repeated the calculation using a finer $360\times360$ grid with $\theta\in[0,2\pi)$ and $\dot{\theta}\in[0,18]$ rad/s - such a fine grid was only used on this one occasion because it was too time-consuming to do repeatedly. This produced:

- Equilibrium: 1 point
- Limit cycle: 129599 points
- Unclassified: 0 points

(assignment_1/Rimless Wheel RoA 360x360 0to2pi 0to18.png)

The finer grid happened to include the equilibrium point, while all other sampled initial conditions were classified as converging to the walking limit cycle. The equilibrium point is a single point on the plot and due to the fine resolution, it is not visible, even though it is on there.

This result is consistent with the expected behavior of the model.

-------------------------------------------------------------------------

## 3. Return Map and Floquet Multiplier

For $N=8$ spokes and a slope angle of $20^\circ$, I constructed a one-dimensional return map using the pre-impact angular velocity as the Poincaré-section variable. The initial condition used to generate the trajectory was

$$
(\theta,\dot{\theta})=(25^\circ,0).
$$

The resulting return map converged to a fixed point at

$$
\dot{\theta}^-_* = 3.394\ \text{rad/s},
$$

where $\dot{\theta}^-$ denotes the angular velocity immediately before impact. The corresponding post-impact angular velocity was

$$
\dot{\theta}^+_* = 2.400\ \text{rad/s}.
$$

![Return map](assignment_1/Rimless Wheel Return Map.png)

To estimate the Floquet multiplier, I perturbed the post-impact fixed point by $\pm0.01$ rad/s and measured the resulting post-impact velocity at the next crossing. The perturbations produced

$$
2.3896 \rightarrow 2.3944\ \text{rad/s}
$$

and

$$
2.4096 \rightarrow 2.4040\ \text{rad/s}.
$$

Using the local slope of the return map gave an estimated Floquet multiplier of

$$
\lambda \approx 0.480.
$$

Since $|\lambda|<1$, small perturbations from the fixed point decay from one step to the next, indicating that the rolling limit cycle is locally stable.

-------------------------------------------------------------------------
### Slope Sweep

The Floquet multiplier remained essentially constant as slope inclination was varied from $5^\circ$ to $35^\circ$. The numerical value was approximately $0.480$.

![Slope sweep for Floquet Multiplier](assignment_1/Floquet vs Slope.png)

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

![Slope sweep for RoA](assignment_1/RoA Slope Sweep.png)


### Number of Spokes Sweep

The number of spokes was varied from 6 to 12 while keeping the slope angle fixed at $20^\circ$. The same $101\times101$ grid was used for each case.

![Number of spokes sweep for Floquet Multiplier](assignment_1/Floquet vs Number of Spokes.png)

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

However, the number of spokes does affect the local stability of the walking cycle. The Floquet multiplier as increasing the number of spokes makes $\lambda$ larger and closer to 1. Therefore, although the measured global RoA changed very little in this sweep, increasing the number of spokes causes perturbations to decay more slowly from one step to the next.

![Number of spokes sweep for RoA](assignment_1/RoA Spoke Sweep.png)

