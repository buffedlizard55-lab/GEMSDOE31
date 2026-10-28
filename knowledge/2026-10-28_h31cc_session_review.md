# H31-CC session review — 28 October 2026

Branch `arena/bb6d6287-gemsdoe31`. Lane self-assigned because the prompt’s method paragraph was absent. The same prompt ordered 3–5 new hypotheses and validation of the top one. That assignment is `knowledge/2026-10-28_h31cc_preregistration.md`. No weekly slot was used. DrivenData was not contacted.

## Decision

**DO NOT SUBMIT.** No current artifact is approved. No human sign-off can override this.

A new GeoTIFF was generated. It is unique against the nine named sites and it passes the local `[0, 1]` format check. It failed the scientific gate and the literal calibration-lattice gate.

| File | Number | Unique versus the nine sites? | Submit? |
|---|---|---|---|
| `docs/downloads/gems31-h31cc-basement-step-37654d-20261028-zeros.tif` | HOLDOUT-DTI 0.0471 [0.0332, 0.0618], `gems57-pooled-hide-v2`, 60,988 withheld. Leaderboard estimate unavailable. | Yes. Maximum 9.64% of dots within 3 px (GEMSDOE27). H33-2-B2 is 8.01%. | No |

SHA-256 `0e82a9e8b80052d0bc61e8f550b2ac5204d012ab1f53fb2208051f285f10ad44`. Name `gems31-h31cc-basement-step-37654d-20261028`. Note (92/140): `H31-CC basement-step low-slope grav dilate 37654d B2 | HOLDOUT-DTI 0.0471 | not a live score`.

Use the all-finite zeros file only if a portal said “Predicted values must be in range [0, 1]” because of NaN. That is a format fix, not permission to upload.

## Why H33-2-B2 is the highest USER-REPORTED number in the nine sites

The value 0.2778 is USER-REPORTED. No organizer receipt is in this repository. The prompt also says 0.3195 and 0.4413. Those three numbers conflict and none was confirmed here.

Byte comparison already in `evidence/h33_forensics_20261025.json`: H33-2-B2 is an exact subset of H27-4, which is an exact subset of the D2.8 300 m Poisson field, after deleting dots within about 2 px of the public catalogue. It adds no new geological pixels. Under the published DTI (α = 0.2, β = 0.8, 300 m triangular kernel), a dot within one kernel of another mostly adds false-positive weight. Deleting catalogue-flank dots can raise the score if those dots were not covering hidden truth. That is a plausible mechanism, not a proof, and not a recipe this session copied.

This session’s same-code rescore of that file is HOLDOUT-DTI 0.0067 [0.0060, 0.0074] on the catalogue-gap folds, because the file was built to avoid the public catalogue. Its SGMC off-catalogue proxy DTI is 0.0940 (61,664 proxy positives). H31-CC’s same proxy is 0.0078. Neither number is a competition score.

## Can a new file beat 0.2778?

Not this one. H31-CC’s paired difference versus a same-domain chance map is −0.0097 [−0.0235, +0.0052]. The interval includes zero and the point estimate is worse. Feature-alone AUCs are 0.43–0.54, so the operator does not recover catalogue faults and is not leaking the labels. The official hidden faults are unavailable. A projection is not a score. Nothing here supports 0.3195 or 0.4413 either.

The reference solution on GitHub is a U-Net, not a hand lineament. That is a different lane and was not fit. No GPU run was made. Copying H33 would fail the 70% overlap rule and was not done.

## Hypotheses

Ranked in the preregistration. Only rank 1 was fit: basement-depth gradient, slope below 4°, gravity horizontal-gradient rank, positive dilatation. Rank 2 (signed magnetic–gravity offset) remains the next scientific candidate and needs its own preregistration. Ranks 3–5 were not fit; rank 3 is too close to existing tilt-worm work.

## Three passes

1. Implementation. Restored the hash-pinned feature stack (19 band hashes matched the template receipt), labels, sample, SGMC, the nine focus rasters, and the spacing-5 lattice. Ran canaries, pre-placement uniqueness, and the screen. Confirmation was not run because the preregistered bar failed.
2. Bug review. The first canary used distance-to-background instead of distance-to-fault and returned NaN. Fixed and rerun; AUCs are finite. The first uniqueness load exceeded the 3.8 GB sandbox. Priors are now streamed. CC1’s paired interval versus NULL is entirely negative; CC2 and CC3 intervals include zero. No arm was retuned after those numbers.
3. Acceptance. Local format validator: no hard failures; values in [0, 1]; EPSG:32611; shape 3730×3292; transform matches. Lattice overlap 99.61% is disclosed and blocks upload. Nine-site overlap is below 10%. `ok_to_submit` is false.

## Sources for manual review

- [Competition problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — not fetched; host is outside this sandbox allowlist.
- [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — not fetched. No live score is claimed.
- [Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) — fetched this session. It is a U-Net notebook, initial commit `aebe92f`, author John Lipor.
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) — not fetched. DOI 10.5066/P93LGLVQ is the dataset cited by the local data manifest.
- [EPSG:32611](https://epsg.io/32611)
- [Tversky index](https://en.wikipedia.org/wiki/Tversky_index)
- Band names were read from the owner-mirror `training_features.tif` tags, not from a fresh USGS page.

## Irregularities

- The prompt’s method paragraph is missing. The lane was self-assigned and disclosed.
- 0.2778, 0.3195, and 0.4413 cannot be reconciled from evidence in this checkout.
- The spacing-5 lattice makes the literal 70% rule fail for any interior map. It was not exempted and not evaded.
- H31-X’s historical HOLDOUT-DTI 0.1661 used a 21.3 km collar and fold-wise emission. The 0.0185 figure in this card is a fixed, full-catalogue-pruned raster on an 8 km template fold. Those are not the same measurement.
