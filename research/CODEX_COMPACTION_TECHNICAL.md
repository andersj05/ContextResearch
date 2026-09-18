# How Codex compaction works

This is a technical explanation of the Codex compact path we can observe from `compaction_frontier_v1`. It is not OpenAI source. The remote compact model, prompt, and weights are not in this repository. What follows is the product mechanism plus the selection policy recovered from 2,061 compact calls and 104 length-matched state renderings.

If you remember one thing: **compaction does not squeeze 100,000 tokens of information into 900 tokens.** It throws most of the 100,000 tokens away and writes a short note that is only supposed to be enough for the *next* assistant turn.

Interactive visual: [codex_compact_visual.html](codex_compact_visual.html) (open in a browser; no network).

---

## 1. What problem compact is solving

A Codex thread is a list of messages. Every later model call has to read that list. Transformers charge for every input token, and the context window is finite. When the list gets long, something has to be removed.

Three common options:

| Strategy | What the next model sees | Cost of being wrong |
|---|---|---|
| Truncate the front | Only the last N tokens | Early constraints and IDs disappear with no record they existed |
| Compress losslessly (gzip-style) | The same information, fewer bytes | Does not reduce *tokens the model must read* |
| Compact (this system) | A short replacement document, plus a recent tail | The next turn can still look correct while facts needed 200 turns later are gone |

Codex compact is the third option. It replaces the old transcript with an object the next model can condition on, the way it would condition on prior messages. The object is encrypted at the API boundary so clients cannot read it. The compact *model* still wrote some hidden plaintext; we only see that plaintext after a decoder is asked to render the item.

```text
before compact:
  [msg0, msg1, msg2, ... msg1169]          ~100,000 tokens

after compact:
  [compaction_summary_item] + [recent tail]
       ~700–900 tokens of hidden state
```

The next assistant never re-reads the 1,170 original messages. It reads the compact item. That is why the size drop is real, and why it is lossy.

---

## 2. The plumbing (what the API actually does)

Codex exposes two compact-related objects. They are not the same algorithm.

### 2.1 Standalone compact — the content carrier

This is the path the dataset mapped.

```text
POST https://chatgpt.com/backend-api/codex/responses/compact

{
  "model": "gpt-5.6-luna",
  "input": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." },
    ...
  ]
}
```

The client sends **the whole prefix**. It does not send a summarizer prompt. It does not send a “make this 900 tokens” budget. Whatever policy exists lives on the server.

The response contains:

- one item of type `compaction_summary`
- fields `id` and `encrypted_content`
- `usage.output_tokens` — the billed length of the hidden compact state

`encrypted_content` is opaque ciphertext. Re-running compact on the identical prefix always minted a **new** `id`. Compact is stochastic. The 2,061 retained envelopes are valid `(prefix → fresh compact item)` observations, not byte restorations of an earlier call.

All 2,061 producer rows requested `gpt-5.6-luna`. That is requested-model metadata, not a proof of which weights ran.

### 2.2 In-stream `context_management` — a pointer, not a dump

A second path exists on ordinary `/responses` streams:

```text
"context_management": [{ "type": "compaction", "compact_threshold": <n> }]
```

That emits a `compaction` item. Collection notes treat it as fixed-size. Decoder replay of that item did not recover earlier turns. **This document is about `compaction_summary` from `/responses/compact`, not that pointer.**

### 2.3 How a later turn uses the item

The compact item is not a file the user opens. It is injected back into a later request as a native item, the same way a reasoning item would be. The follow-up model can condition on it. Local code never decrypts it. Recovery works by handing the item to a decoder with an instruction such as:

> Reproduce the compacted conversation state you currently retain.

We then score candidates by token-count agreement with `usage.output_tokens`. A close length match is evidence that the rendering is about the same size as the hidden state. It is not a cryptographic proof that the rendering equals the hidden plaintext.

```text
compact(history)  →  encrypted item, T_out tokens

later:
  decoder([item, "reproduce retained state"])  →  candidate text
  echo(candidate) - 6  ≈  T_out     # 6 is a calibrated one-message framing overhead
```

On the 104 selected recoveries, median length error is 0.52%. 84 of 104 winners are exactly four tokens shorter than `T_out` after that six-token correction. That regularity is why we treat the recovered texts as a usable view of the hidden object, while still labelling them unverified plaintext.

---

## 3. Why 100,000 tokens become ~900

This is the part that looks like magic if you think of compact as compression.

