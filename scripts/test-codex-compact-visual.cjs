// Offline checks for the Codex compact teaching visual.
// Run: node --test scripts/test-codex-compact-visual.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const filename = path.join(root, 'research/codex_compact_visual.html');
const html = fs.readFileSync(filename, 'utf8');

function script(id) {
  const match = html.match(new RegExp(`<script[^>]*id="${id}"[^>]*>([\\s\\S]*?)<\\/script>`));
  assert.ok(match, `Missing script ${id}`);
  return match[1];
}

const context = vm.createContext({});
vm.runInContext(script('codex-compact-model'), context, { filename });
const viz = context.CodexCompactViz;
const examples = JSON.parse(script('saved-examples'));
const scale = JSON.parse(script('scale-data'));

test('short prefixes copy the transcript instead of folding it', () => {
  const one = viz.build(1, 'dialogue');
  const two = viz.build(2, 'dialogue');
  assert.equal(one.mode, 'replay');
  assert.equal(two.mode, 'replay');
  assert.equal(one.foldedWaves, 0);
  assert.ok(one.compactTokens > one.historyTokens * 0.9);
  assert.ok(one.messages.every(m => m.fate === 'keep'));
  assert.match(one.fragments.map(f => f.text).join('\n'), new RegExp(one.lastSalt));
  assert.match(one.fragments.map(f => f.text).join('\n'), new RegExp(one.firstSalt));
});

test('long prefixes write a pattern note and drop the first unique salt', () => {
  const state = viz.build(54, 'dialogue');
  assert.equal(state.mode, 'pattern');
  assert.equal(state.historyTokens, 54 * viz.WAVE_TOKENS);
  assert.equal(state.historyTokens, 99900);
  assert.equal(state.foldedWaves, 52);
  const body = state.fragments.map(f => f.text).join('\n');
  assert.match(body, /block-and-ack|Code, Math, Config/i);
  assert.match(body, new RegExp(state.lastSalt));
  assert.doesNotMatch(body, new RegExp(state.firstSalt));
  assert.equal(state.messages.find(m => m.id === 'u1-code').fate, 'drop');
  assert.equal(state.messages.find(m => m.id === `u54-dialogue`).fate, 'keep');
  assert.ok(state.compactTokens < 300);
  assert.ok(state.percentIfLossless > state.compactTokens);
});

test('history tokens grow with waves while pattern compact stays on the latest payload', () => {
  const a = viz.build(20, 'dialogue');
  const b = viz.build(80, 'dialogue');
  assert.equal(a.compactTokens, b.compactTokens);
  assert.ok(b.historyTokens > a.historyTokens);
  const json = viz.build(20, 'json');
  const dialogue = viz.build(20, 'dialogue');
  assert.ok(json.compactTokens > dialogue.compactTokens);
});

test('invalid inputs clamp rather than throwing or leaking later waves', () => {
  assert.equal(viz.build(-3, 'dialogue').waves, 1);
  assert.equal(viz.build(400, 'nope').waves, 80);
  assert.equal(viz.build(400, 'nope').lastKindId, 'dialogue');
  assert.equal(viz.build(3, 'json').messages.some(m => m.wave === 3), true);
  assert.equal(viz.build(3, 'json').messages.some(m => m.wave === 4), false);
});

test('saved-case metadata matches the Markdown exports', () => {
  const expected = [
    ['example-1.md', 'cmp-15d33472fc545680ffa49a21', 1127, 1070],
    ['example-2.md', 'cmp-050c26fb0a3c0e45595c2540', 99667, 138],
    ['example-3.md', 'cmp-cdf4ae899afc22275406199b', 398958, 329],
  ];
  assert.equal(examples.length, 3);
  for (let i = 0; i < expected.length; i++) {
    const [file, id, input, compact] = expected[i];
    const text = fs.readFileSync(path.join(root, 'research/compaction-frontier-inspection', file), 'utf8').replace(/\r\n/g, '\n');
    const meta = JSON.parse(text.match(/```json\n([\s\S]*?)\n```/)[1]);
    assert.equal(examples[i].meta.example_id, id);
    assert.equal(examples[i].meta.actual_input_tokens, input);
    assert.equal(examples[i].meta.remote_compact_output_tokens, compact);
    assert.equal(meta.example_id, id);
    assert.equal(meta.actual_input_tokens, input);
    assert.equal(meta.remote_compact_output_tokens, compact);
  }
  const long = fs.readFileSync(path.join(root, 'research/compaction-frontier-inspection/example-2.md'), 'utf8').replace(/\r\n/g, '\n');
  const recovered = long.split('## Complete recovered state\n')[1].match(/^\s*````text\n([\s\S]*?)\n````\s*$/)[1];
  assert.equal(examples[1].recovered, recovered);
});

test('scale table is the inspected master-file band medians', () => {
  assert.deepEqual(scale.map(row => row.median), [663, 724, 697, 934, 852, 690]);
  assert.equal(scale.reduce((n, row) => n + row.n, 0), 2061);
});

test('inline scripts compile, IDs are unique, references resolve, and there are no network dependencies', () => {
  new vm.Script(script('codex-compact-ui'), { filename });
  const markup = html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/g, '');
  const ids = Array.from(html.matchAll(/\bid="([^"\s]+)"/g), m => m[1]);
  assert.equal(new Set(ids).size, ids.length, 'Duplicate element IDs');
  for (const [, id] of script('codex-compact-ui').matchAll(/\$\("([\w-]+)"\)/g)) {
    assert.ok(ids.includes(id), `Unresolvable UI element ${id}`);
  }
  for (const [, attr, target] of markup.matchAll(/\b(aria-controls|aria-labelledby|for)="([^"]+)"/g)) {
    assert.ok(ids.includes(target), `Unresolvable ${attr}: ${target}`);
  }
  for (const [, link] of markup.matchAll(/\bhref="([^"]+)"/g)) {
    assert.ok(fs.existsSync(path.resolve(path.dirname(filename), link)), `Missing local link ${link}`);
  }
  assert.doesNotMatch(html, /<script[^>]*\bsrc=|<link[^>]*\bhref=|@import\s|\bfetch\s*\(|XMLHttpRequest|WebSocket/);
  assert.match(html, /prefers-reduced-motion/);
  assert.match(html, /aria-live="polite"/);
});
