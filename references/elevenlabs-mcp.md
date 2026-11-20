# The ElevenLabs connector (MCP) in this pipeline

Tested on 3 November 2026 from Claude Code with the claude.ai **ElevenLabs** connector connected (the "restricted"
one, `https://api.elevenlabs.io/v1/mcp-claude-marketplace`). Every row below is from a real call, not the docs.

## What it can and can't do for each step

| Step | Through the connector | With the API key (`studio`) |
|---|---|---|
| Cast a voice | **Yes, and better**: `creative_list_voices` with filters returns voices with a `preview_url` to listen to. Voice Commander Xtreme (`Tsns2HvNFKfGiNjllgqo`) is there. | Needs the voice id. |
| Design a voice | **Yes**: `creative_design_voice`, then `creative_save_designed_voice`. | Possible, not wrapped. |
| Speech takes (Eleven v4, tags) | **Yes**: `creative_generate_speech` (prompt, voice, model; 1 credit per character: 52 credits = $0.0086). Default 2 takes per call; ask for 1. | Yes, cached per sentence. |
| Word timestamps of a take | **No.** The speech result has the audio and its length, no alignment. Voice settings (speed, stability, style), seed and output format aren't exposed either. | Yes, in the same call (`with-timestamps`). |
| Word timestamps of any audio | **Yes**, via Scribe: upload the file, `creative_transcribe_audio`, and the result has `words` (text, start, end per word) plus a `words_download_url`. About 5.5 credits a second (116.8 for the sample's 21 s; its estimate said 7.9). | `studio scribe`. |
| Sound effects | **Yes**: `creative_generate_in_flow` with node_type `sfx` (`eleven_text_to_sound_v2`). Default 4 variations: ask for 1. That tool takes no length: effects come back at 1-2 s. The node type has `duration_seconds`, `prompt_influence` and `loop`, settable through `creative_add_flow_node`'s `model_parameters` and `creative_run_flow_nodes` (not tested). Charged 16.7 credits each in the sample (estimated 60.6). | `studio sfx`, in parallel, with each kind's length. |
| Music | **No.** The connector refuses music, image and video nodes. The **full** connector (`https://api.elevenlabs.io/v1/mcp`, added in claude.ai as a custom connector) has them; it signs in with OAuth only (an API key gets 401), and was not authorized during this test, so its music tools are untested here. | `studio music` (composition plan, sections). |
| Phone/radio/room effects on audio | Yes: `audio-effects` node (free). | ffmpeg chains (`telephone`, `broadcast`). |

## How its outputs reach the disk

Every result carries a signed `content_url` (and `words_download_url` for Scribe) on `elevenlabsusercontent.com`. A plain
GET with no credentials downloads it (tested: 200, `audio/mpeg`, 65,652 bytes, mp3 44.1 kHz mono 128 kbps). The links
expire about 2.5 hours after the generation. `studio fetch "<url>" <file>` saves one where the pipeline expects it.

Going the other way (a local file into the connector, for Scribe): `creative_create_asset_upload` (name, mime type,
exact byte size) returns an `upload_url`; one HTTP PUT with the same Content-Type uploads it (`studio put "<url>" <file>
<mime>`, tested: 200); `creative_finalize_asset_upload` with the flow puts it on the flow as a node; that node is the
`connect_from` of the transcription.

Every generation lands on an ElevenLabs **flow** (a canvas the person can open in their browser). Make one flow per
project (`creative_create_flow`) and pass its id to every call.

## The flow the kit uses

- **With a key** (recommended for anything over a few lines): `studio voice`, `studio music`, `studio sfx`, `studio
  scribe`. One call per sentence gives the audio and its word times; music follows the script's sections.
- **With only the connector**: `studio voice --plan` → one `creative_generate_speech` per sentence → `studio fetch` →
  `studio voice` assembles → upload the narration and transcribe it with Scribe → `studio timing
  timing/scribe-words.json`. Effects: `studio sfx --plan` → `sfx` nodes → `studio fetch` → `studio sfx` trims. Music:
  the full connector, or the key, or a track you have the rights to, laid section by section with `studio fit-music
  --library NAME` (`library/music/README.md`).
- **Both**: cast and audition voices through the connector even when the takes are made with the key.

Why the Shepherdr production used the key and not the connector: the sync depends on per-word timestamps, and the
speech tool doesn't return them. Scribe through the connector closes that gap, at the cost of two extra
steps (upload and transcribe) and of timing from what was heard rather than from the text sent.