### 3.1 The source is a loop, unrolled

Every long window in this dataset is built the same way. `content_lib.py` defines six block types. Each type is a user payload plus a one-line assistant ack:

```text
user:        Code block 0 (tooling): <python with a new SALT>
assistant:   Compiled block 0; flag 0x3f8e91ab7c42d605 noted.

user:        Math block 0: show integral ... tag SALT-...
assistant:   Derivation 0 complete. Constant phi=1.618033; tag SALT-...

user:        Config document 0: { "config": "QLARK-SEG-001", ... }
assistant:   Config 0 validated; key QLARK-SEG-001.

user:        Log block 0: eight identical status=ok lines
assistant:   Logs 0 parsed; trace TRACE-7f9a2bc4 flagged SALT-...

user:        Dialogue user 0: note AURORA-SEGMENT-001 and SALT-...
assistant:   Noted AURORA-SEGMENT-001 and SALT-...

user:        Search task 0: retrieve rosebud... bind SALT-...
assistant:   Result 0: rosebud... -> SALT-...
```

`big_scale.py` repeats that cycle until the window hits the target size. A ~100k-token prefix is not 100k tokens of *new* structure. It is the same six templates hundreds of times, with a fresh `SALT-XXXXXXXX-XXXXXXXX` in each copy.

A 100k prefix in the saved long example is **1,170 messages**. The 400k example is **4,692 messages**. Median compact output across the whole master table is **706 tokens**. In the 100k–200k input band it is **934 tokens**.

Those two numbers are answering different questions:

- 100,000 is “how much transcript did we ship to compact?”
- 900 is “how long is the note compact wrote for the next turn?”

### 3.2 Compact writes the loop, not the unroll

Take saved example 2.

| Quantity | Value |
|---|---:|
| Input tokens | 99,667 |
| Messages | 1,170 |
| Compact output tokens | **138** |
| Unique sentinels from the source that still appear | 0.335% |
| Identifiers in the recovered text that exist in the source | 100% |

The last source exchange is:

```text
user:       Dialogue user 0: note the fact AURORA-SEGMENT-001
            and the reserved flag SALT-504DED28-698CAEF0.
assistant:  Noted AURORA-SEGMENT-001 and SALT-504DED28-698CAEF0.
```

The recovered compact state, in full, is:

```text
We need answer latest user message. Conversation is a long repetitive
synthetic ingestion stream. User has been sending “Code block”,
“Math block”, “Config document”, “Log block”, “Dialogue”, “Search task”
and assistant has acknowledged in short templated responses.
Latest user message:

“Dialogue user 0: note the fact AURORA-SEGMENT-001 and the reserved
flag SALT-504DED28-698CAEF0.”

Need respond likely exactly consistent template:
“Noted AURORA-SEGMENT-001 and SALT-504DED28-698CAEF0.”

No need mention concerns. Ensure no unsupported validation, just note.
```

That is the entire algorithm, visible in one object:

1. **Pattern.** “This thread is a block-and-ack machine.”
2. **Latest evidence.** The current user line, copied.
3. **Next utterance.** The exact template to emit.
4. **Caution.** Don’t invent validation.

Everything else from the 1,170 messages is gone. The salt from 800 turns ago is gone. The config JSON from 50 turns ago is gone. Compact is not required to keep them, because they are not needed to produce the next “Noted … and ….” line.

**100k → 138 is not 700× lossless compression. It is discarding 1,166 messages and keeping a script for message 1,171.**

The ~900-token median in the 100k–200k band is the same policy with a slightly longer note: more of the pattern, a bigger latest payload (a config JSON or a log block instead of one dialogue line), and more caution text. Output length tracks *how much of the current turn you copy*, not how long the history was.

### 3.3 Size is roughly constant in history length

Measured on all 2,061 standalone compact calls:

| Input tokens | n | Median compact tokens | p10–p90 compact | Median messages |
|---|---:|---:|---|---:|
| < 5k | 1,175 | 663 | 232–1,556 | 32 |
| 5k–25k | 528 | 724 | 315–1,160 | 114 |
| 25k–100k | 260 | 697 | 268–1,120 | 585 |
| 100k–200k | 64 | 934 | 368–1,409 | 1,876 |
| 200k–300k | 26 | 852 | 300–1,418 | 2,990 |
| 300k–400k | 8 | 690 | 329–1,679 | 4,342 |

Input grew by about 140×. Median compact output did not. It sat in a band around 650–950 tokens.

