poincare grid resolution testing:


To select the numerical resolution of the state–action grid, a grid-refinement study was performed. The Poincaré-section state was parameterized by \(\dot{\theta}\), while the control input was parameterized by the angle of attack \(\alpha\). Both grids were progressively refined while holding their respective ranges fixed.

For each resolution, the state–action map was recomputed and the resulting policy was compared with that obtained at the next finer resolution. The policy difference was measured using the mean absolute change in selected angle of attack,

$$ \mathrm{error} = \frac{1}{N} \sum_i |\alpha_i^{\mathrm{fine}}-\alpha_i^{\mathrm{coarse}}|. $$

A convergence tolerance was selected based on the total allowable angle-of-attack range. The \(\alpha\) range used here is

$$ \Delta\alpha_{\mathrm{range}} = \frac{\pi}{7}-\frac{\pi}{8} = 0.05610\ \mathrm{rad}, $$

and the convergence tolerance was set to \(1\%\) of this range,

$$ \epsilon = 0.01\Delta\alpha_{\mathrm{range}} = 5.61\times10^{-4}\ \mathrm{rad}. $$

The grid was considered converged when the mean policy change fell below this tolerance for two consecutive refinements. The initial refinement sequence was \(21\times5\), \(41\times9\), \(81\times17\), \(161\times33\), and \(321\times65\) state–action resolutions. The mean policy difference decreased from \(0.02094\) rad to \(0.00351\) rad and then to \(0.00132\) rad over the final three comparable refinements, indicating decreasing sensitivity to grid resolution, although the specified convergence tolerance had not yet been reached. Further refinement was therefore performed near the apparent convergence region rather than treating the initial maximum resolution as sufficient.

