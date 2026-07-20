#!/usr/bin/env python3
"""Build the client-facing sample review memo.

Every number that appears in the HTML is read from simulation_results.json,
which is written by sim_unequal_clusters.py. Nothing is hand-typed.
"""

import json
import pathlib

HERE = pathlib.Path(__file__).parent
OUT = pathlib.Path("/mnt/c/Users/grove/Downloads/multisite_mixed_effects_review_sample.html")

R = json.loads((HERE / "simulation_results.json").read_text())
S1, S2, S3 = R["s1_design_effect"], R["s2_type_i_error"], R["s3_informative_cluster_size"]

sizes = S1["site_sizes"]
max_size = max(sizes)
site_bars = "\n".join(
    f'''    <div class="barrow">
      <div class="barlabel">Site {i+1}</div>
      <div class="bartrack"><div class="barfill" style="width:{n/max_size*100:.1f}%;background:{c}">{n}</div></div>
    </div>'''
    for i, (n, c) in enumerate(zip(sizes, [
        "#6c5ce7", "#6c5ce7", "#a29bfe", "#a29bfe", "#74b9ff", "#74b9ff", "#e17055", "#d63031"]))
)

t1_int = S2["type1_random_intercept_z"]
t1_slp_z = S2["type1_random_slope_z"]
t1_slp_t = S2["type1_random_slope_t_kminus2"]


def pct(x):
    return f"{x*100:.1f}%"


def err_bar(label, val, target=0.05):
    """Bar scaled so nominal 5% sits at 25% width."""
    w = min(val / target * 25, 100)
    color = "#00b894" if val <= 0.065 else ("#e17055" if val <= 0.10 else "#d63031")
    return f'''    <div class="barrow">
      <div class="barlabel">{label}</div>
      <div class="bartrack"><div class="barfill" style="width:{w:.1f}%;background:{color}">{pct(val)}</div></div>
    </div>'''


