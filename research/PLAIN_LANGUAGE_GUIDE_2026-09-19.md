# What this research is trying to find out

September 19, 2026. The 1,536-request study is ongoing. This guide explains the completed work; the study's provisional results are in a [separate checkpoint note](TRANSFER_LUNA_FINDINGS_2026-09-19.md).

The central question is: **How should an AI decide what to remember before it knows what it will need later?** We study repeated memory decisions as instructions arrive and memory shrinks.

Imagine handing a project to a colleague. Six jobs each produced a confirmation code, but your colleague can carry only two records. Later, they learn which two jobs might need approval, then which exact code to present. “All six jobs finished” cannot supply a missing code.

There are several ways to handle this. Keep more information. Find out what will matter before discarding anything. Or recover a missing record afterward. The best choice depends on when information arrives and what each action costs. If someone will reliably resend a record later, scarce memory may be better spent on information that will not arrive again.

## The small mathematical example

We started with four yes/no facts. The system sees them, makes a small memory, then learns which three facts might matter. It makes an even smaller memory before learning which single fact to answer. All fact patterns and allowed questions are equally likely. Each stage can use only the memory passed forward and the public instructions revealed so far; it cannot reread an older memory or the original facts.

With two bits of initial memory followed by one bit, the best possible average error is **9/32, or 28.125%**. If the later compressor can reread the original facts before making its one-bit memory, its best error is **1/4, or 25%**. Allowing three initial bits also restores 25%.

The extra loss is therefore **3.125 percentage points**: 28.125 minus 25. It is not “3%,” and it is not a measured error rate for an AI product. It is an exact result within this tiny problem, established through a complete computer search and checked examples. Even the best permitted strategy suffers from the earlier restriction. [Exact result](EXACT_CHAIN_OPTIMUM_2026-09-19.md)

A bit is one yes/no storage unit. Two bits can encode four different messages, including messages about relationships between facts. A record slot instead holds one whole record, including its identifier and code. Two bits and two record slots are very different memory allowances. Model tokens are yet another unit: pieces of text processed by the model.

We also have a locally checked proof for many four-fact pieces. Initial memory is limited to two bits times the number of pieces. A later instruction selects one piece; the final memory still holds one bit. Under those rules, the extra error cannot disappear by encoding the pieces together. The proof needs external review and a fuller comparison with existing research. The exact 3.125-point penalty does not automatically carry over. Whether such effects matter substantially in ordinary AI work remains a separate hypothesis. [Proof review](PROOF_AUDIT_2026-09-18.md)

## The practical testing environment

We then built a controlled handoff environment. An agent selects whole records, encounters later instructions and updates, and eventually needs an exact code. We calculate how different choices should work. This tests a related practical question under different rules; it does not test the bit theorem directly.

Remembering better is not always cheaper. In the six-job example without updates, suppose checking which two jobs might matter costs one unit. Saving both then avoids recovery. Without checking, the required code is missing two-thirds of the time. If recovery costs one unit, its average cost is two-thirds of a unit. If it costs four, checking first is cheaper. These are invented action-cost units, not dollars or token savings. [Recovery results](../experiments/dependency_memory/results/recovery_frontier_report.md)

The 810 record-policy configurations and thousands of scripted episodes are software checks, not independent AI trials. They expose a measurement trap: if recovery always works, even an agent that forgets everything can finish. We therefore measure whether the required current code is available before optional recovery, and what completion costs. A scheduled update can supply that code: availability does **not** mean it survived the original memory.

## What the model experiments have shown

Before the ongoing study, we completed **120 Luna model requests**. These were two different experiments, not 120 complete real-world projects.

The first used 96 requests. It included 36 workflow episodes, all of which finished. The required code was available before recovery in 21; the other 15 needed recovery. Rechecking the saved selections found three early choices below the best availability reference, all involving the public update rule. Every observed later selection was optimal given what remained. This identifies behavior, without revealing why the model chose it. [First findings](LUNA_DEVELOPMENT_FINDINGS_2026-09-19.md)

The next 24 requests used a simpler task and reversed which candidate would receive an updated record. The model chose an optimal pair every time and changed its choices appropriately when the rule reversed. However, the simpler wording and a guaranteed optimal later selector also changed the task. We have shown that it can respond correctly in those conditions; we have not shown that the earlier workflow mistakes were fixed. “Optimal” means best under the memory limits, not that every later request can be answered. [Follow-up findings](REVISION_LUNA_FINDINGS_2026-09-19.md)

## What is happening now, and what remains

The ongoing study compares guidance, framing, later-selector guarantees, six versus twelve jobs, and update direction on matched inputs. It schedules **1,536 requests: 48 conditions in each of 32 generated blocks**. Conditions within a block share underlying materials. Those 32 blocks are constructed task sets, not 32 independent natural-world tests. The main question is whether guidance about future information arrivals helps retention in the fuller task description. A clear benefit, no benefit, or worse performance would each be informative. [Study protocol](../docs/TRANSFER_STUDY.md)

We have a mathematical foundation, a reproducible testing environment, and specific model observations. We still need external proof review, a defensible account of what is new, and realistic agent evidence. Better native compaction, real-world cost savings, and general superiority remain unproved.
