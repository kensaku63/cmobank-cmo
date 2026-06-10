# Hypothesis Test

Use this skill when the user asks for validation plan, MVP test, experiment design, center pin, critical hypothesis, go / no-go criteria, or pivot / withdrawal decision.

## Goal

Identify the center pin and critical hypothesis, then design the fastest validation and decision criteria.

## Required Knowledge

Before producing output, always read the core knowledge files:

- `knowledge/cmobank-principles.md`
- `knowledge/cmo-workflow.md`
- `knowledge/quality-gates.md`
- `knowledge/output-templates.md`
- `knowledge/anti-patterns.md`
- `knowledge/glossary.md`

For deeper grounding, read `cmobank-book/chapter-outline.md` first, then use the relevant book chapters:

- Target demand and demand-side hypothesis: `cmobank-book/06-blue-demand-target-demand.md`
- CMO work, center pin, and critical hypothesis: `cmobank-book/12-cmo-work.md`
- Provisional answers and changing direction: `cmobank-book/13-epilogue.md`
- Precise terms: `cmobank-book/GLOSSARY.md`

## Procedure

1. Restate the strategy:
   - target demand
   - product concept
   - USP
   - funnel
2. Identify the center pin:

   ```text
   それを倒せば全体が連鎖的に決まる最重要の一点は何か。
   ```

3. Identify the critical hypothesis:

   ```text
   この事業がうまくいくために、最も根本で成り立っていなければならない前提は何か。
   ```

4. Prefer demand-side hypotheses first:
   - this demand exists
   - the pain is strong enough
   - willingness to pay is high enough
   - the prospect believes the promise
   - the offer creates action
5. Design the fastest test:
   - interview
   - test ad
   - landing page
   - pre-order
   - manual sales
   - small event / workshop
   - concierge MVP
6. Define success, failure, and inconclusive criteria before running the test.
7. Add anti-confirmation checks:
   - what would prove this wrong
   - what signal should make us stop
   - what signal should make us change target demand
8. Define the next decision:
   - continue
   - change
   - stop
9. Record the hypothesis, test design, and (later) results in `memory/<事業スラッグ>.md` per `memory/README.md`, so the next session resumes from the verified state instead of re-proposing.
10. Run section E of `knowledge/review-checklist.md` before output.

## Output Format

```text
## 戦略の前提
- 狙う需要:
- 商品コンセプト:
- USP:
- ファネル:

## センターピン
〔一点〕

理由:
〔ここが倒れると何が連鎖するか〕

## 重要仮説
〔この事業の成否を決める根本仮説〕

## なぜ先に検証するか
〔この仮説が崩れると、どの戦略要素が崩れるか〕

## 最小検証
- 方法:
- 対象需要:
- 実施期間:
- 必要サンプル:
- 成功条件:
- 失敗条件:
- 判断保留条件:

## 否定兆候
- 〔この反応があれば仮説が怪しい〕
- 〔この違和感があれば見直す〕

## 次の意思決定
- 成功したら:
- 失敗したら:
- 判断保留なら:
```

## Guardrails

- Do not validate minor copy or pricing before validating the root demand hypothesis.
- Do not design tests only to confirm the idea.
- Do not call a pivot successful if the core demand hypothesis has collapsed.
- Do not keep going only because work has already been done.
- Do not ignore a strong "this does not feel like it will work" signal. Treat it as a formal warning to inspect.
