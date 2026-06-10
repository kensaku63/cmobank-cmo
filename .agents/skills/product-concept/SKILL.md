# Product Concept

Use this skill when the user asks for product concept, positioning, USP, offer, value proposition, message direction, or concept critique.

## Goal

Connect the target demand and product through a clear product concept, then translate it into USP and offer.

## Required Knowledge

Before producing output, always read the core knowledge files:

- `knowledge/cmobank-principles.md`
- `knowledge/cmo-workflow.md`
- `knowledge/sales-offer.md`
- `knowledge/quality-gates.md`
- `knowledge/output-templates.md`
- `knowledge/anti-patterns.md`
- `knowledge/examples.md`
- `knowledge/glossary.md`

For deeper grounding, read `cmobank-book/chapter-outline.md` first, then use the relevant book chapters:

- Desire and demand context: `cmobank-book/02-desire-to-demand.md`
- Product planning map: `cmobank-book/07-product-planning-map.md`
- Product concept and USP: `cmobank-book/08-product-concept.md`
- Sales and offer: `cmobank-book/09-sales-and-offer.md`
- Precise terms: `cmobank-book/GLOSSARY.md`

## Inputs

- Target demand
- Product / service
- Features
- Effects
- Existing proof
- Competitors or alternatives
- Price / offer constraints

If target demand is missing, stop and define it first. A product concept cannot be built while the demand side is blank.

## Procedure

1. Restate the target demand in demand language.
2. List product features (aim for 10+; divergence first).
3. Convert features into objective effects.
4. Convert effects into benefits:
   - positive emotion
   - desired state
   - scene where the user feels it
   - check the 1.5 メートル rule: realistic and half a step ahead — not "人生が変わる" (too far), not "少し楽になる" (too near)
5. Attach proof to each important benefit:
   - results
   - testimonials
   - mechanism
   - data
   - authority
   - guarantee
6. Compress into one product concept:

   ```text
   〔狙う需要を持つ人〕に、〔信じられる理由つきのベネフィット〕を提供する商品。
   ```

7. Score the concept against five conditions:
   - people would pay for it
   - newness / surprise
   - benefit
   - believable reason
   - simplicity
8. Translate the concept into USP:

   ```text
   〔独自の強み〕によって、〔ベネフィット〕を、〔オファー〕で提供します。
   ```

9. Design the offer with (`knowledge/sales-offer.md`):
   - good deal (主観的なお得感)
   - low risk (リスクリバーサルは申し込みの不安に紐づける)
   - reason to act now (オファー自体に制限を組み込む)
   - clarity (何を・いくらで・どうすれば、まで)
10. Check the sales 4 点セット: ベネフィット・正しい痛み・No.1 の理由・厚いオファー.
11. Run gates 3-4 in `knowledge/quality-gates.md` and section C of `knowledge/review-checklist.md` before output.

## Output Format

```text
## 狙う需要
〔需要〕

## 商品企画マップ
| 特徴 | 効果 | ベネフィット | 証拠 |
|---|---|---|---|

## 商品コンセプト
〔誰に・どんな価値〕

## 5 条件診断
- 払ってでも欲しい:
- 新しさ / 意外性:
- ベネフィット:
- 信じられる理由:
- シンプル:

## USP
〔独自の強み + ベネフィット + オファー〕

## オファー
- お得感:
- 低リスク:
- 今やる理由:
- わかりやすさ:

## 改善すべき弱点
〔最も弱い軸と補強案〕
```

## Guardrails

- Do not create a concept before target demand is defined.
- Do not list many values as the concept. Compress to one value.
- Do not confuse feature with benefit.
- Do not present a benefit without proof, and do not attach proof unrelated to the benefit (家電大賞 for リラックス is noise).
- Do not confuse concept with catch copy. Concept is internal; copy is external expression.
- If the concept comes out generic (高品質な◯◯), treat it as a research shortage signal and go back to persona-research, not wordsmithing.
