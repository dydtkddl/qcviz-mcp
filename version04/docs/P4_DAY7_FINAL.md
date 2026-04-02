# Phase 4 Day 7 Final (v04)

Day 7 is validation-only.  
No production code changes are required; the goal is full regression and final readiness checks across Phase 1-4.

## Deliverables

1. `verify_regression_all.py` at repository root  
   Full strict regression script (no skip mode) that validates:
   - Phase 1 conversation context behavior
   - Phase 2 modification lane parsing + RDKit candidate generation + sanitization
   - Phase 3 comparison delta + explanation + sanitization
   - Phase 4 integration (imports, flags, observability, timeout profiles, advisor context propagation)
   - Basic micro-benchmark checks

2. `docs/P4_DAY7_FINALverify_regression_all.py`  
   Docs wrapper that launches the root script.

## Run Command (WSL)

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04
PYTHONPATH=src \
  QCVIZ_CONTEXT_TRACKING_ENABLED=true \
  QCVIZ_MODIFICATION_LANE_ENABLED=true \
  QCVIZ_COMPARISON_ENABLED=true \
  python verify_regression_all.py
```

Or run from docs wrapper:

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04
PYTHONPATH=src \
  QCVIZ_CONTEXT_TRACKING_ENABLED=true \
  QCVIZ_MODIFICATION_LANE_ENABLED=true \
  QCVIZ_COMPARISON_ENABLED=true \
  python docs/P4_DAY7_FINALverify_regression_all.py
```

## Expected Output Shape

- Phase headers for `PHASE 1` through `PHASE 4` and `PERFORMANCE`
- Line-by-line `[PASS]` / `[FAIL]` checks
- Final summary:
  - `RESULT: X passed / Y failed / Z total checks`
  - `STATUS: FULL REGRESSION PASSED` when `Y == 0`

## Feature Flags

```ini
QCVIZ_CONTEXT_TRACKING_ENABLED=true
QCVIZ_MODIFICATION_LANE_ENABLED=true
QCVIZ_COMPARISON_ENABLED=true
```

## Notes

- Day 7 intentionally performs strict validation and does not silently skip optional checks.
- If RDKit or required modules are missing, the script reports explicit failures.

