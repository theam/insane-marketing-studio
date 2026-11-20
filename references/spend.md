# Spend: rules, prices, and what the productions cost

## Rules

1. **Estimate before every batch** (`studio voice --dry-run` for characters, `studio seedance estimate`), and **record
   the price each run reports** (the connector's run status carries `price`). The connector's `estimate_only` numbers
   miss both ways: in the kit's sample, Scribe was estimated at 7.9 credits and charged 116.8 (budget Scribe at about
   5.5 credits per second of audio), and an effect was estimated at 60.6 credits and charged 16.7. Generated video
   seconds run about 2× the seconds that end up in the cut (claudia.gallery measured 1.9× and 2.0×).
2. **Agree a cap per service with whoever pays, and put it in the runner** (`gen/shots.json` → `cap_usd`): the run
   refuses any submission that would pass it.
3. **Paid image or video generation needs an explicit yes on its estimate, every time.** Silence never approves spending.
   ElevenLabs takes inside the agreed budget don't need a new question.
4. **A quality complaint stops all spending** until it is resolved; fix the inputs (the plate, the prompt) first.
5. **One take per job**; a second take is paid for whether it's used or not. Ask for two only when a choice is worth it.
6. **Declines are free and final on that service**; never alter an image to get past a filter.
7. **Quote real spend from the provider's billing page**, not from local ledgers (they drift and count declines).
   Say which numbers are estimates.
8. Every API key gets **its own spend or credit limit** on the provider's site, set above the project's cap.

## Prices (as observed; check the provider before quoting)

| Service | What | Price | Source, date |
|---|---|---|---|
| ElevenLabs TTS, Eleven v4 | speech | 1 credit per character; 52 credits = $0.0086 (≈ $0.17 per 1,000 characters) | connector estimate and run, 3 Nov 2026 |
| ElevenLabs Scribe v1 | speech to text | ≈ 5.5 credits a second: 16.3 for 3 s, 116.8 for 21 s (1 credit ≈ $0.000165, so ≈ $0.055 a minute) | connector runs, 3 Nov 2026 |
| ElevenLabs sound effects v2 | one effect | 16.7 credits charged (≈ $0.003); the estimate said 60.6 | connector runs, 3 Nov 2026 |
| ElevenLabs Music v2.5 | a composed bed | not measured on its own (in the 37,389 characters below) | — |
| Seedance 2.5 on Higgsfield | video | $2.31 per 5 s at 720p (≈ $0.46/s); list $0.4622/s 720p, $1.1372/s 1080p | production ledger; claudia.gallery, Oct 2026 |
| Seedance 2.5 on OpenRouter | video | ≈ $0.23/s at 720p ($1.17 per 5 s, $1.86 per 8 s); refuses photoreal people | production, actual |
| Codex image generation | plates, cut-outs | on the ChatGPT plan, no per-image charge recorded | production |

## What the Shepherdr infomercial cost (20-22 Oct 2026)

| Service | Spend | Basis |
|---|---|---|
| Higgsfield (Seedance 2.5, 720p) | **$48.54**: 21 delivered takes (8 overnight $18.49, 9 in epilogue v2 $20.80, 3 in v4 $6.93, 1 in v5 $2.31); 27 submitted, 6 failed for lack of credit | estimates in the production's `gen/ledger.jsonl`; paid from the balance plus a top-up |
| OpenRouter (same model) | **$8.39**: 10 submissions, 4 refused, 6 delivered | provider usage |
| ElevenLabs | **37,389 characters** measured for the explainer and the infomercial's first passes (voices, voice designs, 35 effects, 2 music takes); later rounds (62 chunks, recomposed music, Scribe) not measured | account usage, before and after |
| Codex | 152 candidates on the ChatGPT plan | the production's plate log |
| **Video total** | **≈ $57** | |

The estimates before spending were $50-80 with a $100 cap, then $20-40; for the epilogue round $21 + $7 against an
actual $20.80 + $6.05.

## What this kit's sample cost (3 Nov 2026)

The kit's first sample, a 23.7 s infomercial, made from a fresh install through the entry skill, with no API key:

| What | Credits | Cost (connector's own prices) |
|---|---|---|
| 12 narration takes (Eleven v4) | 472.0 | $0.078 |
| Scribe on the narration (word timing) | 116.8 | $0.019 |
| 14 sound effects (13 kinds, one retake) | 233.3 | $0.039 |
| **Total** | **822.1** | **$0.136** |

No paid video or image generation: the Shepherdr production's score for the music, its starter cut-outs for the pictures. The
Claude session that made it ran 100 turns in 16 minutes; its token use, priced at API rates, came to $6.61 (on a
Claude subscription it's part of the plan's usage).