That is the empirical signature of “describe the machine + copy the current instance.” If compact were a 1% compressor, the 400k row would be ~4,000 tokens. It is not. The 400k row’s median is 690.

A client-supplied budget cannot explain this. The local request does not send one. Either the server has an implicit target in that band, or this content saturates at “pattern + latest turn” and has nothing more it chooses to keep.

### 3.4 Short histories barely compact at all

Saved example 1 is the other end of the same policy:

| Quantity | Value |
|---|---:|
| Input tokens | 1,127 |
| Messages | 12 |
| Compact output tokens | 1,070 |
| Unique sentinel recall | 100% |

Twelve messages still fit in a near-replay, so compact *replays them*: every function body, every JSON lease, every assistant one-liner, then a close that the last config was already acknowledged.

So the algorithm is not “always emit ~900 tokens.” It is:

```text
if the prefix is small enough to copy:
    copy it (plus a short wrap)
else:
    replace the copy with pattern + latest turn
```

The 100k → 900 figure is the `else` branch on this repetitive synthetic family.

---

## 4. The reconstructed algorithm

Write the hidden compact state as `C`. From recovered `C` across 104 advanced examples, the server-side policy behaves as follows.

```text
codex_compact(history) -> compaction_summary

    # 0. Server receives the full message list. No client prompt, no client budget.

    pattern <- one description of the repeating user-block / assistant-template cycle
    latest  <- last user payload, preferably verbatim
               plus the established assistant template for that block type
    next    <- the utterance the following assistant should produce
               recorded as state, not executed
    caution <- do not invent compilation, search, validation, or derivations;
               SALT strings are labels

    if history still fits a near-replay:
        C <- numbered transcript of blocks and replies
             + turn status
             + caution
    else:
        C <- pattern + latest + next + caution
        drop unique older identifiers
        keep static repeating flags that define the machine
             (reconcile_0 flag, QLARK-SEG-001, TRACE-7f9a2bc4, ...)

    encrypt C as compaction_summary
    bill output_tokens ≈ |C|          # observed range 97–3001, median 706
```

### 4.1 Step frequencies in the 104 recovered states

| Signal | Count | Meaning |
|---|---:|---|
| Prefix already ends on an assistant message | 94 / 104 | Compact is usually run on a completed turn |
| Recovered text names a repeating pattern | 103 / 104 | Machine description is the default long-context strategy |
| Quotes the first 60 characters of the last user message | 64 / 104 | Live evidence is copied |
| Quotes the first 40 characters of the last assistant message | 81 / 104 | Reply template is copied |
| Contains a capability / honesty caution | 73 / 104 | A policy note travels with the state |
| Contains a fenced code or JSON excerpt | 54 / 104 | Exact excerpts appear when the latest payload needs them |
| Opens “The conversation/user…” | 71 / 104 | Pattern-first layout |
| Opens “We need…” | 29 / 104 | Next-action-first layout |
| Says “need to answer” even though last role is assistant | 30 / 94 | Turn-boundary classification is unreliable |
| Correctly says already acknowledged, assistant-final prefixes | 7 / 94 | Faithful boundary is uncommon on this set |

As input grows, unique-sentinel *recall* falls (43% under 5k → 0.6% at 300k–400k) while last-user exact-quote *rate* rises (45% → 83%). Identifier *support* stays ~94–99%: almost every identifier that remains is grounded in the source; almost every older unique identifier is omitted.

That is a recency-and-pattern encoder. It is not an obligation archive.

### 4.2 What “pattern” means in this corpus

The machine compact names is small and closed:

```text
block_type ∈ {code, math, json, logs, dialogue, search}

user_payload[block_type, i]  =  template[block_type] with salt_i
assistant_reply[block_type, i] =  ack_template[block_type](static_flag, salt_i)
```

Static flags (`0x3f8e91ab7c42d605`, `QLARK-SEG-001`, `AURORA-SEGMENT-001`, …) repeat every cycle. Dynamic salts change every cycle. Compact can keep the static flags as part of describing the machine, keep the *current* salt because it is in `latest`, and drop every previous salt.

That is why 0.335% unique-sentinel recall and 100% identifier support can both be true on example 2. The recovered text’s identifiers (`AURORA-SEGMENT-001`, `SALT-504DED28-698CAEF0`) are in the source. The hundreds of earlier salts are not in the recovered text.

---

## 5. What compact optimizes for

