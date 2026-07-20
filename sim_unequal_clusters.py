"""
Unequal enrollment across sites in a multisite behavioural trial:
what actually breaks, and what does not.

Three deterministic simulations, each targeting one claim that commonly appears
(or is missing) in a multisite statistical analysis plan.

  S1  Design effect / power        - unequal cluster sizes inflate the variance
                                     inflation factor via the CV of site sizes.
  S2  Type-I error                 - a random-INTERCEPT-only model applied to data
                                     with a genuine site x treatment interaction
                                     gives anti-conservative inference; a random
                                     SLOPE model with a small-sample t reference
                                     distribution restores nominal alpha.
  S3  Estimand under informative   - when site size correlates with site-level
      cluster size                   effect, the precision-weighted (mixed model)
                                     estimate and the unweighted site-average
                                     estimate target different quantities.

Scope note: participants are modelled at the primary contrast (change from
baseline) rather than as an explicit 3-level repeated-measures structure. The
question under review is site-level clustering with unequal n; collapsing the
within-participant level to the primary contrast isolates that question without
changing the site-level conclusions.

Run:  python sim_unequal_clusters.py
"""

import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")

SEED = 20260720
NREP = 400
ALPHA = 0.05

# A realistic unequal multisite enrollment pattern: 8 sites, 245 participants.
SITE_N = np.array([62, 48, 40, 31, 25, 18, 12, 9])
ICC = 0.05


# --------------------------------------------------------------------------
# S1. Design effect with unequal cluster sizes
# --------------------------------------------------------------------------
def design_effects(site_n=SITE_N, icc=ICC):
    """Eldridge et al. (2006) CV-adjusted design effect vs the equal-size form."""
    m_bar = site_n.mean()
    cv = site_n.std(ddof=1) / m_bar

    de_equal = 1 + (m_bar - 1) * icc
    de_unequal = 1 + (m_bar * (1 + cv**2) - 1) * icc

    return {
        "n_sites": int(site_n.size),
        "n_total": int(site_n.sum()),
        "site_sizes": site_n.tolist(),
        "mean_site_size": round(float(m_bar), 2),
        "cv_site_size": round(float(cv), 4),
        "icc": icc,
        "de_equal_assumption": round(float(de_equal), 4),
        "de_unequal_actual": round(float(de_unequal), 4),
        "variance_understated_pct": round(
            float((de_unequal / de_equal - 1) * 100), 2
        ),
        # n required scales with the design effect
        "n_needed_equal": int(np.ceil(200 * de_equal)),
        "n_needed_unequal": int(np.ceil(200 * de_unequal)),
    }


