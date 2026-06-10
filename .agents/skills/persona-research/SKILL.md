# Persona Research

Use this skill when the user asks for market research, customer understanding, persona building, pain discovery, "顧客理解", "リサーチ", "ペルソナ", or when any upstream task (demand selection, concept, LP) lacks research depth.

## Goal

Run the research loop (鳥の目・虫の目・魚の目 → ペルソナ脳内マップ) and produce deep, demand-language insights that feed demand selection and product concept.

Marketing outcomes are ~80% determined by research. This skill is the input layer for every other skill.

## Required Knowledge

Before producing output, always read:

- `knowledge/research-method.md`
- `knowledge/persona-empathy.md`
- `knowledge/quality-gates.md` (gates 0 and 1)
- `knowledge/examples.md`
- `knowledge/glossary.md`

For deeper grounding, read `cmobank-book/chapter-outline.md` first, then:

- Research method: `cmobank-book/04-research-birds-bugs-fish-eye.md`
- Persona mind map and empathy: `cmobank-book/05-persona-mind-map.md`
- Desire vs demand: `cmobank-book/02-desire-to-demand.md`

## Procedure

1. Define what the research must answer (which demand, which market, which persona). Research without a question becomes aimless collection.
2. Bird's eye: search for market size, industry structure, regulation, PEST (current state). Estimate market size as 購入意欲額 × 人数 with explicit assumptions.
3. Bug's eye: collect competitors' LPs, pricing, claimed demands. Collect raw customer language from reviews, Q&A sites, and SNS. Record exact phrases, not summaries.
4. Fish's eye: same PEST viewed as movement. List "what changed recently / what will change" and where each change creates a demand-supply gap.
5. Build the research map (3 branches) and diagnose which eye is thin. Fill the thin one before proceeding.
6. Build the persona mind map:
   - Center: one demand (broad enough to aim No.1, not overcrowded)
   - 現状: pain as "scene + emotion" pairs, in the persona's own words
   - 理想: desired future as "scene + emotion" pairs
   - 解決策: existing alternatives and their features, fact-based
   - 良い需要: candidates from the gap between 現状 and 理想 and from holes competitors leave
7. Verify empathy depth: for each line, ask "would this persona really say this?" Replace anything a seller would generically write.
8. Label every n=1 insight as 未検証 and propose how to verify it with multiple people (interview questions tied to the 4 purposes: demand / pain・benefit / alternatives / decision criteria).
9. Run gates 0 and 1 in `knowledge/quality-gates.md` before output.

## Output Format

```text
## リサーチの問い
〔このリサーチで答えること〕

## 鳥の目
- 市場規模(推定式つき):
- 業界構造・規制:
- PEST(現状):

## 虫の目
- 競合と名乗っている需要:
- 生の痛みの言葉(出典つき・原文のまま):

## 魚の目
- 最近変わったこと / これから変わること:
- それが生む需要と供給のギャップ:

## ペルソナ脳内マップ
- 中心の需要:
- 現状(シーン + 感情):
- 理想(シーン + 感情):
- 解決策(競合と特徴):
- 良い需要候補:

## 未検証の仮説と検証方法
- 〔仮説〕: 〔誰に・何を聞いて再現を確かめるか〕

## 次の工程への引き継ぎ
〔demand-research / product-concept who consumes this〕
```

## Guardrails

- Do not present numbers without sources or explicit estimation steps. Separate 事実 / 推定 / 仮説.
- Do not stop at attributes (age, job, family). Persona is a brain, not a profile.
- Do not write pains as abstract words (快適・便利・安心). Always scene + emotion.
- Do not slip into seller perspective. "自分ならこう買うかな" is a red flag.
- Do not generalize an n=1 insight without labeling it unverified.
- Do not converge during divergence. Candidate generation and gate-based selection are separate phases.
