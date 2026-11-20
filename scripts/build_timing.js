#!/usr/bin/env node
// Builds timing.js for a project's video.html from its script.md: window.PROJECT, window.TIMING, window.CUES,
// window.CAPTIONS, window.WORDS and window.SECTIONS. Extracted from the Shepherdr production (build-timing.js).
//
//   studio timing                 real timing from timing/words-lead.json (scripts/voices.py), else a placeholder
//   studio timing --placeholder   placeholder timing estimated from the words and tags (before any voice exists)
//   studio timing words.json      real timing from a transcript (ElevenLabs Scribe's format works as it is)
//
// A transcript is an array of words, or an object with a `words` array; each word needs `text` (or `word`), `start`
// and `end` in seconds (`type: "spacing"` and `"audio_event"` entries are ignored). Script words are matched to
// transcript words with a global alignment, so a misheard or missing word only blurs its own neighbourhood.
const fs = require('fs');
const path = require('path');

const DIR = process.env.PROJECT_DIR || process.cwd();
const project = JSON.parse(fs.readFileSync(path.join(DIR, 'project.json'), 'utf8'));
const md = fs.readFileSync(path.join(DIR, 'script.md'), 'utf8');
const body = (md.split(/^## Script[ \t]*$/m)[1] || '').split(/^## /m)[0];
// The spelling the voice needs → the spelling the screen shows (project.json "display").
const DISPLAY = project.display || {};
const display = w => Object.entries(DISPLAY).reduce((s, [a, b]) => s.split(a).join(b), w);
// Spoken paragraphs; a section marked "(no narrator)" is a description, not narration, and ends them.
const lines = body.split('\n').map(l => l.trim());
const stop = lines.findIndex(l => l.startsWith('**') && /no narrator/i.test(l));
const spoken = (stop >= 0 ? lines.slice(0, stop) : lines);
const TAG_PAUSE = { 'short pause': 0.35, pause: 0.6, 'long pause': 1.0, chuckles: 0.7, 'laughs softly': 0.8, laughs: 0.9 };

const tokens = [];
let section = 0, para = 0;
for (const p0 of spoken) {
  if (!p0) continue;
  const sm = p0.match(/^\*\*(\d+)\s*·/);
  if (sm) { section = +sm[1]; continue; }
  if (p0.startsWith('**')) continue;
  para++;
  const m0 = p0.match(/^([A-Z][A-Z0-9_]+):\s*/);
  const speaker = m0 ? m0[1].toLowerCase() : 'narrator';
  const p = m0 ? p0.slice(m0[0].length) : p0;
  let cue = null, pause = 0;
  for (const m of p.matchAll(/\{#(\w+)\}|\[([^\]]+)\]|([^\s{[]+)/g)) {
    if (m[1]) { cue = m[1]; continue; }
    if (m[2]) { pause += TAG_PAUSE[m[2].toLowerCase()] || 0; continue; }
    const raw = m[3];
    const shown = display(raw).replace(/^"/, '“').replace(/"$/, '”');
    tokens.push({ raw, display: shown, norm: norm(raw), cue, pause, para, section, speaker });
    cue = null; pause = 0;
  }
}
if (!tokens.length) { console.error('script.md has no spoken words under "## Script"'); process.exit(1); }

function norm(w) { return w.toLowerCase().replace(/[^a-z0-9]/g, ''); }
function similar(a, b) {
  if (a === b) return true;
  if (!a || !b) return false;
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++)
    d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return 1 - d[a.length][b.length] / Math.max(a.length, b.length) >= 0.7;
}

function placeholderTimes() {
  let t = (project.timing && project.timing.lead) || 0.5, lastPara = tokens[0].para;
  for (const tok of tokens) {
    if (tok.para !== lastPara) { t += 0.3; lastPara = tok.para; }
    t += tok.pause;
    const dur = Math.min(0.6, Math.max(0.2, 0.1 + 0.05 * tok.norm.length)) * 0.8;
    tok.start = t; tok.end = t + dur * 0.85; t += dur;
    if (/\.\.\.$|…$/.test(tok.raw)) t += 0.3;
    else if (/[.?!]["”]?$/.test(tok.raw)) t += 0.15;
    else if (/[,;:]$/.test(tok.raw)) t += 0.08;
  }
}

function transcriptTimes(file) {
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  const words = (Array.isArray(data) ? data : data.words)
    .filter(w => !w.type || w.type === 'word')
    .map(w => ({ ...w, text: w.text ?? w.word, norm: norm(w.text ?? w.word ?? '') }))
    .filter(w => w.norm);
  // Needleman–Wunsch between script tokens and transcript words.
  const n = tokens.length, m = words.length, GAP = -1;
  const S = Array.from({ length: n + 1 }, () => new Float64Array(m + 1));
  for (let i = 1; i <= n; i++) S[i][0] = i * GAP;
  for (let j = 1; j <= m; j++) S[0][j] = j * GAP;
  for (let i = 1; i <= n; i++) for (let j = 1; j <= m; j++) {
    const match = similar(tokens[i - 1].norm, words[j - 1].norm) ? 2 : -1;
    S[i][j] = Math.max(S[i - 1][j - 1] + match, S[i - 1][j] + GAP, S[i][j - 1] + GAP);
  }
  let i = n, j = m;
  while (i > 0 && j > 0) {
    const match = similar(tokens[i - 1].norm, words[j - 1].norm) ? 2 : -1;
    if (S[i][j] === S[i - 1][j - 1] + match) { tokens[i - 1].start = words[j - 1].start; tokens[i - 1].end = words[j - 1].end; tokens[i - 1].heard = words[j - 1].text; i--; j--; }
    else if (S[i][j] === S[i - 1][j] + GAP) i--;
    else j--;
  }
  // Script words the transcript lacks get a time between their aligned neighbours.
  const lost = [];
  tokens.forEach((tok, k) => {
    if (tok.start != null) return;
    lost.push(tok.raw);
    const prev = tokens.slice(0, k).reverse().find(x => x.start != null);
    const next = tokens.slice(k + 1).find(x => x.start != null);
    const a = prev ? prev.end : 0, b = next ? next.start : a + 0.4;
    tok.start = a + (b - a) * 0.5; tok.end = tok.start + 0.2;
  });
  const misheard = tokens.filter(t => t.heard && norm(t.heard) !== t.norm).map(t => `${t.raw}→${t.heard}`);
  if (lost.length) console.warn(`words the transcript does not have (timed by their neighbours): ${lost.join(', ')}`);
  if (misheard.length) console.warn(`heard differently (check the pronunciation by ear): ${misheard.join(', ')}`);
}

// Captions: one per sentence, long sentences split at the punctuation nearest their middle.
function buildCaptions() {
  const sentences = [];
  let cur = [];
  tokens.forEach((tok, k) => {
    cur.push(tok);
    const next = tokens[k + 1];
    if (/[.?!]["”]?$|\.\.\.$|…$/.test(tok.raw) || !next || next.para !== tok.para) { sentences.push(cur); cur = []; }
  });
  const text = ts => ts.map(t => t.display).join(' ');
  const split = ts => {
    if (text(ts).length <= 58 || ts.length < 4) return [ts];
    const mid = text(ts).length / 2;
    let best = null;
    for (let k = 1; k < ts.length - 1; k++) {
      const pos = text(ts.slice(0, k + 1)).length;
      const score = Math.abs(pos - mid) - (/[,;:—]$/.test(ts[k].raw) ? 14 : 0);
      if (!best || score < best.score) best = { k, score };
    }
    return [...split(ts.slice(0, best.k + 1)), ...split(ts.slice(best.k + 1))];
  };
  const caps = sentences.flatMap(split).map(ts => ({ start: ts[0].start, end: ts[ts.length - 1].end + 0.25, text: text(ts), speaker: ts[0].speaker }));
  caps.forEach((c, k) => { if (caps[k + 1] && c.end > caps[k + 1].start - 0.04) c.end = caps[k + 1].start - 0.04; });
  return caps;
}

const args = process.argv.slice(2);
// --check FILE: only compare a transcript with the script (every word heard?) and change nothing.
if (args[0] === '--check') {
  transcriptTimes(path.resolve(args[1]));
  const heard = tokens.filter(t => t.heard).length;
  console.log(`speech-to-text check: ${heard} of ${tokens.length} script words found in ${path.basename(args[1])}${heard === tokens.length ? '' : ' (see above)'}`);
  process.exit(0);
}
let src = null;
if (args.includes('--placeholder')) src = null;
else if (args[0]) src = path.resolve(args[0]);
else if (fs.existsSync(path.join(DIR, 'timing/words-lead.json'))) src = path.join(DIR, 'timing/words-lead.json');
if (src) transcriptTimes(src); else placeholderTimes();

const r = v => Math.round(v * 1000) / 1000;
const cues = {};
for (const tok of tokens) if (tok.cue) {
  if (cues[tok.cue] != null) console.warn(`cue {#${tok.cue}} is used twice; the first one wins`);
  else cues[tok.cue] = r(tok.start);
}
const balanceQuotes = text => {
  const opens = (text.match(/“/g) || []).length, closes = (text.match(/”/g) || []).length;
  return opens > closes ? text + '”' : closes > opens ? '“' + text : text;
};
const captions = buildCaptions().map(c => ({ start: r(c.start), end: r(c.end), text: balanceQuotes(c.text), speaker: c.speaker }));
const wordList = tokens.map(t => ({ w: t.display, s: r(t.start), e: r(t.end), sp: t.speaker === 'narrator' ? 'n' : t.speaker, sec: t.section, cue: t.cue || undefined }));
const sections = {};
tokens.forEach(t => { const s = sections[t.section] = sections[t.section] || { start: t.start, end: t.end }; s.start = Math.min(s.start, t.start); s.end = Math.max(s.end, t.end); });
Object.values(sections).forEach(s => { s.start = r(s.start); s.end = r(s.end); });
const lastWordEnd = r(tokens[tokens.length - 1].end);
const PROJECT = { title: project.title, style: project.style, fps: project.fps || 30, credits: project.credits || [] };

const out = `// Generated by build_timing.js from script.md (${src ? 'transcript: ' + path.relative(DIR, src) : 'placeholder estimate'}).
// Re-run \`studio timing\` instead of editing this file.
window.PROJECT = ${JSON.stringify(PROJECT)};
window.TIMING = ${JSON.stringify({ source: src ? 'transcript' : 'placeholder', words: tokens.length, lastWordEnd })};
window.SECTIONS = ${JSON.stringify(sections)};
window.CUES = ${JSON.stringify(cues, null, 1)};
window.CAPTIONS = ${JSON.stringify(captions, null, 1)};
window.WORDS = ${JSON.stringify(wordList)};
`;
fs.writeFileSync(path.join(DIR, 'timing.js'), out);
console.log(`timing.js: ${Object.keys(cues).length} cues, ${captions.length} captions, ${tokens.length} words, last word ends at ${lastWordEnd} s (${src ? 'transcript' : 'placeholder'})`);