# --------------------------------------------------------------------------
# shared data generator
# --------------------------------------------------------------------------
def make_trial(rng, site_n, icc, tau_effect, delta=0.0, size_effect_corr=0.0):
    """One multisite trial with 1:1 within-site randomisation.

    icc              between-site variance share of the intercept
    tau_effect       SD of the site-specific treatment effect (0 = homogeneous)
    delta            true average treatment effect
    size_effect_corr correlation between site size and that site's effect
                     (informative cluster size)
    """
    k = site_n.size
    sd_site = np.sqrt(icc)
    sd_resid = np.sqrt(1 - icc)

    site_int = rng.normal(0, sd_site, k)

    if size_effect_corr == 0.0:
        site_slope = rng.normal(0, tau_effect, k)
    else:
        z_size = (site_n - site_n.mean()) / site_n.std(ddof=1)
        noise = rng.normal(0, 1, k)
        latent = size_effect_corr * z_size + np.sqrt(
            max(1 - size_effect_corr**2, 0)
        ) * noise
        site_slope = tau_effect * latent

    rows = []
    for j, n_j in enumerate(site_n):
        trt = np.zeros(n_j)
        trt[: n_j // 2] = 1
        rng.shuffle(trt)
        y = (
            site_int[j]
            + (delta + site_slope[j]) * trt
            + rng.normal(0, sd_resid, n_j)
        )
        rows.append(pd.DataFrame({"site": j, "trt": trt, "y": y}))

    return pd.concat(rows, ignore_index=True)


def _fit(df, re_formula):
    m = smf.mixedlm("y ~ trt", df, groups=df["site"], re_formula=re_formula)
    return m.fit(reml=True)


# --------------------------------------------------------------------------
# S2. Type-I error: intercept-only vs slope + small-sample reference
# --------------------------------------------------------------------------
def type_i_error(site_n=SITE_N, icc=ICC, tau_effect=0.30, nrep=NREP):
    rng = np.random.default_rng(SEED)
    k = site_n.size
    rej_int_z = rej_slope_z = rej_slope_t = 0
    fitted = 0

    for _ in range(nrep):
        df = make_trial(rng, site_n, icc, tau_effect=tau_effect, delta=0.0)
        try:
            f_int = _fit(df, "1")
            f_slp = _fit(df, "1 + trt")
        except Exception:
            continue
        fitted += 1

        # naive normal reference, random intercept only
        if abs(f_int.params["trt"] / f_int.bse["trt"]) > stats.norm.ppf(1 - ALPHA / 2):
            rej_int_z += 1
        # random slope, still naive normal reference
        if abs(f_slp.params["trt"] / f_slp.bse["trt"]) > stats.norm.ppf(1 - ALPHA / 2):
            rej_slope_z += 1
        # random slope + t reference on k-2 df (between-within style correction)
        if abs(f_slp.params["trt"] / f_slp.bse["trt"]) > stats.t.ppf(
            1 - ALPHA / 2, k - 2
        ):
            rej_slope_t += 1

    return {
        "nrep_fitted": fitted,
        "tau_site_treatment_effect": tau_effect,
        "nominal_alpha": ALPHA,
        "type1_random_intercept_z": round(rej_int_z / fitted, 4),
        "type1_random_slope_z": round(rej_slope_z / fitted, 4),
        "type1_random_slope_t_kminus2": round(rej_slope_t / fitted, 4),
    }


# --------------------------------------------------------------------------
# S3. Informative cluster size: which estimand is being reported
# --------------------------------------------------------------------------
def informative_cluster_size(
    site_n=SITE_N, icc=ICC, tau_effect=0.35, delta=0.30, corr=0.85, nrep=250
):
    rng = np.random.default_rng(SEED + 1)
    mixed_est, siteavg_est = [], []

    for _ in range(nrep):
        df = make_trial(
            rng, site_n, icc, tau_effect=tau_effect, delta=delta,
            size_effect_corr=corr,
        )
        try:
            f = _fit(df, "1 + trt")
        except Exception:
            continue
        mixed_est.append(f.params["trt"])

        # unweighted mean of within-site differences = site-average estimand
        d = df.groupby(["site", "trt"])["y"].mean().unstack()
        siteavg_est.append(float((d[1.0] - d[0.0]).mean()))

    mixed_est = np.array(mixed_est)
    siteavg_est = np.array(siteavg_est)

    return {
        "nrep_fitted": int(mixed_est.size),
        "true_participant_weighted_effect": round(
            float(np.average([delta], weights=[1])), 4
        ),
        "corr_site_size_with_effect": corr,
        "mean_mixed_model_estimate": round(float(mixed_est.mean()), 4),
        "mean_site_average_estimate": round(float(siteavg_est.mean()), 4),
        "mean_absolute_divergence": round(
            float(np.mean(np.abs(mixed_est - siteavg_est))), 4
        ),
        "pct_reps_diverging_over_0_05": round(
            float(np.mean(np.abs(mixed_est - siteavg_est) > 0.05) * 100), 2
        ),
    }


if __name__ == "__main__":
    out = {
        "seed": SEED,
        "s1_design_effect": design_effects(),
        "s2_type_i_error": type_i_error(),
        "s3_informative_cluster_size": informative_cluster_size(),
    }
    print(json.dumps(out, indent=2))
    with open("simulation_results.json", "w") as fh:
        json.dump(out, fh, indent=2)
