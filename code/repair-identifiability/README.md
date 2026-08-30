# Repair Identifiability and Product-Measurement Complexity of Bond Failures in Graph States

Public verification snapshot for the August 2026 v10 freeze of the manuscript by Ayush Nadiger.

The paper studies a known graph state with a suspect intended bond and separates two questions: localizing which bond is faulty and identifying which physical repair action is required. Its central Pauli-support result is that a severed bond and full endpoint Z-dephasing can be distinguished by a Pauli observable exactly when that observable lies in the failed-graph stabilizer group but outside the target stabilizer group, `±S(G-e) \ ±S(G)`.

## What is public here

`repro/` contains the lightweight exact checks used during the freeze pass, the W8/W10 wheel obstruction checks, symbolic bounded-weight wheel checks, and source for the large W14 exact obstruction search. `ITERATION_AUDIT_v10.md` records the publication-readiness changes.

The manuscript's theorems do not depend on software. Results that use finite enumeration are explicitly labeled computer-assisted in the paper.

## Quick checks

From `repro/`:

```bash
python audit_single_edge.py
python audit_endpoint_tomography.py
python audit_compression_gap.py
python audit_w8_weighted_fast.py
python wheel_cert_check.py
python audit_wheel_weight3_symbolic_boundaries.py
python audit_kn_weight_profile.py
```

Python checks use the standard library plus `numpy` and/or `networkx` where indicated. The W14 exact search sources require C++17 and OpenMP and create a large temporary intermediate file.

The complete arXiv release bundle contains the remaining census inputs and auxiliary audit scripts so the submitted manuscript and its verification snapshot can be archived together.
