---
name: script
description: Write the concept and the script of a marketing video in the studio's format — sections, speakers, Eleven v4 tone tags, {#cue} marks for the animation, CAPITALS for shouted words. Use for the concept pitches and the script of a new video, and to rewrite or shorten one after notes.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Read, Write, Edit
---

# Concept and script

## Concept (only if the brief has none)

Three pitches, at most 80 words each: the premise, the hook line, the escalation, the call to action, one risk. Ask
"Which one? (Default: A.) Anything to change?" They may mix them; that's fine.

## The script

Write `script.md` in the project in exactly the template's format (read the project's own `script.md` first):

- `## Script` holds the narration. `**N · Title**` starts a section; **each section gets its own music style**, so start
  one where the story turns (the problem, the reveal, the features, the offer, the close).
- A paragraph starting `NAME:` in capitals is that speaker's (add the voice to `project.json`); everything else is the
  narrator. A section titled with "(no narrator)" is a silent description (an epilogue) and ends the narration.
- `[tags]` direct the delivery (Eleven v4): `[excited]`, `[shouting]`, `[calmly]`, `[dramatically]`, `[fast]`,
  `[deep voice]`, `[desperate]`, `[annoyed]`. A tag holds until the next one. In an explainer, no forced non-verbal
  tags (`[laughs]`): the tone carries it.
- `{#name}` marks the word an animation lands on. Put one on every word where something should appear: a new idea, a
  number, a name, a punchline. Names are short, unique, lowercase.
- Words in CAPITALS are shouted and punch the frame in the infomercial. Use them for the peaks only.
- Spell names the way the voice must say them; put the on-screen spelling in `project.json` → `"display": {"Shepherder": "Shepherdr"}`.
- `## Notes` lists the source and date of every fact, quote and number.

Then run `studio voice --dry-run` (characters per take: the ElevenLabs cost) and `studio timing --placeholder` (the
estimated length). Fast infomercial narration runs about 3.5 words a second after the tempo stretch; a calm explainer
about 2.4.

## What makes the infomercial script work (from the director's notes on Shepherdr)

- **Infomercial structure:** the problem (the viewer's, played big) → "there has to be a better way" → "Introducing…"
  → how it works, one feature per line → "But wait, there's more!" → the offer and the price gag → the call to action →
  a deadpan disclaimer ("Results not typical").
- **Open on a hook** and the viewer's own problem. Self-aware is good: "Are you fed up with AI psychosis?"
- **Escalate to the absurd** with current memes: "Run ten agents! A hundred! No… A THOUSAND!" Say who said what
  ("Dario said…"), and only quote what people really said, with the source in Notes.
- **Clarity beats cleverness.** A joke the viewer has to decode is cut ("the Manhattan bit doesn't land").
- **Cut the weakest part.** Before recording, name the part with the least energy and cut it (testimonials went:
  "they drop the intensity a lot").
- **Nerdy, never sexualized; no profanity.** Wink at references, never copy their lines.
- Product claims are true or obvious hyperbole.

Read `${CLAUDE_PLUGIN_ROOT}/references/style-infomercial.md` (or `style-explainer.md`) and
`${CLAUDE_PLUGIN_ROOT}/references/content-rules.md` before writing.

## Checkpoint B

Show the script (the text of `## Script`, plus its estimated length and the cost of one take of every line) **before
any audio is generated**, and ask "OK, or what to change?". Log the answer in `brief.md`. Keep earlier versions as
`script-v1.md`, `script-v2.md` when a rewrite is big.
