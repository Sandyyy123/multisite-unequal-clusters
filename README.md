> **⚠️ Proprietary — All Rights Reserved.** © 2026 Sandeep Grover. This repository is licensed to Sandeep Grover and may **not** be used, run, copied, modified, distributed, or used to train models without prior written permission. Public visibility does not grant a license. See [LICENSE](LICENSE).

---

# Unequal enrollment across sites in a multisite trial

What unbalanced site sizes actually do to a mixed-effects analysis, and what they do not.

A mixed-effects model does **not** assume equal numbers of participants per site. Likelihood-based
estimation uses each site's actual contribution and there is no balanced-design requirement anywhere
in it. That part of the usual worry is unfounded.

Unequal enrollment does, however, change four things that analysis plans routinely miss. This
repository quantifies three of them by simulation rather than by assertion.

```
python sim_unequal_clusters.py      # writes simulation_results.json
```

Seed `20260720`, fixed. numpy + statsmodels only.

## The enrollment pattern used

8 sites, 245 participants, sizes `[62, 48, 40, 31, 25, 18, 12, 9]`.
Mean site size 30.62, coefficient of variation **0.602**, ICC 0.05.
The largest site is 6.9x the smallest.

## S1. The design effect that ignores variability in site size

The common form uses only the mean site size. The Eldridge et al. (2006) form adds the CV.

| Formula | Design effect |
|---|---|
| `1 + (m - 1) * ICC` (assumes equal sites) | 2.4813 |
| `1 + (m(1 + CV^2) - 1) * ICC` (actual) | 3.0363 |

The equal-size formula understates the required variance inflation by
**22.4%**. A study powered for 497 analysable
participants needs about **608** to hold the same power.

Eldridge et al. give the decision rule directly: below a CV of 0.23 the adjustment is negligible,
above it most trials should account for variable cluster size. This enrollment pattern sits at
CV = 0.602, comfortably above that threshold.

## S2. Unequal sites plus a site-varying effect equals anti-conservative inference

Data generated under a true null with a genuine site-by-treatment interaction
(SD of the site-specific effect = 0.3), then analysed three ways.
400 replicates, nominal alpha 0.05.

| Specification | Empirical type-I error |
|---|---|
| Random intercept only, z reference | **0.185** |
| Random slope for treatment, z reference | 0.062 |
| Random slope, t on k-2 df | **0.020** |

Omitting the site-level random slope for treatment inflates the false positive rate to
18.5%, more than three times nominal. Restoring the slope brings it
to 6.2%, which is the single most important fix.

A fixed t reference on k-2 df overshoots to 2.0%: conservative
rather than correct. A crude df rule trades one calibration error for another, which is why
Kenward-Roger, estimating the denominator df from the fitted covariance rather than a fixed count, is
preferable to any rule of thumb. The number of *sites*, not the number of participants, is what makes
a small-sample correction necessary at all.

## S3. Informative cluster size changes the estimand

When site size correlates with the site-specific effect (r = 0.85 here),
the precision-weighted mixed-model estimate and the unweighted site-average estimate answer different
questions.

| Estimator | Targets | Mean estimate |
|---|---|---|
| Mixed model, precision weighted | Participant-average effect | 0.3768 |
| Unweighted mean of site differences | Site-average effect | 0.3102 |

Mean absolute divergence on the same dataset: **0.0761** SD.
They differ by more than 0.05 SD in 63.6% of replicates.
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
