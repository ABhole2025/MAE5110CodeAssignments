Poincare grid resolution testing:


To select the numerical resolution of the state–action grid, a grid-refinement study was performed. The state was represented by \(\dot{\theta}\), and the control input was the angle of attack \(\alpha\). The ranges of both variables were kept fixed while the number of grid points was increased.

For each grid resolution,  the state–action map and was recomputed and the resulting policy was compared to the policy from the next finer grid. The difference between two policies was measured by the mean absolute change in the selected angle of attack:

$$ \mathrm{error} = \frac{1}{N} \sum_i |\alpha_i^{\mathrm{fine}}-\alpha_i^{\mathrm{coarse}}|. $$

I wanted the allowable policy error to be small relative to the range of possible \(\alpha\) values, rather than just picking an arbitrary number. The total \(\alpha\) range is

$$ \Delta\alpha_{\mathrm{range}} = \frac{\pi}{7}-\frac{\pi}{8} = 0.05610\ \mathrm{rad}, $$

and the convergence tolerance was set to \(1\%\) of this range,

$$ \epsilon = 0.01\Delta\alpha_{\mathrm{range}} = 5.61\times10^{-4}\ \mathrm{rad}. $$

Basically, the resolution was considered 'good enough' when the average change in selected \(\alpha\) was less than \(0.000561\) rad for two consecutive refinements.


Relatively large increments in resolution were swept first to see how the policy changed as the grid was made finer. The initial sequence was:

$$ 21\times5,\quad 41\times9,\quad 81\times17,\quad 161\times33,\quad 321\times65. $$

The mean policy difference decreased as the grid was refined:

$$ 0.020937 \rightarrow 0.003506 \rightarrow 0.001321\ \mathrm{rad}. $$

This showed that the policy was becoming less sensitive to the grid resolution, but the \(321\times65\) grid was still above the \(0.000561\)-rad tolerance.

(PLOT FOR THIS SECTION)


Zoomed-in refinement

Since the policy difference was clearly decreasing, the grid was then refined in smaller increments near the apparent convergence region. Starting from \(321\times65\), the resolutions tested were:

$$ 321\times65 \rightarrow 341\times69 \rightarrow 361\times73. $$

The results were:

| Refinement | Mean \(|\Delta\alpha|\) |
|---|---:|
| \(321\times65 \rightarrow 341\times69\) | \(0.000311\) rad |
| \(341\times69 \rightarrow 361\times73\) | \(0.000442\) rad |

Both values are below the \(0.000561\)-rad tolerance. Therefore, the convergence criterion was satisfied for two consecutive refinements.

The selected grid resolution was therefore

$$ \boxed{361\times73} $$

or 361 \(\dot{\theta}\) points and 73 \(\alpha\) points. At this resolution,

$$ \Delta\dot{\theta}=0.012304\ \mathrm{rad/s}. $$

[Zoomed-in grid-refinement plot]




(targer theta dot = 4.05)
========================================
FINAL POINCARE GRID
========================================
Using 361 state points x 73 alpha points
  Simulating 26,353 state-action pairs...
  Progress: 100.0% (26,353/26,353) Elapsed: 0.5 min
Maximum steps to RoA: 4
Candidate initial conditions:
  theta_dot = 3.678902 rad/s
  theta_dot = 3.691206 rad/s
  theta_dot = 3.703510 rad/s
  theta_dot = 3.715814 rad/s
  theta_dot = 3.728118 rad/s
  theta_dot = 3.740422 rad/s
  theta_dot = 3.752726 rad/s
  theta_dot = 3.765030 rad/s
  theta_dot = 3.777334 rad/s
  theta_dot = 3.789638 rad/s
  theta_dot = 3.801942 rad/s
  theta_dot = 3.814246 rad/s
  theta_dot = 3.826550 rad/s
  theta_dot = 3.838854 rad/s
  theta_dot = 3.851158 rad/s
  theta_dot = 3.863462 rad/s
  theta_dot = 3.875766 rad/s
  theta_dot = 3.888070 rad/s
  theta_dot = 3.900374 rad/s
  theta_dot = 3.912678 rad/s
  theta_dot = 3.924982 rad/s
  theta_dot = 3.937286 rad/s
  theta_dot = 3.949590 rad/s
  theta_dot = 3.961894 rad/s
  theta_dot = 3.974198 rad/s
  theta_dot = 3.986502 rad/s
  theta_dot = 3.998806 rad/s
  theta_dot = 4.011110 rad/s
  theta_dot = 4.023414 rad/s
  theta_dot = 4.035718 rad/s
  theta_dot = 4.048022 rad/s
  theta_dot = 4.060326 rad/s
  theta_dot = 4.072630 rad/s
  theta_dot = 4.084934 rad/s
  theta_dot = 4.097238 rad/s
  theta_dot = 4.109542 rad/s
  theta_dot = 4.121846 rad/s
  theta_dot = 4.134150 rad/s
  theta_dot = 4.146454 rad/s
  theta_dot = 4.158758 rad/s
  theta_dot = 4.171063 rad/s
  theta_dot = 4.183367 rad/s
  theta_dot = 4.195671 rad/s
  theta_dot = 4.207975 rad/s
  theta_dot = 4.220279 rad/s
  theta_dot = 4.232583 rad/s
  theta_dot = 4.244887 rad/s
  theta_dot = 4.257191 rad/s
  theta_dot = 4.269495 rad/s
  theta_dot = 4.281799 rad/s
  theta_dot = 4.294103 rad/s
  theta_dot = 4.306407 rad/s
  theta_dot = 4.318711 rad/s
  theta_dot = 4.331015 rad/s
  theta_dot = 4.343319 rad/s
  theta_dot = 4.355623 rad/s
  theta_dot = 4.367927 rad/s
  theta_dot = 4.380231 rad/s
  theta_dot = 4.392535 rad/s
  theta_dot = 4.404839 rad/s
  theta_dot = 4.417143 rad/s
  theta_dot = 4.429447 rad/s
Reachable states: 345/361
Delta theta_dot: 0.012304 rad/s
Maximum steps to RoA: 4

Selected initial condition: theta_dot = 4.048022 rad/s
Steps to RoA = 4
First control alpha = 0.392699 rad

Policy sequence:
Step 1: theta_dot = 4.048022 rad/s, alpha = 0.392699 rad
         -> next theta_dot = 2.846056 rad/s
Step 2: theta_dot = 2.842228 rad/s, alpha = 0.392699 rad
         -> next theta_dot = 1.989288 rad/s
Step 3: theta_dot = 1.993251 rad/s, alpha = 0.430099 rad
         -> next theta_dot = 1.158812 rad/s
Step 4: theta_dot = 1.156578 rad/s, alpha = 0.448020 rad
         -> next theta_dot = 0.182238 rad/s