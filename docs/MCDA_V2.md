# Scenario-specific R MCDA (2026-11-02)

Decision: retain C1 identity, REE role, activity/window, JORC and verified GIS requirements; make PANEL specific to a fixed analysis scenario. Legacy G0 and strict panels retain their existing definitions for historical reconstruction. No source approval, Project ID or research window is altered.

| New panel | Fixed criteria | Interpretation |
|---|---|---|
| CORE_BASELINE_V2 | T1, D1, I1–I4 | Technical maturity, development and infrastructure conditions |
| RESOURCE_EXTENDED_V2 | Core + R1 | Resource-enhanced conditions |
| STRATEGIC_EXTENDED_V2 | Core + S1 | Composition-enhanced conditions |
| FULL_PANEL_V2 | Existing 12 criteria | Six-domain complete-case analysis |

Core is a deliberately reduced, versioned analysis, not a six-domain development potential score. Coverage and selection bias must be reported before substantive interpretation. Commercial/NORM observations remain in the database and full-panel analysis; missingness is never scored zero. Every alternative within one panel uses the same criteria and weights. Criteria are not chosen dynamically to improve ranks or sample size.

The new panels release verified complete cases independently. Another project's pending evidence or GIS does not block their export. At least two cases are needed to rank. Legacy frozen-19 GIS release remains unchanged. The existing evidence schema continues to store missing/conflicting observations and reasons.

Run from repository root:

```bash
python -m au_ree run --through r_export --offline
python scripts/run_mcda_pipeline.py --workspace work --out work/r_mcda/run-001
```

The supervisor also supports `python scripts/run_research_pipeline.py --profile mcda --mode check` for counts and `--mode write` for a timestamped ranking run. It consumes existing exports and never waits for unrelated Census completion.

Use a fresh output directory for each run. The runner writes one manifest, source/config/code hashes, candidate counts, panel definitions and per-panel status. Sparse panels skip independently. R failures are recorded and cause nonzero CLI exit. Existing stage exports provide project-level exclusions and criterion coverage; the runner checks point-ready membership.

R uses the existing PROMETHEE II (V-shape, IQR thresholds), SAW, TOPSIS, criterion deletion and threshold sensitivity algorithms. Monte Carlo samples scenario weights around the declared assumptions; zero weights remain zero. It evaluates weight uncertainty only, not measurement uncertainty. Ties are retained. Subset ranks must not be compared directly to full-cohort ranks. `CORE_ON_*` reruns use the same projects as each expanded panel to isolate criteria effects; thresholds are recalculated on each matched set, so report the actual threshold audit.

Configured weights remain explicitly illustrative assumptions, not researcher-elicited AHP. AHP can still be run directly with `R/run_mcda.R --ahp ...` after genuine pairwise judgments. No signed decisions or judgments are fabricated. The V2 runner does not promote assumed-weight results to publication-ready findings.

Historical code is archived under `archive/pre_nonblocking_093d724/`. Active audit compatibility paths remain to preserve existing workflows and reproducibility. No historical evidence or dataset is deleted.

## Validation at implementation

- Python suite: 287 passed (18 existing Shapely deprecation warnings).
- R 4.3.3: actual synthetic AHP/PROMETHEE II/SAW/TOPSIS/100-draw Monte Carlo executed twice; ranking and draw CSVs were byte-identical.
- Integrated synthetic canonical exports: core and resource panels completed, strategic/full panels independently skipped, matched-core rerun completed.
- Actual offline reconstruction: 203 historical master records, 220 observations, zero approved source documents in the canonical scoring registry, zero verified scoring values and zero point-ready V2 cases. This is a canonical evidence integration limitation; these counts do not describe the entire national Census or imply that the repository has no documentary evidence elsewhere. No research ranks were produced or fabricated.
