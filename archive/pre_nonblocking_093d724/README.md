# Historical pipeline snapshot

Frozen from commit `093d724cc25fc319725bf347fc4d8ab196aadaf3` before the non-blocking R refactor.

- `pipeline.tar.gz`: exact historical scripts, reproducibility tools, configuration, Python modules and workflows (`git archive`). Extract into a separate checkout to inspect; source data remain in Git at the commit above.
- `R/run_mcda.R`: previous R entrypoint, retained verbatim.

Historical audit scripts still referenced by provenance checks, workflows or tests remain callable at their original paths. They are compatibility/reproduction entrypoints, not the new ranking entrypoint. Moving them indiscriminately would break historical reconstruction. New ranking uses `scripts/run_mcda_pipeline.py` and the canonical stage exports.
