# RECALLZERO Gate 8.2 — Single-Screen Jury Experience

A localhost-only replay that **requires the original sealed Gate 7 runtime data** (not included in this source-only repository) of the **real archived Muse responses** and SHA-256-sealed evidence in Gate 7.

## Windows setup

Extract to `C:\Projects\RECALLZERO_EvidenceReplay_G8_2` and run in PowerShell:

```powershell
cd C:\Projects\RECALLZERO_EvidenceReplay_G8_2
python .\gate8.py --gate7 C:\Projects\RECALLZERO_BlindCausal_G7 --check
python -m unittest discover -s tests -v
python .\gate8.py --gate7 C:\Projects\RECALLZERO_BlindCausal_G7 --port 8770
```

In a second terminal: `Start-Process http://127.0.0.1:8770`.

## Jury mode

- Use **Reveal next proof** or **Right Arrow** to advance A → B → F.
- **Recording view** hides the header/footer; use browser F11 for full-screen 1920 × 1080 recording.
- **Auto-play** advances every 8.5 seconds, stops on F (does not loop), and pauses if the tab becomes hidden.
- **Explore six cases** exposes C/D/E, while the right-side **Show audit** reveals the SHA-256 ledger.
- Markings are presented as **browser-only reading aids** alongside original full JPEGs; no original image or archived Muse response is edited.

## Evidence and safety boundaries

- The server calls the existing `Gate 7.verify_seal()` and validates each original JPEG and archived action/rationale.
- No Meta API calls, payment actions, checkout requests, or file writes are implemented by the replay.
- The checkout response on screen is an **illustrative simulated policy**. The HTTP 423 was observed in the **separate Gate 6 simulated checkout**, not during Gate 8.
- B and F use contributor-described same-unit linkage; no independently verified physical identity; C is a one-photo check; the six conditions are not an accuracy benchmark.
- An archived decision is not a certification of authenticity and `ALLOW` means only no visible conflict in the narrow scenario.
- Screenshots and timing must be validated in the user's browser; Python tests do not certify UI layout.

## Verification

`python .\gate8.py --gate7 C:\Projects\RECALLZERO_BlindCausal_G7 --check`

Expected: `VERIFIED_SEALED_REPLAY` with `model_correct: 6`, `baseline_correct: 5`, `server_calls: 0` when pointed at your fully populated Gate 7 folder.
