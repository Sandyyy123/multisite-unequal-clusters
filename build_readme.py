#!/usr/bin/env python3
"""Write README.md with the headline numbers injected from simulation_results.json."""

import json
import pathlib

HERE = pathlib.Path(__file__).parent
R = json.loads((HERE / "simulation_results.json").read_text())
S1, S2, S3 = R["s1_design_effect"], R["s2_type_i_error"], R["s3_informative_cluster_size"]

README = f"""# Unequal enrollment across sites in a multisite trial

What unbalanced site sizes actually do to a mixed-effects analysis, and what they do not.

A mixed-effects model does **not** assume equal numbers of participants per site. Likelihood-based
estimation uses each site's actual contribution and there is no balanced-design requirement anywhere
in it. That part of the usual worry is unfounded.

Unequal enrollment does, however, change four things that analysis plans routinely miss. This
repository quantifies three of them by simulation rather than by assertion.

```
python sim_unequal_clusters.py      # writes simulation_results.json
```

Seed `{R['seed']}`, fixed. numpy + statsmodels only.

## The enrollment pattern used

{S1['n_sites']} sites, {S1['n_total']} participants, sizes `{S1['site_sizes']}`.
Mean site size {S1['mean_site_size']}, coefficient of variation **{S1['cv_site_size']:.3f}**, ICC {S1['icc']}.
The largest site is {max(S1['site_sizes'])/min(S1['site_sizes']):.1f}x the smallest.

## S1. The design effect that ignores variability in site size

The common form uses only the mean site size. The Eldridge et al. (2006) form adds the CV.

| Formula | Design effect |
|---|---|
| `1 + (m - 1) * ICC` (assumes equal sites) | {S1['de_equal_assumption']:.4f} |
| `1 + (m(1 + CV^2) - 1) * ICC` (actual) | {S1['de_unequal_actual']:.4f} |

The equal-size formula understates the required variance inflation by
**{S1['variance_understated_pct']:.1f}%**. A study powered for {S1['n_needed_equal']} analysable
participants needs about **{S1['n_needed_unequal']}** to hold the same power.

Eldridge et al. give the decision rule directly: below a CV of 0.23 the adjustment is negligible,
above it most trials should account for variable cluster size. This enrollment pattern sits at
CV = {S1['cv_site_size']:.3f}, comfortably above that threshold.

## S2. Unequal sites plus a site-varying effect equals anti-conservative inference

Data generated under a true null with a genuine site-by-treatment interaction
(SD of the site-specific effect = {S2['tau_site_treatment_effect']}), then analysed three ways.
{S2['nrep_fitted']:,} replicates, nominal alpha {S2['nominal_alpha']}.

| Specification | Empirical type-I error |
|---|---|
| Random intercept only, z reference | **{S2['type1_random_intercept_z']:.3f}** |
| Random slope for treatment, z reference | {S2['type1_random_slope_z']:.3f} |
| Random slope, t on k-2 df | **{S2['type1_random_slope_t_kminus2']:.3f}** |

Omitting the site-level random slope for treatment inflates the false positive rate to
{S2['type1_random_intercept_z']*100:.1f}%, more than three times nominal. Restoring the slope brings it
to {S2['type1_random_slope_z']*100:.1f}%, which is the single most important fix.

A fixed t reference on k-2 df overshoots to {S2['type1_random_slope_t_kminus2']*100:.1f}%: conservative
rather than correct. A crude df rule trades one calibration error for another, which is why
Kenward-Roger, estimating the denominator df from the fitted covariance rather than a fixed count, is
preferable to any rule of thumb. The number of *sites*, not the number of participants, is what makes
a small-sample correction necessary at all.

## S3. Informative cluster size changes the estimand

When site size correlates with the site-specific effect (r = {S3['corr_site_size_with_effect']} here),
the precision-weighted mixed-model estimate and the unweighted site-average estimate answer different
questions.

| Estimator | Targets | Mean estimate |
|---|---|---|
| Mixed model, precision weighted | Participant-average effect | {S3['mean_mixed_model_estimate']:.4f} |
| Unweighted mean of site differences | Site-average effect | {S3['mean_site_average_estimate']:.4f} |

Mean absolute divergence on the same dataset: **{S3['mean_absolute_divergence']:.4f}** SD.
They differ by more than 0.05 SD in {S3['pct_reps_diverging_over_0_05']:.1f}% of replicates.
Neither is wrong. An analysis plan should say which one it is reporting.

## The fourth thing, not simulated here

With few sites, mixed-model software defaults to large-sample inference. Below roughly 30 to 40
clusters, use REML with Kenward-Roger or Satterthwaite denominator degrees of freedom for any
site-level or site-varying term. Below about 5 to 7 sites, fixed site effects plus site-by-treatment
interactions are often the more honest specification, since the between-site variance is barely
estimable.

## Scope

Participants are modelled at the primary contrast rather than as an explicit three-level
repeated-measures structure. The question under study is site-level clustering with unequal n;
collapsing the within-participant level isolates that question without changing the site-level
conclusions. For a real three-level design the same points apply with a participant random intercept
added.

## Reference

Eldridge SM, Ashby D, Kerry S. Sample size for cluster randomized trials: effect of coefficient of
variation of cluster size and analysis method. *International Journal of Epidemiology* 2006.
PMID 16943232. https://doi.org/10.1093/ije/dyl129
"""

(HERE / "README.md").write_text(README, encoding="utf-8")
print(f"Wrote README.md ({len(README):,} chars)")
