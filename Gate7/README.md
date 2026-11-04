# RECALLZERO — Gate 7: Blind Cross-View Causal Proof

**Public-source distribution:** the original local Gate 7 run completed 6/6 recorded Muse decisions, but the sealed runtime evidence pack is not included here. Source tests use synthetic fixtures.

Gate 7 tests whether additional visual evidence changes an agent decision appropriately, versus a conservative rules baseline. This is **not** a counterfeit certification, verified retail inventory test, commercial checkout, or statistical model superiority claim.

## Requirements

- Python 3.10+ (standard library only)
- Your **existing** Gate 6 image files and the verified Meta Muse client used in Gate 6 (not bundled here)
- No credentials required for any bundled command

## 0. Start (PowerShell)

```powershell
cd C:\Projects\RECALLZERO_BlindCausal_G7
python .\gate7.py status
python -m unittest discover -s tests -v
```

The package has been initialized already. `init` is provided for a fresh copy; do not run with `--force` on your inspected manifests.

## 1. Link evidence

Copy original source JPEGs from `C:\Projects\RECALLZERO_RealWebEvidence_G6\web_images\` into `evidence\`, keeping original byte content. For example:

```powershell
Copy-Item C:\Projects\RECALLZERO_RealWebEvidence_G6\web_images\ryobi_01.jpg .\evidence\ryobi_01.jpg
Copy-Item C:\Projects\RECALLZERO_RealWebEvidence_G6\web_images\ryobi_04.jpg .\evidence\ryobi_04.jpg
```

Edit `worlds/A.json` and `worlds/B.json` with photo entries:

```json
{
  "path": "evidence/ryobi_01.jpg",
  "sha256": "<RAW FILE SHA256> ",
  "source_page": "https://commons.wikimedia.org/wiki/File:Counterfeit_Ryobi_18V_4Ah_battery_01.jpg"
}
```

Use `Get-FileHash .\evidence\ryobi_01.jpg -Algorithm SHA256` to calculate the *raw* file digest. Do **not** copy the resized/EXIF-stripped photo seal from Gate 6 as the raw file digest. A and B should use the relevant first and both views respectively; F may reuse the cross-view pair, but its adversarial text is only a prompt-resilience test. This is **not** six independently sampled products.

Set the world `observed_marks` manually after inspection, e.g. `{"side_capacity_ah": 6, "base_model_code": "RB18L40"}` for B. These annotations are deliberately withheld from the exported blind payload.

For C, D, and E, collect actual independently reviewable evidence; do not manufacture a consistent case, illegible label, or mismatched pairing by editing images. Set a written `independent_case_provenance` and `unit_linkage_basis`; distinguish the contributor's claim about the same device from independent confirmation.

Set `evidence_inspected_by_operator` true **only after inspection**.

## 2. Record truth, then seal

Update `manifests/truth.json` with the operator name and policy truth after independent case checks. Change `status` to `INSPECTED_PRE_MODEL`. The predefined outcomes are **hypotheses**, not proven factual labels. To seal:

```powershell
python .\gate7.py status
python .\gate7.py seal
```

`seal` blocks if any of six worlds lacks evidence/inspection/provenance. Sealing is immutable in the run: to change evidence, create a separate new run. It hashes the truth JSON, manifests, world JSON and raw evidence bytes. This is an integrity seal, **not** a trusted external timestamp.

## 3. Execute local baseline and export blind model payloads

```powershell
python .\gate7.py baseline
python .\gate7.py export
```

Baseline uses **human-transcribed marks plus rules**, not OCR. Do not label it an OCR comparison. Model payloads under `reports/payloads/` exclude ground-truth labels, case descriptions, operator notes and observed marks. A transport adapter must send image bytes and ensure source filenames, metadata, URL paths or image annotations with the answer are **not forwarded**. For a stronger blind test, neutralize revealing filenames and audit your exact outgoing request.

## 4. Optional Muse live calls (adapter included)

`gate7_muse_bridge_v2.py` is included and uses `https://api.meta.ai/v1` with `muse-spark-1.3` via the OpenAI-compatible Python SDK. It is dry-run by default, requires a separately populated **valid sealed evidence pack** and `MODEL_API_KEY`, and only makes a potentially billed request when both `--live` and `--confirm-cost` are provided. Do not upload secret keys or publish live model response records without review.

After each legitimate model call, write a local JSON result (example schema, **not a real result**):

```json
{
  "world_id": "B",
  "action": "HOLD_FOR_REVIEW",
  "model": "EXACT_MODEL_ID_FROM_PROVIDER",
  "stage": "cross_view",
  "raw_response": {"example_only": "REPLACE_WITH_VERBATIM_PROVIDER_RESPONSE"}
}
```

Import one result per world. `raw_response` must preserve the real provider response:

```powershell
python .\gate7.py import-model --file .\my_muse_B.json
```

One result is allowed per world in this initial run, preventing silent replacement of unfavorable outputs. For a new evaluation, use a separately pre-registered run and preserve all attempts, including failures.

## 5. Evaluate

```powershell
python .\gate7.py evaluate
Get-Content .\reports\gate7_results.json
```

Incomplete evidence or missing model outputs must not be presented as benchmark success. The report always sets `meta_superiority_proven=false`: a favorable 6-case observation is insufficient for a statistical superiority claim. No live purchases, merchant inventory verification, or transaction interventions are performed.

## Gate transition

- **G7-a PASS**: runner offline tests pass; evidence integrity checks function.
- **G7-b PASS**: six evidence-grounded worlds independently inspected and sealed.
- **G7-c PASS**: real provider outputs imported with blind-request audits and results evaluated.
- **G7-d RESEARCH CLAIM**: add a properly sized held-out set, real OCR baseline, blinded unit provenance, stage-wise ablations, repeated calls, and predeclared statistical criteria.

Reject assertions such as *verified counterfeit*, *Meta superiority proved*, or *real checkout prevented* unless supported by additional independent evidence.
