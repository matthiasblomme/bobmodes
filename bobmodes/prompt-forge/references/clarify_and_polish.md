# Clarify and polish reference

Everything the spine needs during the clarify and structure stages: the clarify question
bank, the gating rules that stop clarification becoming an interrogation, the task-spec
template, and the optional voice and anti-AI passes.

---

## Clarify question bank, by dimension

Pull from these. Include only the questions whose answer would actually change the prompt.
Rephrase them to the user's material - do not read the bank aloud.

| Dimension | The questions to consider |
|---|---|
| **Goal** | What is the single outcome? What does the user do with the result? What would make this a failure? |
| **Audience** | Who reads the output - the user, an end user, a machine? What do they already know? |
| **Scope** | What is explicitly in, and what is out? How big is one run (one item, a batch, an ongoing job)? |
| **Inputs** | What material does the model get? What form is it in? Is it pasted, referenced, or fetched? Can it be missing or malformed? |
| **Output format** | Prose, list, table, JSON, code, a file? How long? Any fixed template or schema? |
| **Constraints** | Hard rules, tone, things to avoid, length caps, forbidden actions? |
| **Success criteria** | How does the model know it did well? Is there a checkable property ("valid JSON", "under 200 words", "cites a source per claim")? |
| **Edge cases** | Empty input, ambiguous input, conflicting instructions, out-of-scope requests - what should happen? |

Aim for **three sharp questions**, not ten generic ones. The dimensions most often left
vague in a brain dump are output format, success criteria, and edge cases - start there.

### Gating rules (when NOT to ask)

**Run the gate before opening the question bank, not after.** The bank is a menu of what
*could* be unclear; the gate decides whether you are allowed to ask at all.

- **Hard gate:** if the material already contains goal, inputs, and output shape, asking is
  a rule violation, not a judgement call - even when good questions exist. Field semantics,
  edge-case behaviour, and format details are defaultable, never askable, once those three
  are present: pick the sensible default, state it as a named assumption, produce the
  prompt. The user corrects a wrong default in the iterate round for free; a question round
  always costs them a turn.
- The user has explicitly said "just make something reasonable" or is clearly in a hurry:
  same treatment, default and state.
- Below the hard gate, still prefer defaults: reserve questions for real forks where the
  wrong guess produces a structurally different prompt and wastes the user's time.

Never ask a question whose answer you could infer from the material with reasonable
confidence. Asking to offload your own thinking is the failure mode this gate exists to stop.

---

## Task-spec template

Assemble the answers into this before writing the final prompt. It is scaffolding for you,
not necessarily the literal shape of the prompt (the model profile decides how much of it
survives into the prompt text).

```
GOAL:        <the one outcome>
CONTEXT:     <background the model needs and would otherwise invent>
TASK:        <the request, stated once>
INPUTS:      <what it works on / where the material appears>
CONSTRAINTS: <hard rules; do X not Y; length; tone; forbidden actions>
OUTPUT:      <exact shape of the answer>
SUCCESS:     <how "done well" is checked>
EXAMPLES:    <0-3, if format or judgement is non-obvious>
APPROACH:    <optional suggested steps, if the path is non-obvious and the model wants them>
```

Then hand the spec to [`model_tuning.md`](model_tuning.md) to render it into the final,
model-shaped prompt.

---

## Optional pass: voice

When the user wants the eventual output to sound like them (or like a specific target
voice), bake a voice instruction into the prompt. This skill only *writes the instruction*;
it does not do the writing itself.

- **Keep the instruction concrete.** A vague "write in my voice" does nothing for the target
  model. Name the traits that actually matter: "direct, leads with the answer, short
  paragraphs, no corporate filler, sentence-case headings, straight quotes, dry humour",
  and so on.
- **Get the traits from the user, or from a sample.** If the user has not described their
  voice, either ask for three or four defining traits, or ask them to paste a short piece
  they have written and derive the traits from it. If they want a named public style, name
  the qualities of that style rather than just the label.
- **Consider embedding a short exemplar.** For voice, one or two lines of the target voice
  in the prompt often carries more than a list of adjectives, especially on Fable and Opus.
- Voice notes land especially well on Fable and Opus, which follow communication-style
  guidance closely; lower tiers need the traits made more explicit.

---

## Optional pass: de-slop (anti-AI)

Adds constraints that strip the generic-LLM tells from the eventual output. Include the
items that fit the task; do not paste the whole list into every prompt.

Common tells to instruct the model to avoid:

- Preamble and throat-clearing ("Certainly!", "Great question", "In this response I will").
- Empty summary paragraphs that restate what was just said.
- Hedging stacks ("it's worth noting that", "generally speaking", "in many cases").
- Rule-of-three padding and forced parallelism.
- Over-signposting ("Firstly... Secondly... In conclusion").
- Fake enthusiasm and exclamation marks.
- Emoji, unless asked for.
- Em dashes and en dashes (this skill's own hygiene rule; instruct the target model to use
  hyphens, commas, or separate sentences).
- Corporate filler and consultant-speak ("leverage", "utilise", "seamless", "robust").

Calibrate by tier: Fable needs the least of this (its default prose is cleanest), lower
tiers need more of it made explicit. State the constraints as a short "avoid:" list near
the end of the prompt so they are the last thing the model reads before answering.

---

## Optional pass: handoff

When the prompt is one step in a longer piece of work, emit a short handoff doc so the user
can open a fresh session with full context and not re-explain. Keep it to:

- **Goal** - what the larger piece of work is.
- **Where we are** - what this prompt does and what has been decided.
- **The prompt** - the finished artefact.
- **Open questions / next steps** - anything deferred.

---

## Optional pass: skill-ify

When the user will reuse a prompt regularly, it should become a skill rather than a prompt
they paste each time. Do not hand-roll a `SKILL.md` here. Hand off to the **skill-creator**
skill, passing the finished prompt and the task spec as the starting material.

Match the handoff to how the reuse surfaced: if the user **explicitly asked** to make the
prompt reusable or official, that request already is the go-ahead - execute the handoff in
the same turn, do not answer with "say the word". Reserve the offer for reuse *you* inferred
("you'll clearly run this weekly - want it as a skill?").
