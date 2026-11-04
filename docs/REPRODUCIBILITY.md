# Reproducibility and evidence availability

This repository publishes **source code, six predeclared action comparisons and reported raw rationales**, but it does **not** publish the local evidence pack. Replaying the exact sealed Gate 7 run requires the six real-world JSON manifests, the original JPEG assets, `manifests/seal.json`, `manifests/truth.json`, and the imported model records. These are not bundled here because the photographed catalog assets have different licensing/provenance conditions.

## Run source tests without the evidence pack

```powershell
cd Gate7
python -m unittest discover -s tests -v
cd ..\Gate8_2
python -m unittest discover -s tests -v
```

Gate 7 tests use **synthetic local fixtures** to validate sealing, tamper checks, and payload field exclusion. They are not six real Muse evaluations.

## Run the full replay with a verified local evidence pack

```powershell
cd Gate8_2
python .\gate8.py --gate7 C:\Projects\RECALLZERO_BlindCausal_G7 --check
python .\gate8.py --gate7 C:\Projects\RECALLZERO_BlindCausal_G7 --port 8770
```

The web interface is at `http://127.0.0.1:8770`. Missing images, imported responses, truth manifests or seal cause the server to refuse the full replay. Do not treat the source-only repository as a turnkey runnable hosted demo. Use the linked submission video to see the recorded working run.

The public report in `results/gate7_results.json` reports the **six selected conditions**, not independent field measurements. A/B/F reuse photos, and the baseline uses **human transcription + rules**, not OCR. No production payment, recall or counterfeit certification occurred.
