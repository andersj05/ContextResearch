// Offline checks for the teaching model, embedded evidence, and HTML wiring.
// Run: node --test scripts/test-compaction-visualizer.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const filename = path.join(root, 'research/compaction_algorithm_visualizer.html');
const html = fs.readFileSync(filename, 'utf8');
function script(id) {
  const match = html.match(new RegExp(`<script[^>]*id="${id}"[^>]*>([\\s\\S]*?)<\\/script>`));
  assert.ok(match, `Missing script ${id}`);
  return match[1];
}
const context = vm.createContext({});
vm.runInContext(script('compaction-model'), context, { filename });
const model = context.CompactionModel;
const examples = JSON.parse(script('saved-examples'));

test('all 24 walkthrough states preserve valid source-to-checkpoint provenance', () => {
  for (const answered of [false, true]) {
    for (const keep of [false, true]) {
      for (let step = 0; step < model.stages.length; step++) {
        const state = model.build(step, answered, keep);
        const ids = new Set(state.messages.map(m => m.id));
        assert.equal(state.messages.length, answered ? 7 : 6);
        assert.equal(new Set(state.fragments.map(f => f.id)).size, state.fragments.length);
        for (const fragment of state.fragments) {
          assert.ok(fragment.sources.length);
          for (const id of fragment.sources) assert.ok(ids.has(id), `Unresolvable source ${id}`);
        }
        assert.equal(state.complete, step === 5);
      }
    }
  }
});

test('an already answered request is never presented as an action to repeat', () => {
  const finished = model.build(5, true, true);
  assert.match(finished.fragments.find(f => f.id === 'turn').text, /Awaiting user/);
  assert.match(finished.fragments.find(f => f.id === 'next').text, /Do not repeat/);
  const pending = model.build(5, false, true);
  assert.match(pending.fragments.find(f => f.id === 'turn').text, /Response pending/);
  assert.match(pending.fragments.find(f => f.id === 'next').text, /^Acknowledge retry_limit=5/);
  assert.ok(!pending.messages.some(m => m.id === 'm7'));
});

test('superseded settings are discarded while enduring constraints remain', () => {
  const state = model.build(5, true, true);
  assert.equal(state.messages.find(m => m.id === 'm2').state, 'drop');
  assert.equal(state.messages.find(m => m.id === 'm1').state, 'keep');
  assert.match(state.fragments.find(f => f.id === 'setting').text, /retry_limit=5/);
  assert.match(state.fragments.find(f => f.id === 'constraint').text, /do not change production/);
  assert.equal(state.messages.find(m => m.id === 'm5').state, 'merge');
});

test('disabling obligation preservation removes the exact key from the checkpoint', () => {
  const kept = model.build(5, true, true);
  const lost = model.build(5, true, false);
  assert.match(kept.fragments.map(f => f.text).join('\n'), /LARCH-72/);
  assert.doesNotMatch(lost.fragments.map(f => f.text).join('\n'), /LARCH-72/);
  assert.equal(lost.messages.find(m => m.id === 'm3').state, 'lost');
  assert.match(lost.fragments.find(f => f.id === 'next').text, /Wait for/);
});

test('stepping backward rebuilds state without leaking later fields or mutating the source', () => {
  const final = model.build(5, true, true);
  final.messages[0].text = 'modified';
  assert.equal(model.build(0, true, true).fragments.length, 0);
  assert.equal(model.build(1, true, true).fragments.length, 1);
  assert.match(model.build(5, true, true).messages[0].text, /staging/);
  assert.equal(model.build(-1, true, true).step, 0);
  assert.equal(model.build(100, true, true).step, 5);
});

test('all saved source messages, full recovered strings, and metadata match the Markdown exports', () => {
  assert.equal(examples.length, 3);
  for (let i = 0; i < examples.length; i++) {
    const text = fs.readFileSync(path.join(root, `research/compaction-frontier-inspection/example-${i + 1}.md`), 'utf8').replace(/\r\n/g, '\n');
    const [source, recovered] = text.split('## Complete recovered state\n');
    const meta = JSON.parse(source.match(/```json\n([\s\S]*?)\n```/)[1]);
    const messages = Array.from(source.matchAll(/### (user|assistant)\n\n````text\n([\s\S]*?)\n````/g), m => ({ role: m[1], text: m[2] }));
    const checkpoint = recovered.match(/^\s*````text\n([\s\S]*?)\n````\s*$/)[1];
    assert.deepEqual(examples[i], { meta, messages, recovered: checkpoint });
    assert.equal(messages.length, 4);
  }
});

test('echo correction and length errors reproduce every saved case', () => {
  for (const { meta } of examples) {
    const score = model.score(meta.advanced_adjusted_tokens + 6, meta.remote_compact_output_tokens);
    assert.equal(score.adjusted, meta.advanced_adjusted_tokens);
    assert.equal(score.delta, -4);
    assert.ok(Math.abs(score.error / 100 - meta.advanced_token_error) < 1e-8);
    assert.equal(model.score(meta.remote_compact_output_tokens + 6, meta.remote_compact_output_tokens).error, 0);
  }
  assert.equal(model.score(6, 138).error, 100);
  assert.equal(model.score(282, 138).error, 100);
  for (const pair of [[5, 138], [140, 0], [NaN, 138], [140, Infinity]]) {
    assert.throws(() => model.score(...pair), /Expected billed tokens/);
  }
});

test('inline scripts compile, IDs are unique, references resolve, and there are no network dependencies', () => {
  new vm.Script(script('compaction-ui'), { filename });
  const markup = html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/g, '');
  const ids = Array.from(html.matchAll(/\bid="([^"\s]+)"/g), m => m[1]);
  assert.equal(new Set(ids).size, ids.length, 'Duplicate element IDs');
  for (const [, id] of script('compaction-ui').matchAll(/\$\("([\w-]+)"\)/g)) {
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
