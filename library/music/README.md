# Library scores

A library score lets `studio fit-music --library NAME` lay music under a video without composing a new bed: each chunk
of the project's `music.json` plays the score's section named in its `"library"` field, from that section's first beat,
cut to fit. It's the fallback when you can't compose (the ElevenLabs connector in Claude has no music) and you have a
track you have the rights to use.

**The kit ships no score.** The INSANE Shepherdr infomercial's score was composed with ElevenLabs Music, whose terms
don't allow sharing generated music for other people to reuse, so it stays with the team that made it. Compose your own
when you can (an ElevenLabs API key, or the full ElevenLabs connector): `studio music` writes a bed whose sections
change where your story turns.

## Adding one

Put two files in `~/.local/share/insane-marketing-studio/music/` (kit updates don't touch it):

- `NAME.mp3`: the track.
- `NAME.json`: where its sections are, and the credit to print:

```json
{
  "title": "My score",
  "source": "Music: <title> by <author>, <licence>",
  "bpm": 126,
  "sections": {
    "muzak":  { "start": 0.0,   "end": 17.76, "what": "sad elevator muzak: the problem" },
    "reveal": { "start": 33.41, "end": 38.16, "what": "a hit into the hype anthem" },
    "hype":   { "start": 38.16, "end": 62.95, "what": "relentless synth-funk under a fast voiceover" }
  }
}
```

The infomercial template's `music.json` names these sections: muzak, build, reveal, hype, escalate, butwait, cooking,
offer, finale. Rename them in either file so they match, and credit the track on the end card.
