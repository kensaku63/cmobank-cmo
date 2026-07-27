# Runtime skills

このディレクトリには、cmobank-cmo が session 実行時に使う専用 skill を置きます。

## Skills

- `persona-research`: 鳥の目・虫の目・魚の目のリサーチとペルソナ脳内マップを作る(全スキルの入力層)
- `cmo-strategy`: 事業全体の CMO 提案書を作る
- `demand-research`: 青い需要候補を出し、狙う需要を決める
- `product-concept`: 商品コンセプト、USP、オファーを作る
- `lp-funnel`: LP とコミュニケーションファネルを設計・レビューする
- `hypothesis-test`: センターピン、重要仮説、検証計画を作る
- `build-marketing-summary`: マーケティングの文言・判断・根拠・思考過程を4段階の権威レベルに分け、壁打ちから正本化まで進める

## Quality Policy

- 各スキルは、対応する `knowledge/quality-gates.md` のゲートを通してから出力する
- 出力前に `knowledge/review-checklist.md` の該当セクションを回す
- リサーチが薄いまま下流の成果物を作らない。詰まったら `persona-research` に戻る

## Reference Policy

Each skill should read the core files in `knowledge/` before producing output. Use `cmobank-book/` as the deeper reference layer when a task needs chapter-level grounding, precise terminology, or more context than the compact `knowledge/` files provide.

Start deep references from `cmobank-book/chapter-outline.md`, then read the relevant chapter files.