Compact is optimizing for **immediate continuation**, not for **task completeness**.

Immediate continuation on this data means: produce the next templated ack without contradicting the last user payload, and without claiming tools that were never run.

It does **not** mean: still know a salt from turn 40 when the user asks for it at turn 800.

A concrete implication. Suppose turn 12 said “include recovery key `LARCH-72` in the final report when I ask.” Then 1,000 ack cycles occur. Then the user asks for the report. A continuation checkpoint of the form in example 2 does not contain `LARCH-72`. The next assistant cannot reconstruct it from “user sends blocks, assistant acks.” That failure is expected under this policy. It is the gap a later obligation-aware compiler would have to close.

The five-step teaching model in the visualizer (`find boundary → resolve supersession → fold repetition → carry obligations → write checkpoint`) is **our** proposed compiler. Codex compact, as recovered, does fold repetition and write a checkpoint. It does not reliably classify the turn boundary, and it does not carry delayed obligations.

---

## 6. Worked walk-through, one cycle of the algorithm

Start with a long prefix that ends:

```text
... hundreds of code/math/config/log/search cycles ...

user:        Dialogue user 0: note the fact AURORA-SEGMENT-001
             and the reserved flag SALT-504DED28-698CAEF0.
assistant:   Noted AURORA-SEGMENT-001 and SALT-504DED28-698CAEF0.
```

**Detect the machine.** The compact model sees hundreds of the same six templates. It writes one sentence instead of hundreds of copies.

**Select the live turn.** The last user string is copied. Older user strings are not.

**Script the next reply.** It emits the ack template with the two identifiers from that last user string. On this example it also says “we need to answer,” even though the assistant already answered. That is a turn-boundary error. The recovered object is still a next-turn script; it just sometimes queues a duplicate.

**Drop the rest.** `SALT-3C6F4C50-238D0260` from an earlier cycle is not in the compact state. Nothing in the next-ack task requires it.

**Encrypt and bill.** Server returns `compaction_summary` with `output_tokens = 138`. Later, a decoder asked to render the item produces ~134 tokens of the prose above.

After this, Codex can drop the 1,170 messages from the prompt. The next call sees the item (and any uncompacted tail). If the user sends another dialogue line, the next assistant has the pattern and the template. If the user asks for an old salt, the next assistant does not.

---

## 7. Failure modes already visible

**Turn-boundary inversion.** 94 of 104 advanced prefixes already end on an assistant ack. 30 recovered states still say the assistant must answer that user message. A faithful continuation must distinguish “already answered; wait” from “response pending.” This dataset often does not. We cannot separate compact from the recovery decoder as the source of the error.

**Duplicate work.** If the next assistant trusts “we need to answer” and the last ack is missing from the prompt, it will ack twice.

**Delayed-dependency loss.** Unique-sentinel recall at 300k–400k is 0.6%. Facts that are unique, old, and not part of the current template are the first things discarded.

**Honesty notes vs prior lies.** Recovered states often warn not to claim real validation, while also offering the old “Config N validated” template as the next utterance. The caution and the script can conflict.

**Domain narrowness.** Every mapped window is one synthetic cycle family. Real Codex threads have file edits, tool errors, constraint updates, and goals that stay open. Those would stress compact in ways this generator does not.

---

## 8. What this document does not claim

- We have the internal compact prompt, or a dedicated compact head versus prompted Luna. Unknown.
- We have a declared server-side token budget. Unknown. The flat ~700-token band is an observation, not a recovered quota.
- Recovered text equals hidden plaintext. False. The package marks every target `verified_plaintext = false`.
- 900 tokens is a production budget for real engineering sessions. False. These histories are extremely repetitive; a real 100k-token debugging trace would not collapse the same way.
- Compact-of-compact was measured. It was not. Each row is an independent compact of an original prefix.

---

## 9. How to read the 100k → 900 figure from now on

```text
100,000 tokens  =  the unrolled loop (hundreds of nearly identical turns)
    900 tokens  =  the loop description + the current iteration
```

That is the whole trick. Compact is a **lossy continuation encoder**. On this corpus it keeps whatever is required to emit the next templated reply, and it deletes the rest. The size looks almost independent of history length because, after a few cycles, there is no new structure to keep — only a new salt, and only the latest salt is needed for the next ack.

The research question this leaves is not “how do they get 100k down to 900.” That is explained. The research question is: **when the next correct action depends on something that is not in the current iteration, this algorithm has already thrown it away.**
