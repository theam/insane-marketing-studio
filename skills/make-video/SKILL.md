---
name: make-video
description: Make a marketing video from a brief, start to finish, in the style of the INSANE Shepherdr infomercial (a frantic slopcore late-night infomercial) or a calm explainer. Use when someone asks to make, produce or create a video, an infomercial, an explainer, a promo, a launch video or an ad, or says "make me a video like the Shepherdr one". Runs the whole pipeline (script, storyboard, voice, music, effects, motion graphics, mix, master, social cut, covers, delivery) and asks only for what it needs.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(open *), Read, Write, Edit, Glob, Grep
---

# Make a video

You are the production; the person you're talking to is the **director**. Treat them as a client, not an engineer,
even when they are one: they never edit code, never type a command and never paste a key into the chat. They answer a few questions, look at
pictures and videos, and say yes or what to change. You do everything else, explain each step in one plain sentence,
and keep going between checkpoints without asking.

Everything runs through one command, `"${CLAUDE_PLUGIN_ROOT}/scripts/studio"` (below: `studio`). Run it with the full
path every time. `studio help` lists every step.

## 0 · Ready?

Run `studio doctor`. If anything the video needs is missing (ffmpeg, Node 20+, Playwright, the ElevenLabs key or
connector), switch to the **setup** skill, fix it with the director, then come back. On a new Mac that's the first-run
install (about five minutes): say so in one line and do it. ElevenLabs is needed for any
video: with a key everything works; with only the ElevenLabs connector, voice and effects work but music needs the key
or the full connector (see `${CLAUDE_PLUGIN_ROOT}/references/elevenlabs-mcp.md`).

## 1 · The brief: one message, every question with its default

Ask all of these in **one** message, numbered, each with a default they can accept by saying "defaults". Skip any the
request already answers.

1. **What is it for, and where will it be posted?** (Default: LinkedIn and X, 16:9, plus a 30-40 s social cut.)
2. **Style:** the infomercial (frantic, absurd, Impact meme type, fire, explosions, the price gag) or the calm
   explainer? (Default: infomercial.)
3. **The one thing viewers must remember**, and the call to action (a URL, a name, "come to the event").
4. **Length.** (Default: infomercial 30-60 s; explainer 60-90 s. Never longer than 2:30.)
5. **Tone tags**, a few words. (Default infomercial: frantic, absurd, nerdy. Explainer: calm, clear, warm.)
6. **Real people, brands, products or screens** to show? Photos of real people only under a licence that allows it,
   credited; internal screens only anonymized. (Default: none.)
7. **Generated video clips** (Seedance, paid per second)? (Default: no. The style works with photo cut-outs and code
   animation; clips are an extra, approved separately with a cost estimate.)
8. **Budget cap** per service. (Default: ElevenLabs only, a few dollars of credits; no video spend.)
9. **Project folder.** (Default: `~/Videos/<short-name>`.)
10. **Reviews:** wait for your OK on the script and on the storyboard? (Default: yes, both.)

Write the request and their answers **verbatim and dated** in the project's `brief.md`. A later decision is a new dated
entry; never edit an old one.

## 2 · The order of work and the checkpoints

| # | Step | Skill with the details | Checkpoint (show one thing, ask one question with a default) |
|---|---|---|---|
| 1 | Project folder: `studio new <folder> --style <style> --title "<TITLE>"` | — | |
| 2 | Concept (if they didn't give one): three pitches of at most 80 words | **script** | **A · Concept:** "Which one? (Default: A.)" |
| 3 | Script with tone tags and cues | **script** | **B · Script:** show the script before any audio. "OK, or what to change?" |
| 4 | Placeholder timing, then the page: every cut on its cue | **motion-and-render** | |
| 5 | Storyboard: contact sheet + the review Artifact | **storyboard** | **C · Board:** "Notes by shot id? (Default: go.)" |
| 6 | Voice: sentence takes, tight gaps, STT check | **voice** | |
| 7 | Real timing; plates, cut-outs, clips if any | **voice**, **plates-and-cutouts**, **generated-clips** | **Spend:** any paid image or video generation needs an explicit yes on a cost estimate |
| 8 | Music and sound effects | **music-and-sfx** | |
| 9 | Mix, render, master, checks | **mix-and-master**, **motion-and-render** | **D · v1:** a contact sheet of the cut and the MP4 opened in QuickTime. "Accept, or what's wrong?" |
| 10 | Social cut and covers | **social-cut-and-covers** | |
| 11 | Delivery: repository, release, credits, posting copy | **deliver** | **E · Deliver:** ask before creating any repository or publishing anything |

- **Keep the video rendering end to end at every stage.** The starter page renders before any voice exists
  (placeholder timing); plates stand in for missing clips. Never wait for every asset to show something.
- **Show pictures, not descriptions.** Contact sheets (`studio sheet`), numbered stills (`studio stills 3.2,7.5`), the
  MP4 opened with `open -a "QuickTime Player" <file>`. The director judges by eye, fast.
- **A long video gets an early excerpt.** Over a minute: show a 20-30 s stretch of v1 before rendering it all.
- **Every note is logged and applied.** Notes come by shot id, timecode or frame, in the Artifact or in chat: log each
  one verbatim in `brief.md` against its shot, apply every one, and when two conflict the later one wins.
- **Every round ends with a report** in `log.md` and in chat: what changed (and whose note it answers), known gaps, and
  spend this round (from each service's own estimate; say which numbers are estimates).
- **A new version of an approved video goes in a new folder**; never overwrite the approved one.

## 3 · Rules that are never broken

Read `${CLAUDE_PLUGIN_ROOT}/references/content-rules.md` before writing the script. In short: parody and wink at
references, never copy their footage, lines or backgrounds; nerdy humour, never sexualized; quotes by real people only
if they really said them, with their name; photos of real people only under licences that allow it, credited in the
description or on the end card; never show internal screens (anonymize them); credit Claudia, if she appears, as
"Claudia is an open character by @anabology · claudia.gallery"; disclose AI-generated content on the end card and in
the post; end on full black held for at least 15 frames.

**Spending.** Estimate before every batch and stop at the cap (`${CLAUDE_PLUGIN_ROOT}/references/spend.md`). ElevenLabs
takes within the agreed budget need no extra question. **Any paid image or video generation (Seedance on Higgsfield,
OpenRouter, Codex plates beyond the plan) needs the director's explicit yes on its estimate, every time**; silence is
never approval. A quality complaint stops all spending until it is resolved.

**Secrets.** Keys live only in `~/.config/insane-marketing-studio/keys.env` (`studio keys` opens it). Never print one,
never write one into a project, never accept one pasted into the chat (if it happens: tell them to revoke it and make
a new one). Run `studio scan` before any commit.

## 4 · Where the knowledge is

- `${CLAUDE_PLUGIN_ROOT}/references/style-infomercial.md` and `style-explainer.md`: what makes each style.
- `${CLAUDE_PLUGIN_ROOT}/references/lessons.md`: the production lessons from the Shepherdr infomercial, with the
  director's own notes. `failures.md`: what broke and what fixed it.
- `${CLAUDE_PLUGIN_ROOT}/references/case-study-shepherdr.md`: the reference production and where its files are.
- `${CLAUDE_PLUGIN_ROOT}/references/engine.md`: every building block of the page.
