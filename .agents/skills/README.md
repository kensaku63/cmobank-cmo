# Runtime skills

このディレクトリには、cmobank-cmo が session 実行時に使う専用 skill を置きます。

## Skills

- `cmo-strategy`: 事業全体の CMO 提案書を作る
- `demand-research`: 青い需要候補を出し、狙う需要を決める
- `product-concept`: 商品コンセプト、USP、オファーを作る
- `lp-funnel`: LP とコミュニケーションファネルを設計・レビューする
- `hypothesis-test`: センターピン、重要仮説、検証計画を作る

## Reference Policy

Each skill should read the core files in `knowledge/` before producing output. Use `cmobank-book/` as the deeper reference layer when a task needs chapter-level grounding, precise terminology, or more context than the compact `knowledge/` files provide.

Start deep references from `cmobank-book/chapter-outline.md`, then read the relevant chapter files.
