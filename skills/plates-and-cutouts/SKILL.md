---
name: plates-and-cutouts
description: Make the pictures a video needs — photographic cut-outs (stickers), full-bleed plates, fire and explosion elements — with Codex image generation, macOS Vision subject lifting and chroma keying; use the kit's starter cut-outs; handle photos of real people under licence. Use when a shot needs an object, a person, a background, a mascot or a sticker.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/studio *), Bash(open *), Read, Write, Edit
---

# Plates and cut-outs

The infomercial's look is **real photographic cut-outs, never drawings** ("big Impact is much more meme"),
centred, one idea per cut, often with a white sticker outline. Effects on stills stand in for video. Cheap and homemade
beats polished.

## Free first: the starter cut-outs

`engine/cutouts/` (in every project) has Codex-made cut-outs from the Shepherdr production: blender, brain, cat-tests,
coffee-cube, container, crown, goat, goat-engineer, gpu, hammock, headphone-sheep, laptop, office-chair, plant-laptop,
ram-stick, rubber-duck, server, sheep, tiger (CC BY 4.0, The Agile Monkeys; disclose them as AI-generated). Use them as
`sprite(el, 'kit:rubber-duck', 560, 'obj stk')`. Fire and explosions are in `engine/fx/`. The folder also holds The
Agile Monkeys' wordmarks (`tam-wordmark-white`/`-black`): trademarks, not licensed for other uses; put the director's
own logo in `assets/cutouts/` for the end card.

## New pictures with Codex (asks first)

Codex image generation runs on the person's ChatGPT plan (Codex CLI, `codex login`). It's not billed per image, but
it's image generation: **show the list of prompts and ask before running it.**

1. Write `assets/plates/book.json`: `{"<id>": {"prompt": "...", "shape": "square", "n": 2}}`.
   - A cut-out: "A real photograph of <object>, isolated on a flat pure green (#00FF00) background, no shadow on the
     background, nothing else in the frame, no text." (Magenta for green objects.) Or on any plain background and let
     Vision lift it.
   - Fire, explosions, light: "… isolated on a pure black (#000000) background" (the page screens it in).
   - A full-bleed plate is the shot's **first state** (the window already open, the room as it must look).
   - A character: attach face references every time (`"refs": ["assets/refs/face.png"]`): without them the likeness
     drifts.
2. `studio plates assets/plates/book.json` → `assets/plates/cands/<id>/<k>.png`. Keep every candidate.
3. Show them (`studio sheet` doesn't apply here: open the images, or make a sheet with the director's picks).
4. Cut the pick out: `studio cutout assets/plates/cands/goat/1.png assets/cutouts/goat.png` (macOS Vision lifts the
   subject and trims it), or `studio chroma in.png assets/cutouts/goat.png green`. Check the edge on a dark and a
   light background.

Codex refuses some words: rephrase, never alter an image to get past a filter. OpenRouter's video models refuse
photoreal people; Codex makes those plates.

## Real people, brands and screens

- **Photos of real people** only under a licence that allows it (Wikimedia Commons: CC BY, CC BY-SA, public domain),
  as parody cut-outs, undistorted. Record each in `assets/cutouts/CREDITS.md` (file, author, licence, source URL) and
  put the attribution on the end card and in the post. Quotes on screen only if they really said them, with their
  name and title. Shepherdr: Dario Amodei (TechCrunch, CC BY 2.0), Elon Musk (Gage Skidmore, CC BY-SA 4.0), Jensen Huang
  (The White House, public domain).
- **A real product photo** (another company's): cut out of a press image, credited ("Image: Tesla, via Electrek").
- **Confidential screens never appear as they are.** Rebuild or anonymize them first (no client data, colleagues' names,
  calendars, figures): the Shepherdr explainer replaced an internal page with an anonymized version. Screenshots go in
  `assets/screens/`.
- **Claudia** (claudia.gallery) is an open character anyone may use: take her identity text from the claudia MCP
  (`claudia_canon`, at https://claudia.gallery/mcp) and credit her "Claudia is an open character by @anabology ·
  claudia.gallery".
