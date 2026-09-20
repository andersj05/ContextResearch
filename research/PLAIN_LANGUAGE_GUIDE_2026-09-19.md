# What this research is trying to find out

September 19, 2026. The 1,536-request study is complete. This guide explains what we have learned and what remains uncertain. The detailed model results are in the [completed-study findings](TRANSFER_LUNA_FINDINGS_2026-09-19.md).

The central question is: **How should an AI decide what to remember before it knows what it will need later?** We study repeated memory decisions as instructions arrive and memory shrinks.

Imagine handing a project to a colleague. Six jobs each produced a confirmation code, but your colleague can carry only two records. Later, they learn which two jobs might need approval, then which exact code to present. “All six jobs finished” cannot supply a missing code.

You could keep more information, find out what will matter before discarding anything, or recover a missing record afterward. The best choice depends on timing and cost. If someone will reliably resend a record later, scarce memory may be better spent on information that will not arrive again.

## The small mathematical example

We started with four yes/no facts. The system sees them, makes a small memory, then learns which three facts might matter. It makes an even smaller memory before learning which single fact to answer. All fact patterns and allowed questions are equally likely. Each stage can use only the memory passed forward and the public instructions revealed so far; it cannot reread an older memory or the original facts.

With two bits of initial memory followed by one bit, the best possible average error is **9/32, or 28.125%**. If the later compressor can reread the original facts before making its one-bit memory, its best error is **1/4, or 25%**. Allowing three initial bits also restores 25%.

The extra loss is **3.125 percentage points**. This is an exact result within this tiny problem, established through a complete computer search and checked examples. Even the best permitted strategy suffers from the earlier restriction. It is not a measured error rate for an AI product. [Exact result](EXACT_CHAIN_OPTIMUM_2026-09-19.md)

A bit is one yes/no storage unit. Two bits can encode four different messages, including messages about relationships between facts. A record slot instead holds one whole record, including its identifier and code. Two bits and two record slots are very different memory allowances. Model tokens are yet another unit: pieces of text processed by the model.

We also have a locally checked proof for many four-fact pieces, with two initial bits per piece and a final one-bit memory after one piece is selected. The extra error cannot disappear by encoding the pieces together, although the exact 3.125-point penalty does not automatically carry over. External proof review and priority assessment remain open. The mathematical methods have established predecessors; what may be new is the particular construction and result. [Proof review](PROOF_AUDIT_2026-09-18.md), [literature check](SCALING_LITERATURE_CHECK_2026-09-19.md)

## The practical testing environment

We then built a controlled handoff environment. An agent selects whole records, encounters later instructions and updates, and eventually needs an exact code. We calculate how different choices should work. This tests a related practical question under different rules; it does not test the bit theorem directly.

Remembering better is not always cheaper. In the six-job example without updates, suppose checking which two jobs might matter costs one unit. Saving both then avoids recovery. Without checking, the required code is missing two-thirds of the time. If recovery costs one unit, its average cost is two-thirds of a unit. If it costs four, checking first is cheaper. These are invented action-cost units, not dollars or token savings. [Recovery results](../experiments/dependency_memory/results/recovery_frontier_report.md)

The 810 record-policy configurations and thousands of scripted episodes are software checks, not independent AI trials. They expose a measurement trap: if recovery always works, even an agent that forgets everything can finish. We therefore measure availability **before optional recovery**, as well as completion cost. A scheduled update can supply the code; availability does not necessarily mean the original record survived.

## The earlier model experiments

Before the larger study, we completed **120 Luna requests** in two separate experiments. These are historical observations, additional to the new study.

The first used 96 requests, including 36 workflow episodes. All finished, but 15 needed recovery. Rechecking the saved selections found three early choices below the best availability reference, involving the update rule. Every observed later selection was optimal given what remained. [First findings](LUNA_DEVELOPMENT_FINDINGS_2026-09-19.md)

The next 24 requests used a simpler task. Every selection was optimal, including when the update direction reversed. Wording and the promised later-selector skill also changed, so this did not show that the earlier mistakes were fixed. [Follow-up findings](REVISION_LUNA_FINDINGS_2026-09-19.md)

## The completed larger study

The study sent **1,536 requests and obtained 1,533 valid answers**. Three responses were lost and remain missing. It used six or twelve jobs and varied task wording, guidance, later-selector guarantees, and update direction. Public refresh priorities were assigned independently of job names, and display order was shuffled. The model had to follow those priorities when deciding which records might arrive again.

There were 48 conditions within each of 32 generated task sets. Matched conditions shared materials, allowing comparisons without changing the underlying records. These were controlled tasks, not 1,536 real-world projects. [Study protocol](../docs/TRANSFER_STUDY.md)

Across all valid answers, **1,422 selections were optimal and 111 were below the best achievable availability**. “Optimal” means best under the stated limits; it does not guarantee success on every later query. Each choice was scored over every possible candidate pair and final target, rather than judged from one lucky or unlucky continuation.

The main comparison asked whether a reminder to consider future information arrivals helped in the fuller workflow description. Across **128 matched comparisons**, generic guidance produced **114 optimal selections**, while the future-information reminder produced **118**. The estimated overall advantage was small, and the uncertainty range included no improvement. We therefore have **not established a guidance benefit**. The individual mistakes are still useful examples to investigate.

This study tests the first retention choice. The later selector was represented by an ideal reference, not another model call. Two candidate records fit in its two slots, so the second boundary does not force it to discard an available candidate. This differs from the mathematical example, where the second memory limit is binding. It also means the results measure the potential supplied by a selection, not demonstrated performance of a complete agent. [Completed findings](TRANSFER_LUNA_FINDINGS_2026-09-19.md)

## Our current understanding and next steps

Early forgetting can impose an unavoidable penalty in a precisely defined problem. In the record tasks, the model usually chooses well, but some choices leave avoidable gaps. The tested reminder has not yet shown a reliable improvement.

Next we need external mathematical review, clearer priority assessment, and experiments where later memory decisions also matter. Realistic agent tests must include recovery and cost. Better native compaction, real-world savings, and general superiority remain unproved.
