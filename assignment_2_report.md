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