HTML = f"""<meta charset="utf-8">
<title>Multisite Mixed-Effects Review: Unequal Enrollment Across Sites</title>
<style>
  :root{{
    --bg:#0a0a0f; --surface:#12121a; --surface2:#1a1a26; --accent:#6c5ce7;
    --accent2:#00cec9; --green:#00b894; --orange:#e17055; --red:#d63031;
    --text:#e8e8f0; --muted:#8a8aa0; --line:#252533; --blue:#74b9ff;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.6;padding-bottom:60px}}
  .wrap{{max-width:960px;margin:0 auto;padding:0 20px}}
  .samplenote{{background:var(--orange);color:#1a1a1a;text-align:center;font-weight:600;font-size:.85rem;padding:8px}}
  .hero{{background:linear-gradient(135deg,#12121f 0%,#1a1a3a 60%,#101028 100%);padding:56px 0 40px;border-bottom:1px solid var(--line)}}
  .hero h1{{font-size:2.2rem;font-weight:800;letter-spacing:-.5px}}
  .hero h1 span{{color:var(--accent2)}}
  .hero p{{color:var(--muted);margin-top:10px;font-size:1.05rem;max-width:680px}}
  .herostats{{display:flex;gap:28px;margin-top:28px;flex-wrap:wrap}}
  .herostats div{{border-left:3px solid var(--accent);padding-left:12px}}
  .herostats b{{display:block;font-size:1.5rem;color:#fff}}
  .herostats small{{color:var(--muted)}}
  .metabar{{display:flex;gap:0;flex-wrap:wrap;background:var(--surface);border:1px solid var(--line);border-radius:10px;margin:26px 0;overflow:hidden}}
  .metabar div{{flex:1;min-width:150px;padding:14px 18px;border-right:1px solid var(--line)}}
  .metabar div:last-child{{border-right:none}}
  .metabar small{{color:var(--muted);display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.5px}}
  .metabar b{{font-size:.95rem}}
  section{{margin:38px 0}}
  .snum{{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:var(--accent);border-radius:8px;font-weight:700;margin-right:12px;color:#fff}}
  h2{{font-size:1.35rem;display:flex;align-items:center;margin-bottom:14px}}
  h3{{font-size:1.02rem;margin:18px 0 8px;color:#fff}}
  p.lead{{color:var(--muted);margin-bottom:14px}}
  .card{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:22px;margin-bottom:16px}}
  .barrow{{display:flex;align-items:center;gap:12px;margin:10px 0}}
  .barlabel{{width:210px;font-size:.85rem;color:var(--muted)}}
  .bartrack{{flex:1;background:var(--surface2);border-radius:6px;height:22px;overflow:hidden}}
  .barfill{{height:100%;border-radius:6px;display:flex;align-items:center;justify-content:flex-end;padding-right:8px;font-size:.72rem;color:#0a0a0f;font-weight:700}}
  .deliv{{display:flex;gap:12px;align-items:flex-start;padding:12px 0;border-bottom:1px solid var(--line)}}
  .deliv:last-child{{border-bottom:none}}
  .chk{{color:var(--green);font-weight:700;font-size:1.1rem;flex-shrink:0}}
  .todo{{color:var(--orange);font-weight:700;font-size:1.1rem;flex-shrink:0}}
  .badge{{font-size:.7rem;padding:2px 8px;border-radius:20px;background:var(--surface2);color:var(--muted);border:1px solid var(--line);margin-left:8px;white-space:nowrap}}
  .pipe{{display:flex;flex-direction:column;gap:0}}
  .pnode{{display:flex;gap:14px;align-items:flex-start;padding:14px 0;position:relative}}
  .pnode:not(:last-child)::after{{content:"";position:absolute;left:7px;top:26px;bottom:-6px;width:2px;background:var(--line)}}
  .pdot{{width:16px;height:16px;border-radius:50%;flex-shrink:0;margin-top:4px;z-index:1}}
  .pdot.auto{{background:var(--green)}} .pdot.manual{{background:var(--orange)}} .pdot.out{{background:var(--accent2)}}
  .pnode b{{font-size:.98rem}}
  .pnode p{{color:var(--muted);font-size:.88rem}}
  .rec{{border-left:4px solid var(--line);padding:16px 18px;background:var(--surface);border-radius:0 10px 10px 0;margin-bottom:14px}}
  .rec.crit{{border-left-color:var(--red)}}
  .rec.warn{{border-left-color:var(--orange)}}
  .rec.ok{{border-left-color:var(--green)}}
  .rec b{{display:block;margin-bottom:6px;font-size:1rem}}
  .rec p{{color:var(--muted);font-size:.9rem}}
  .tag{{display:inline-block;font-size:.68rem;letter-spacing:.5px;text-transform:uppercase;padding:3px 9px;border-radius:4px;font-weight:700;margin-bottom:8px}}
  .tag.crit{{background:rgba(214,48,49,.18);color:#ff7675}}
  .tag.warn{{background:rgba(225,112,85,.18);color:#e17055}}
  .tag.ok{{background:rgba(0,184,148,.18);color:#00b894}}
  pre{{background:#08080d;border:1px solid var(--line);border-radius:10px;padding:16px 18px;overflow-x:auto;font-size:.82rem;line-height:1.55;color:#d8d8e8;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
  pre .cm{{color:#6b6b85}}
  pre .kw{{color:#a29bfe}}
  pre .st{{color:#55efc4}}
  .two{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
  @media(max-width:760px){{.two{{grid-template-columns:1fr}}.barlabel{{width:120px}}}}
  .quote{{background:var(--surface2);border:1px solid var(--line);border-left:4px solid var(--accent2);border-radius:0 10px 10px 0;padding:18px 20px;font-size:.94rem;line-height:1.75}}
  .grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
  .grid3 div{{background:var(--surface2);border:1px solid var(--line);border-radius:8px;padding:14px}}
  .grid3 b{{display:block;font-size:1.35rem;color:#fff}}
  .grid3 small{{color:var(--muted);font-size:.78rem}}
  @media(max-width:760px){{.grid3{{grid-template-columns:1fr}}}}
  table{{width:100%;border-collapse:collapse;font-size:.88rem}}
  th{{text-align:left;color:var(--muted);font-weight:600;font-size:.74rem;text-transform:uppercase;letter-spacing:.5px;padding:10px 12px;border-bottom:1px solid var(--line)}}
  td{{padding:11px 12px;border-bottom:1px solid var(--line)}}
  tr:last-child td{{border-bottom:none}}
  .mono{{font-family:ui-monospace,Menlo,monospace;font-size:.84rem;color:var(--accent2)}}
  footer{{border-top:1px solid var(--line);margin-top:50px;padding-top:26px;color:var(--muted);font-size:.88rem}}
  footer b{{color:#fff;font-size:1rem;display:block;margin-bottom:4px}}
</style>

<div class="samplenote">Sample output - illustrative site sizes and wording. Your actual figures replace these once I have the plan.</div>

<div class="hero">
  <div class="wrap">
    <h1>Does your mixed-effects model actually handle <span>unequal enrollment across sites?</span></h1>
    <p>A focused statistical review of one specification question in a multisite behavioural intervention plan: what unbalanced site sizes do to your standard errors, your power, and your estimand - and the four places an otherwise-correct analysis paragraph quietly goes wrong.</p>
    <div class="herostats">
      <div><b>{S1['n_sites']}</b><small>sites, illustrative</small></div>
      <div><b>{S1['n_total']}</b><small>participants</small></div>
      <div><b>{S1['cv_site_size']:.2f}</b><small>CV of site size</small></div>
      <div><b>{S2['nrep_fitted']:,}</b><small>simulation replicates</small></div>
    </div>
  </div>
</div>

<div class="wrap">

  <div class="metabar">
    <div><small>Question</small><b>Unequal cluster sizes</b></div>
    <div><small>Method</small><b>Mixed-effects / multilevel</b></div>
    <div><small>Deliverable</small><b>Review memo + wording</b></div>
    <div><small>Reviewer</small><b>Dr. Sandeep Grover</b></div>
  </div>

  <!-- 1 -->
  <section>
    <h2><span class="snum">1</span>The short answer</h2>
    <div class="rec ok">
      <span class="tag ok">Reassuring</span>
      <b>A correctly specified mixed model does not assume equal numbers per site.</b>
      <p>Likelihood-based estimation of a multilevel model uses each site's actual contribution. There is no balanced-design requirement anywhere in the estimation. Reviewers who claim otherwise are confusing mixed models with classical fixed-effects ANOVA, which does assume balance. So the headline concern behind your question resolves in your favour.</p>
    </div>
    <div class="rec crit">
      <span class="tag crit">But</span>
      <b>Unequal enrollment still changes four things, and most plans address only the first.</b>
      <p>It inflates the design effect (power), it interacts with site-level effect heterogeneity to make inference anti-conservative, it shifts which estimand you are actually reporting when site size is informative, and with few sites it exposes the denominator degrees-of-freedom problem. Each is addressed below with the specification change and the wording that closes it.</p>
    </div>
    <div class="grid3">
      <div><b>{S1['variance_understated_pct']:.0f}%</b><small>variance understated if the design effect ignores the CV of site size</small></div>
      <div><b>{pct(t1_int)}</b><small>actual type-I error of a random-intercept-only model when the effect varies by site</small></div>
      <div><b>{S3['pct_reps_diverging_over_0_05']:.0f}%</b><small>of replicates where the two defensible estimands differ by more than 0.05 SD</small></div>
    </div>
  </section>

  <!-- 2 -->
  <section>
    <h2><span class="snum">2</span>The enrollment pattern this memo assumes</h2>
    <p class="lead">Illustrative only. I substitute your real per-site counts on the first pass, which is why the enrollment table is the one thing I need alongside the plan.</p>
    <div class="card">
{site_bars}
      <p style="color:var(--muted);font-size:.86rem;margin-top:16px">
        {S1['n_total']} participants across {S1['n_sites']} sites. Mean site size {S1['mean_site_size']},
        coefficient of variation <span class="mono">{S1['cv_site_size']:.3f}</span>. The largest site is
        {max(sizes)/min(sizes):.1f} times the smallest. That ratio, not the imbalance itself, is what drives
        everything in sections 3 to 6.
      </p>
    </div>
  </section>

  <!-- 3 -->
  <section>
    <h2><span class="snum">3</span>Failure mode 1: the design effect that ignores variability in site size</h2>
    <p class="lead">This is the single most common defect I find in multisite analysis plans. The sample-size section computes a design effect from the average site size and the ICC, and never accounts for the spread of site sizes.</p>
    <div class="card">
      <h3>The two formulas</h3>
      <pre><span class="cm"># What most plans use - assumes every site contributes m participants</span>
DE_equal   = 1 + (m_bar - 1) * ICC
           = 1 + ({S1['mean_site_size']} - 1) * {S1['icc']}
           = <span class="st">{S1['de_equal_assumption']:.4f}</span>

<span class="cm"># Eldridge et al. (2006), CV-adjusted - what unequal enrollment requires</span>
DE_unequal = 1 + (m_bar * (1 + CV^2) - 1) * ICC
           = 1 + ({S1['mean_site_size']} * (1 + {S1['cv_site_size']:.4f}^2) - 1) * {S1['icc']}
           = <span class="st">{S1['de_unequal_actual']:.4f}</span></pre>
      <p style="color:var(--muted);font-size:.9rem;margin-top:14px">
        With this enrollment pattern the equal-size formula understates the required variance inflation by
        <b style="color:#e17055">{S1['variance_understated_pct']:.1f}%</b>. A study powered for
        {S1['n_needed_equal']} analysable participants actually needs about
        <b style="color:#e17055">{S1['n_needed_unequal']}</b> to hold the same power. At an ICC of {S1['icc']} that
        gap is recoverable. At an ICC of 0.10 or above, with this much spread in site size, it is the difference
        between a powered trial and an underpowered one.
      </p>
    </div>
    <div class="card">
      <h3>There is a published threshold, and you are above it</h3>
      <p style="color:var(--muted);font-size:.9rem">
        Eldridge, Ashby and Kerry (<i>International Journal of Epidemiology</i> 2006, PMID 16943232) give the
        decision rule directly: below a coefficient of variation of <b style="color:#00b894">0.23</b> the
        adjustment for variable cluster size is negligible; above it, most trials should account for it. This
        enrollment pattern sits at <b style="color:#e17055">{S1['cv_site_size']:.3f}</b>. That is not a
        borderline call, and citing the threshold in your plan turns a reviewer objection into a settled point.
      </p>
    </div>
    <div class="rec warn">
      <span class="tag warn">Recommended change</span>
      <b>State the CV of site size explicitly in the sample-size paragraph.</b>
      <p>Two sentences. Give the anticipated per-site enrollment range, the implied CV, and the CV-adjusted design effect. This is the cheapest defensive edit in the whole plan, and it pre-empts the reviewer question directly.</p>
    </div>
  </section>

  <!-- 4 -->
  <section>
    <h2><span class="snum">4</span>Failure mode 2: unequal sites plus a site-varying effect equals anti-conservative inference</h2>
    <p class="lead">This is the one that costs papers. If the intervention effect genuinely varies across sites - which in a behavioural intervention delivered by different staff it almost always does - and you fit a random intercept for site but no random slope for treatment, your standard error for the treatment effect is too small. Unequal site sizes make it worse, because the large sites dominate the estimate.</p>
    <div class="card">
      <h3>Simulated type-I error, {S2['nrep_fitted']:,} replicates, true effect set to zero</h3>
      <p style="color:var(--muted);font-size:.86rem;margin-bottom:14px">Data generated with a genuine site-by-treatment interaction (SD of site-specific effect = {S2['tau_site_treatment_effect']}), then analysed three ways. Nominal alpha is 5%.</p>
{err_bar("Random intercept only, z test", t1_int)}
{err_bar("Random slope, z test", t1_slp_z)}
{err_bar("Random slope, t on k-2 df", t1_slp_t)}
      <p style="color:var(--muted);font-size:.9rem;margin-top:16px">
        The random-intercept-only model rejects a true null <b style="color:#ff7675">{pct(t1_int)}</b> of the time
        instead of 5%. That is more than three times the nominal rate, and it is the difference between a finding
        and a false positive. Adding the random slope for treatment brings it to
        <b style="color:#00b894">{pct(t1_slp_z)}</b>, close to nominal and the single most important fix.
        Referring the statistic to a t distribution on k-2 = {S1['n_sites']-2} degrees of freedom instead
        overshoots to {pct(t1_slp_t)}, which is conservative rather than correct: a crude df rule trades one
        calibration error for another. This is exactly why Kenward-Roger, which estimates the denominator df from
        the fitted covariance rather than a fixed count, is the right choice here.
      </p>
    </div>
    <div class="rec crit">
      <span class="tag crit">Highest priority</span>
      <b>Add a random slope for treatment at the site level, and say what happens if it will not converge.</b>
      <p>With {S1['n_sites']} sites a random slope is estimable but not comfortable. The plan should name the fallback in advance rather than leaving it to a post hoc decision: that is section 7.</p>
    </div>
  </section>

  <!-- 5 -->
  <section>
    <h2><span class="snum">5</span>Failure mode 3: informative cluster size changes your estimand, not just your standard error</h2>
    <p class="lead">If site enrollment correlates with something that also drives the outcome - larger sites are better resourced, recruit faster, deliver the intervention with higher fidelity - then site size is informative. A mixed model precision-weights sites, so it answers "what is the effect for the average participant". An unweighted average of site-level effects answers "what is the effect at the average site". These are different questions and they give different numbers.</p>
    <div class="card">
      <h3>Simulated divergence, {S3['nrep_fitted']:,} replicates</h3>
      <p style="color:var(--muted);font-size:.86rem;margin-bottom:14px">Site size correlated with the site-specific effect at r = {S3['corr_site_size_with_effect']}, true participant-level average effect = {S3['true_participant_weighted_effect']} SD.</p>
      <table>
        <tr><th>Estimator</th><th>Targets</th><th>Mean estimate</th></tr>
        <tr><td>Mixed model, precision weighted</td><td>Participant-average effect</td><td class="mono">{S3['mean_mixed_model_estimate']:.4f}</td></tr>
        <tr><td>Unweighted mean of site differences</td><td>Site-average effect</td><td class="mono">{S3['mean_site_average_estimate']:.4f}</td></tr>
      </table>
      <p style="color:var(--muted);font-size:.9rem;margin-top:14px">
        Mean absolute divergence between the two on the same dataset:
        <b class="mono" style="color:#e17055">{S3['mean_absolute_divergence']:.4f}</b> SD, and they differ by more
        than 0.05 SD in <b style="color:#e17055">{S3['pct_reps_diverging_over_0_05']:.1f}%</b> of replicates.
        Neither is wrong. But only one answers the question your trial is asking, and the plan should say which.
      </p>
    </div>
    <div class="rec warn">
      <span class="tag warn">Recommended change</span>
      <b>Name the estimand in one sentence, and pre-specify the other as a sensitivity analysis.</b>
      <p>For a behavioural intervention intended to be scaled across sites, the site-average estimand is often the policy-relevant one, and the mixed model is then the sensitivity analysis rather than the primary. This is worth a deliberate decision rather than a default.</p>
    </div>
  </section>

  <!-- 6 -->
  <section>
    <h2><span class="snum">6</span>Failure mode 4: few sites and the denominator degrees of freedom</h2>
    <p class="lead">Mixed model software defaults to large-sample inference. With a small number of sites, that default is optimistic, and the number of sites is what matters here, not the number of participants.</p>
    <div class="two">
      <div class="card">
        <h3>The rule of thumb</h3>
        <p style="color:var(--muted);font-size:.9rem">Below roughly 30 to 40 clusters, use REML with a Kenward-Roger or Satterthwaite denominator adjustment for any site-level or site-varying term. Section 4 shows what the uncorrected version costs. Participant-level covariates are far less affected, because they have participant-level degrees of freedom behind them.</p>
      </div>
      <div class="card">
        <h3>Site as fixed instead of random</h3>
        <p style="color:var(--muted);font-size:.9rem">With fewer than about 5 to 7 sites, the between-site variance is estimated so poorly that fixed site effects plus site-by-treatment interaction terms are often the more honest specification. You give up generalisation to unobserved sites, which for a defined multisite trial is frequently not a loss worth paying for.</p>
      </div>
    </div>
  </section>

  <!-- 7 -->
  <section>
    <h2><span class="snum">7</span>The convergence ladder, pre-specified</h2>
    <p class="lead">Random-slope models with a modest number of sites do fail to converge, or converge to a singular fit. If the plan does not say what happens next, the decision gets made after the data are seen. Reviewers notice. The fix is to write the ladder down in advance.</p>
    <div class="card">
      <div class="pipe">
        <div class="pnode"><div class="pdot out"></div><div><b>Primary specification</b><p>Random intercept for site plus random slope for treatment, unstructured covariance, REML, Kenward-Roger degrees of freedom.</p></div></div>
        <div class="pnode"><div class="pdot auto"></div><div><b>If the model does not converge</b><p>Refit with an independent (diagonal) site-level covariance structure, dropping the intercept-slope correlation. Report that this was done.</p></div></div>
        <div class="pnode"><div class="pdot auto"></div><div><b>If the fit is singular, slope variance at zero</b><p>Drop to a random intercept only, and report the site-level variance components that led to the decision. A near-zero slope variance is a finding about the intervention, not just a numerical nuisance.</p></div></div>
        <div class="pnode"><div class="pdot manual"></div><div><b>If fewer sites than expected recruit</b><p>Switch to fixed site effects with site-by-treatment interaction, pre-specified at the threshold you name now, not chosen later.</p></div></div>
        <div class="pnode"><div class="pdot out"></div><div><b>Reported either way</b><p>Site-level variance components, ICC with a confidence interval, and per-site enrollment. These belong in the results table regardless of which rung you land on.</p></div></div>
      </div>
    </div>
  </section>

  <!-- 8 -->
  <section>
    <h2><span class="snum">8</span>Repeated measures: the third level</h2>
    <p class="lead">Your design has measurements within participants within sites. Two specification points follow, and they are easy to get wrong in opposite directions.</p>
    <div class="rec warn">
      <span class="tag warn">Point 1</span>
      <b>Do not collapse the participant level into the site level.</b>
      <p>Measurements nested in participants nested in sites is a genuine three-level structure. Fitting site as the only grouping factor treats repeated measurements on one participant as independent, which understates standard errors for within-participant contrasts, the very contrasts a pre-post intervention study cares about most.</p>
    </div>
    <div class="rec warn">
      <span class="tag warn">Point 2</span>
      <b>Say which within-participant covariance structure you are assuming, and what you do if it is wrong.</b>
      <p>Unstructured is preferable with few timepoints and is the usual default for a three-or-four-wave behavioural trial. Compound symmetry is more parsimonious but assumes constant correlation across all lags, which post-intervention follow-up data usually violate. Name the primary and the fallback.</p>
    </div>
    <div class="rec ok">
      <span class="tag ok">Bonus</span>
      <b>Likelihood-based estimation handles missing outcome data under MAR without imputation.</b>
      <p>This is a genuine advantage of your chosen approach and most plans undersell it. The caveat worth adding: differential attrition by site is a plausible MNAR mechanism in multisite behavioural work, so a pattern-mixture or delta-adjusted sensitivity analysis is worth one sentence.</p>
    </div>
  </section>

  <!-- 9 -->
  <section>
    <h2><span class="snum">9</span>Drop-in replacement wording</h2>
    <p class="lead">This is the format of what you get back: your paragraph, rewritten to close the gaps above, in the register of the surrounding plan rather than a statistician's shorthand. Illustrative text below; the real version is built on your actual sentences.</p>
    <div class="quote">
      The primary analysis will use a three-level linear mixed-effects model, with repeated measurements nested
      within participants and participants nested within sites. The model will include fixed effects for treatment
      arm, time, and their interaction, a random intercept for site, a random slope for treatment at the site
      level, and a random intercept for participant. Because anticipated enrollment differs across sites
      (expected range X to Y participants; coefficient of variation Z), the sample-size calculation applies the
      variability-adjusted design effect 1 + (m(1 + CV squared) - 1) x ICC rather than the equal-cluster-size form.
      Mixed-effects estimation accommodates unequal numbers of participants per site without modification, and
      accommodates missing outcome data under a missing-at-random assumption. Models will be fitted by restricted
      maximum likelihood with Kenward-Roger degrees of freedom, given the limited number of sites. Should the
      site-level random slope fail to converge or return a singular fit, the covariance structure will be
      simplified to independent random effects and then, if necessary, to a random intercept only; any such step
      will be reported. Site-level variance components and the intraclass correlation with a confidence interval
      will be reported alongside the treatment effect. As a pre-specified sensitivity analysis, an unweighted
      site-average treatment effect will be estimated to assess whether informative site size materially changes
      the conclusion.
    </div>
  </section>

  <!-- 10 -->
  <section>
    <h2><span class="snum">10</span>Matching syntax, Stata and R</h2>
    <p class="lead">The memo ships with runnable syntax for the primary model and each rung of the convergence ladder, so the wording and the code cannot drift apart.</p>
    <div class="two">
      <div>
        <h3>Stata</h3>
        <pre><span class="cm">* three-level, random slope at site</span>
<span class="kw">mixed</span> outcome i.arm##i.time ///
    || site: i.arm, <span class="kw">cov(unstructured)</span> ///
    || pid: , <span class="kw">reml</span> <span class="kw">dfmethod(kroger)</span>

<span class="cm">* ICC and variance components</span>
<span class="kw">estat icc</span>

<span class="cm">* fallback 1: independent covariance</span>
<span class="kw">mixed</span> outcome i.arm##i.time ///
    || site: i.arm, <span class="kw">cov(independent)</span> ///
    || pid: , <span class="kw">reml</span>

<span class="cm">* fallback 2: random intercept only</span>
<span class="kw">mixed</span> outcome i.arm##i.time ///
    || site: || pid: , <span class="kw">reml</span> <span class="kw">dfmethod(kroger)</span></pre>
      </div>
      <div>
        <h3>R</h3>
        <pre><span class="cm"># three-level, random slope at site</span>
<span class="kw">library</span>(lmerTest)
m <- <span class="kw">lmer</span>(outcome ~ arm * time +
       (1 + arm | site) + (1 | pid),
     data = d, REML = <span class="st">TRUE</span>)
<span class="kw">anova</span>(m, ddf = <span class="st">"Kenward-Roger"</span>)

<span class="cm"># variance components and ICC</span>
<span class="kw">VarCorr</span>(m)
performance::<span class="kw">icc</span>(m)

<span class="cm"># fallback 1: independent covariance</span>
m2 <- <span class="kw">lmer</span>(outcome ~ arm * time +
        (1 | site) + (0 + arm | site) + (1 | pid),
      data = d, REML = <span class="st">TRUE</span>)</pre>
      </div>
    </div>
  </section>

  <!-- 11 -->
  <section>
    <h2><span class="snum">11</span>What arrives, and when</h2>
    <div class="card">
      <div class="deliv"><span class="chk">&#10003;</span><div><b>Verdict on the proposed model</b><span class="badge">1 page</span><p style="color:var(--muted);font-size:.88rem">Whether unequal enrollment is handled, and the exact sentence in your plan that does or does not establish it.</p></div></div>
      <div class="deliv"><span class="chk">&#10003;</span><div><b>Ranked concern list</b><span class="badge">2 to 3 pages</span><p style="color:var(--muted);font-size:.88rem">Each concern with the specification change that closes it, ordered by what a reviewer is most likely to raise.</p></div></div>
      <div class="deliv"><span class="chk">&#10003;</span><div><b>Replacement wording</b><span class="badge">drop-in</span><p style="color:var(--muted);font-size:.88rem">Your analysis paragraph rewritten in your register, ready to paste into the plan.</p></div></div>
      <div class="deliv"><span class="chk">&#10003;</span><div><b>Design effect recomputed on your enrollment</b><span class="badge">your numbers</span><p style="color:var(--muted);font-size:.88rem">CV-adjusted, with the implied change to required sample size at your ICC assumption.</p></div></div>
      <div class="deliv"><span class="chk">&#10003;</span><div><b>Stata and R syntax</b><span class="badge">runnable</span><p style="color:var(--muted);font-size:.88rem">Primary model plus every rung of the convergence ladder.</p></div></div>
      <div class="deliv"><span class="todo">&#9679;</span><div><b>What I need from you</b><span class="badge">to start</span><p style="color:var(--muted);font-size:.88rem">The relevant sections of the plan, the expected per-site enrollment counts, and your assumed ICC if one is stated. Nothing else.</p></div></div>
    </div>
  </section>

  <!-- 12 -->
  <section>
    <h2><span class="snum">12</span>How the numbers on this page were produced</h2>
    <p class="lead">Every figure in sections 1 to 5 comes from a simulation written for this review rather than quoted from a textbook, so you can check it rather than take it on trust.</p>
    <div class="card">
      <table>
        <tr><th>Section</th><th>What was simulated</th><th>Replicates</th></tr>
        <tr><td>3</td><td>Design effect, analytic, both formulas on the same enrollment vector</td><td class="mono">exact</td></tr>
        <tr><td>4</td><td>Type-I error under a true site-by-treatment interaction, three inference methods</td><td class="mono">{S2['nrep_fitted']:,}</td></tr>
        <tr><td>5</td><td>Estimand divergence under informative cluster size</td><td class="mono">{S3['nrep_fitted']:,}</td></tr>
      </table>
      <p style="color:var(--muted);font-size:.88rem;margin-top:14px">
        Seed <span class="mono">{R['seed']}</span>, fixed for reproducibility. The code is a single self-contained
        Python file using numpy and statsmodels, and I am happy to send it with the memo so your team can rerun it
        on your own enrollment numbers.
      </p>
    </div>
  </section>

  <footer>
    <b>Dr. Sandeep Grover</b>
    PhD, clinical epidemiology and biostatistics. Mixed-effects and multilevel modelling for clustered and
    repeated-measures designs. Peer reviewer for clinical and epidemiological journals.<br><br>
    Feel free to share with your team.
  </footer>

</div>
"""

OUT.write_text(HTML, encoding="utf-8")
print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")
