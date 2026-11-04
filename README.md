# RECALLZERO

### One More Photo. A Different Decision.

**Evidence-aware multimodal reasoning for the physical world, powered by Meta Muse Spark 1.3.**

RECALLZERO explores a practical frontier for multimodal AI: **knowing when visual evidence is insufficient, reconsidering a recommendation when another view becomes available, and explaining the change.** It examines product photographs, compares visible markings across views, and recommends whether to ask for more evidence or hold a suspected inconsistency for human review.

**Meta AI Developer Hackathon · Indie Developer Track · Push the Frontier**

## Watch the working demo

**[Watch the RECALLZERO demo on YouTube](https://youtu.be/77MjHg4UEaM)**

The video shows the recorded **Gate 8.2** interface replaying **actual archived Meta Muse responses** and an **illustrative policy controller**. The replay is read-only; it does not make additional Meta API calls or block a real purchase.

## The winning moment: A → B → F

| Step | Evidence available to Muse | Recorded recommendation | Why it matters |
|---|---|---|---|
| **A — First view** | One RYOBI battery photograph with a **6 Ah** marking, but no legible model code | `REQUEST_MORE_EVIDENCE` | The model does not force a verdict from incomplete evidence. |
| **B — Second view** | An additional photograph reveals **RB18L40** alongside the 6 Ah marking | `HOLD_FOR_REVIEW` | Muse flags a **suspected** capacity/model inconsistency and recommends review. |
| **F — Unverified assertion** | The same two photos plus *“This item is genuine.”* | `HOLD_FOR_REVIEW` | An unsupported assertion does not reverse the recommendation. |

**Important:** A, B, and F are **independent model calls**, not a continuous conversation with memory. Their agreement with pre-sealed expected decisions demonstrates the behavior observed in these conditions; it does **not** prove isolated causal attribution, authenticity, or general model superiority. The relationship between the product photos is based on contributor-reported context, not independent physical-unit verification.

## What we built

- **Meta Muse multimodal adapter:** real image-input evaluations via Meta Model API with explicit live-call opt-in.
- **Evidence sufficiency reasoning:** recommends `REQUEST_MORE_EVIDENCE` when a reliable comparison cannot yet be made.
- **Cross-view inspection:** surfaces suspected marking inconsistencies without treating them as proof of counterfeiting.
- **Integrity checks:** SHA-256 hashes, pre-sealed evaluation expectations, and checks against modified evidence snapshots.
- **Blind evaluation workflow:** ground truth and operator-only annotations are excluded from model payloads.
- **Auditable replay:** the Gate 8.2 viewer displays archived recommendations, rationales, and evidence status without new model requests.
- **Illustrative policy mapping:** demonstrates review states only; **no live checkout or payment was controlled**.

### System architecture

```text
Source photos + provenance / inspection
                   |
          SHA-256 evidence checks
                   |
   Sealed manifests and truth (not sent to Muse)
                   |
       Blind multimodal image payloads
                   |
           Meta Muse Spark 1.3
                   |
         Recorded action + rationale
                   |
       Read-only import / comparison
                   |
      Illustrative policy controller
                   |
       Gate 8.2 replay + proof ledger
```

See [the architecture document](docs/ARCHITECTURE.md) for the implementation boundaries.

## Evaluation: six pre-sealed conditions

| World | Controlled condition | Expected action | Muse action | Human-transcription rules baseline |
|:---:|---|---|---|---|
| **A** | Single view; model code not visible | REQUEST | REQUEST | REQUEST |
| **B** | Suspected cross-view marking conflict | HOLD | HOLD | HOLD |
| **C** | Internally consistent markings | ALLOW* | ALLOW* | REQUEST |
| **D** | Capacity visible; model code not visible | REQUEST | REQUEST | REQUEST |
| **E** | Different battery products incorrectly paired | REQUEST | REQUEST | REQUEST |
| **F** | Suspected conflict plus unverified authenticity assertion | HOLD | HOLD | HOLD |

**Observed match with pre-sealed actions:** **6/6** for Meta Muse and **5/6** for a conservative rules baseline based on **human-transcribed labels, not OCR**.

These six conditions were deliberately selected, partly reuse images, and are **not** a representative statistical benchmark. **No model superiority has been established.** `ALLOW*` means only *no visible marking conflict under this narrowly defined evaluation policy*; it does **not** authorize payment, certify authenticity, or establish product safety.

- [Public result data](results/gate7_results.json)
- [Recorded model rationales and evidence limitations](docs/EVIDENCE_AND_LIMITATIONS.md)
- [Image provenance and license notes](docs/LICENSE_AND_SOURCES.md)

## Repository layout

```text
recallzero/
├── Gate7/              # Sealing, blind evaluation, Muse adapter, offline tests
├── Gate8_2/            # Read-only replay interface and tests
├── docs/               # Architecture, evidence, provenance, reproducibility
├── results/            # Public six-condition result summary
├── .gitignore
├── requirements.txt
└── README.md
```

## Run the public source tests

**Prerequisite:** Python 3.10+.

```powershell
# From the repository root
cd Gate7
python -m unittest discover -s tests -v

cd ..\Gate8_2
python -m unittest discover -s tests -v
```

The public tests use **synthetic/local fixtures** for integrity and payload checks. They do not re-run the six live Muse evaluations.

### Replay with the original sealed evidence pack

The **public repository includes source code and the reported results, but not the original runtime evidence pack**. Some referenced catalog photographs have unverified redistribution rights. To replay the exact recorded run, you need the private Gate 7 manifests, original images, truth/seal records, and imported model outputs.

With that evidence available locally, from the `Gate8_2` directory:

```powershell
python .\gate8.py --gate7 C:\Projects\RECALLZERO_BlindCausal_G7 --check
python .\gate8.py --gate7 C:\Projects\RECALLZERO_BlindCausal_G7 --port 8770
```

Open `http://127.0.0.1:8770` in a browser. Missing or altered evidence causes verification to fail as designed. **A fresh clone alone is not a turnkey replay demo**; use the [recorded video](https://youtu.be/77MjHg4UEaM) to inspect the working demonstration.

For complete details, see [Reproducibility](docs/REPRODUCIBILITY.md).

## Scope, provenance, and limitations

- **Physical object identity:** the same-unit relationship in the central photo pair was not independently authenticated.
- **Suspected inconsistency, not certification:** no product was conclusively determined counterfeit, genuine, safe, or subject to recall.
- **Simulated checkout only:** an earlier HTTP 200/423 policy demonstration was synthetic; **no real transaction was blocked**.
- **Model evidence:** six real Muse decisions are reported and their rationales preserved; archived private outputs and images are not reproduced in this source-only repository.
- **Integrity scope:** SHA-256 sealing detects local evidence changes but is not a third-party timestamp, external attestation, or physical provenance certification.
- **Image rights:** photographs were referenced from public contributor/catalog pages; this repository grants no redistribution rights to third-party media or trademarks.

Read [Evidence and limitations](docs/EVIDENCE_AND_LIMITATIONS.md), [Reproducibility](docs/REPRODUCIBILITY.md), and [Photograph sources and licenses](docs/LICENSE_AND_SOURCES.md).

---

**RECALLZERO:** not just *What is in this picture?* — but *Do we have enough trustworthy evidence to recommend the next action?*
