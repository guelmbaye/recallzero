# Architecture

```text
Source photographs + provenance / inspection
             |
     SHA-256 evidence checks
             |
 Human-validated labels -> sealed manifest / truth (excluded from model input)
             |
   Blind multimodal image payloads
             |
    Meta Muse Spark 1.3 API
             |
  Raw JSON action + rationale
             |
  Read-only import and comparison
             |
  Illustrative policy controller (NO REAL CHECKOUT)
             |
  Gate 8.2 localhost replay + proof ledger
```

The runner stores SHA-256 hashes in `manifests/seal.json` and refuses a modified evidence snapshot. This protects against undetected local changes but is **not** a third-party timestamp or certification.

**Decision scope:** `ALLOW` in condition C means no visible marking conflict in a controlled policy; it does **not** authorize payment, identify a genuine product, or establish electrical safety. B/F linkage is based on the contributor's description, not independent inventory verification.

The API is called by `Gate7/gate7_muse_bridge_v2.py` only with `--live --confirm-cost` and `MODEL_API_KEY` present. The Gate8_2 server does not make any Meta calls.
