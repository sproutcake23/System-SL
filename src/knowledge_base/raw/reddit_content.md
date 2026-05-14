# Reddit Deep Learning Digest
Generated on: 2026-05-14 11:13:18

# Self Learning | Build a modern LLM from scratch. Every line commented. Explained like we are five.

**Post Author:** u/raiyanyahya  
**Reddit Link:** [View Discussion](https://www.reddit.com/r/deeplearning/comments/1tchmnj/self_learning_build_a_modern_llm_from_scratch)

## External Link
🔗 [Direct Link to Content](https://github.com/raiyanyahya/how-to-train-your-gpt)

## Top Discussions

---

# Most RAG apps in production are confidently wrong and nobody talks about this enough

**Post Author:** u/SilverConsistent9222  
**Reddit Link:** [View Discussion](https://www.reddit.com/r/deeplearning/comments/1tcn9ty/most_rag_apps_in_production_are_confidently_wrong)

## Post Content
Been working with a few teams integrating RAG into internal tools, support bots, document Q&amp;A, contract search, and I keep running into the same thing nobody warns you about when you're following tutorials.

The basic retrieve-then-generate pipeline looks fine in demos. Clean question, clean doc, clean answer. Then real users show up.

The failure mode that gets me is this: the system pulls chunks from different versions of the same policy document, has no way to know they're from different versions, blends them together, and returns an answer with full confidence. No caveat, no "I'm not sure," nothing. Just fluent and wrong.

The deeper issue is that standard RAG has no mechanism for uncertainty. It retrieves, it generates, it moves on, same confidence level whether it nailed it or completely fabricated something plausible.

What actually fixes this (at least in the systems I've worked on) isn't swapping out the model. It's the architecture:

**A routing layer** — decide if retrieval is even necessary before making the call. Some questions don't need it and you're wasting tokens.

**Retrieval scoring** — evaluate what came back before passing it to the model. If the context scores low, reformulate the query and try again instead of just generating garbage confidently.

**A hallucination check** — second LLM call that reads both the generated answer and the retrieved docs and checks if every claim is actually traceable. Most teams aren't doing this and it's probably the highest ROI addition you can make.

The retry loop especially helped in our case because users never phrase questions the way your embedding model expects. The system silently reformulates and retries, user has no idea it happened.

None of this is exotic. It's just a few extra decision points in the pipeline. But if you're running plain RAG in production and wondering why users are losing trust in it, this is almost certainly why.

Curious if anyone else has run into the versioning/context blending issue specifically, that one seems underreported.

## Top Discussions

### Chat #1 by u/SilverConsistent9222
> Did a full breakdown of this with the pipeline diagrams if anyone wants the visual walkthrough: [https://youtu.be/98HaWtfd6ek?si=\_wl1NMHenqlosQIp](https://youtu.be/98HaWtfd6ek?si=_wl1NMHenqlosQIp) covers the four specific failure modes and how the agentic loop addresses each one.

---

# The RTX Pro 6000 Blackwell has 96GB VRAM — here's what that actually unlocks for ML workloads in 2026

**Post Author:** u/dark_Knight_034  
**Reddit Link:** [View Discussion](https://www.reddit.com/r/deeplearning/comments/1tcol1s/the_rtx_pro_6000_blackwell_has_96gb_vram_heres)

## Post Content
Most coverage of the RTX Pro 6000 Blackwell focuses on the spec sheet. Not many people are talking about what 96GB VRAM actually changes for day-to-day ML work.

Here's what it unlocks that wasn't possible before on a single card:

**1. 70B models at full FP16 - no quantization**  
Llama 3.3 70B in FP16 needs \~140GB across two GPUs or heavy INT4 quantization on a single card. With 96GB you're running it unquantized on one card. That's a meaningful quality difference, especially for fine-tuning and eval runs.

**2. Multi-model serving from a single card**  
Load a 7B + 13B model simultaneously and switch between them without cold loading. Useful for pipelines that chain models or need fast A/B comparison.

**3. 128k context without OOM**  
KV cache at 128k context on a 70B model is brutally memory hungry. 96GB makes it practical without tiling tricks.

**4. Full fine-tuning on 34B models - single GPU**  
QLoRA brings this down to \~20GB, but full fine-tuning on a 34B? \~544GB across multiple GPUs normally. With techniques like gradient checkpointing + 96GB you can push closer to single-card fine-tuning on 13B-20B comfortably.

**5. Workstation + inference - same machine**  
It's a PCIe Gen5 workstation card, not a data center card. ECC memory support. Runs rendering pipelines and ML inference simultaneously. Niche but real use case for VFX + AI studios.

The interesting shift: hardware like this used to mean a $6-8k purchase decision. Cloud rental has changed that math — you can now access 96GB VRAM workloads by the hour without the capex commitment.

Curious what workloads people are finding most interesting at this memory range.

My Daily Dose of thoughts on GPU

## Top Discussions

---

# An interesting challenge to squish out as many juice from Qwen2.5 0.5B model

**Post Author:** u/ANR2ME  
**Reddit Link:** [View Discussion](https://www.reddit.com/r/deeplearning/comments/1tc872t/an_interesting_challenge_to_squish_out_as_many)

## Post Content
https://www.h2loop.ai/contests/bear-the-tokens

Someone was able to optimize it to get more than 5k tok/s on a T4 GPU 😯 

## Top Discussions

---

# OpenAI reportedly missed revenue targets. Shares of Oracle and these chip stocks are falling

**Post Author:** u/thisguy123123  
**Reddit Link:** [View Discussion](https://www.reddit.com/r/deeplearning/comments/1tcb1gv/openai_reportedly_missed_revenue_targets_shares)

## External Link
🔗 [Direct Link to Content](https://www.cnbc.com/amp/2026/04/28/openai-reportedly-missed-revenue-targets-shares-of-oracle-and-these-chip-stocks-are-falling.html)

## Top Discussions

---

