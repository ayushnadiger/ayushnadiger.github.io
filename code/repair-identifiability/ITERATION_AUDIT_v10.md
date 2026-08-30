# v10 adversarial freeze audit

This pass is a publication-readiness revision of v9. It does not change mathematical theorem statements or finite-enumeration outputs.

## Changes

1. **Current prior art.** Added Hinsche--Eisert--Carrasco, *Abelian State Hidden Subgroup Problem: Learning Stabilizer Groups and Beyond*, PRX Quantum 7, 020337 (2026), and explicitly distinguished StateHSP/hidden-cut/stabilizer-group learning from the known-topology physical-fault catalogue studied here.
2. **Abstract hierarchy.** Moved the exact Pauli-support characterization `±S(G-e) \ ±S(G)` ahead of the near-blind `Theta(g^-2)` scaling so the paper's reusable structural theorem is the first technical result advertised.
3. **Catalogue motivation.** Made the bond-local model operationally explicit as a post-localization repair decision between bond re-establishment/rerouting and boundary-memory reset/reinitialization. The manuscript continues to analyze the broader arbitrary one-/two-memory dephasing catalogue separately.
4. **Terminology.** Described `H_cut` as a single-edge-deletion (cut-only) catalogue to avoid confusing this problem with the hidden-cut problem.
5. **Code availability.** Added a public reproducibility pointer and synchronized the source bundle README.
6. **Portability cleanup.** Removed stale absolute `/mnt/data/...` import paths from five audit scripts; all imports now resolve from the release directory when the scripts are invoked normally.

## Validation plan

- run the quick deterministic Python audits listed in `repro/README.md`;
- compile the manuscript through three pdflatex passes;
- reject unresolved citations/references and overfull boxes;
- package the exact v10 source and reproducibility snapshot.

The expensive W14 enumeration is unchanged from v9; its source is included and its exact outputs remain documented in the package.
