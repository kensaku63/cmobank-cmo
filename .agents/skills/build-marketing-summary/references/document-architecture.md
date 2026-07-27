# Marketing Summary Document Architecture

## 標準構成

既存の文書管理ルールがない場合は、次を起点にする。ファイル名は環境に合わせて変えてよいが、権威レベルは混ぜない。

```text
PROJECT.md / index
├── canon/
│   ├── core-words.md
│   ├── marketing-strategy.md
│   ├── communication-principles.md
│   └── production-checklist.md
├── reference/
│   ├── audience-and-demand.md
│   ├── evidence.md
│   ├── language-examples.md
│   └── glossary.md
└── workbench/
    ├── open-questions.md
    ├── decision-log.md
    └── topic-*.md
```

小規模な事業ではファイルを統合してよい。ただし、異なる権威レベルを一つの文書へ統合しない。

## 文書ごとの責務

### `PROJECT.md` / index

文書システムの入口。目的、現在地、権威レベル、作業中の論点、各正本への導線を置く。マーケティング本文を重複させない。

### `canon/core-words.md`

権威レベルはVerbatim Canon。

- 事業定義
- カテゴリ定義
- 狙う需要の一文
- 商品コンセプト
- 中心となる約束
- ブランドメッセージ
- USP
- 公式用語の短い定義
- 使用禁止表現

掲載文言は明示的な再承認なしに変更・言い換えない。背景、例、候補、理由は置かない。

### `canon/marketing-strategy.md`

権威レベルはDecision Canon。

- ビジネスゴール
- 狙う需要と選定理由
- 需要を持つ人、持たない人
- 最重要ベネフィットと価値の優先順位
- 競合と代替手段
- 選ぶモノサシ
- Right to Win
- 約束できる範囲
- 重要仮説と検証状態

### `canon/communication-principles.md`

権威レベルはDecision Canon。

- コミュニケーション前の認識
- 変えるべき認識
- 行動時の認識
- 共感、教育、約束、証拠、不安解消
- 伝える順番
- 伝えないこと
- 語り方の原則
- 避けるカテゴリー認識

### `canon/production-checklist.md`

権威レベルはDecision Canon。公開前にYes/Noで判定できる10〜15問へ絞る。

### `reference/audience-and-demand.md`

需要が生まれるシーン、感情、心の声、代替行動、拒否理由、生の発言を置く。

### `reference/evidence.md`

約束を支える実績、数値、仕組み、利用事例、顧客の声を置く。各証拠がどの約束を支えるか、公開可能か、出典、確認日を示す。

### `reference/language-examples.md`

良い例、悪い例、修正例、媒体別応用例を置く。「公式コピーではない」と明記する。

### `reference/glossary.md`

用語の背景、関連概念、誤用例を置く。公式な短い定義はVerbatim Canonを参照する。

### `workbench/open-questions.md`

決める問い、必要性、選択肢、推奨、更新先Canon、状態を置く。

### `workbench/decision-log.md`

決定日、決定内容、採用理由、棄却案、影響するCanon、再検討条件を置く。現在の結論はCanonを参照する。

### `workbench/topic-*.md`

複数回の壁打ちが必要な重要論点だけを独立させる。軽い論点まで分割しない。

## 文書冒頭の表示

各文書に、権威レベル、使用ルール、参照用途を明記する。

```text
権威レベル: Verbatim Canon
使用ルール: 確定文言は、明示的な再承認なしに変更・言い換えない。
参照用途: 公式コピー、制作物レビュー
```

```text
権威レベル: Reference
使用ルール: 判断材料として参照する。例文は公式コピーとしてそのまま使用しない。
参照用途: リサーチ、企画、コピー開発
```

Workbenchには次を目立つ位置に置く。

> この文書には未確定の候補が含まれる。マーケティングの正本として使用しない。

## 優先順位と競合解決

通常の参照順は次の通り。

1. Verbatim Canon
2. Decision Canon
3. Reference
4. Workbench

ただし、Verbatim CanonとDecision Canonは単純な上下関係ではない。公式文言はVerbatim Canon、意味の解釈はDecision Canonを正とする。両者が矛盾した場合は、片方を都合よく選ばず、公開を止めて再決定する。

## 昇格フロー

```text
Workbenchで壁打ち
→ 人間が判断を確定
→ Decision Logへ理由を記録
→ Decision Canonへ意味を反映
→ 必要な文言だけVerbatim Canonへ圧縮
→ Referenceと制作例を更新
```

## 分割の判断

次の場合だけ文書を分ける。

- 権威レベルが異なる。
- 読む場面や読者が明確に異なる。
- 独立して更新される。
- 一つの文書に置くと誤用や重複が起きる。

「章が長い」という理由だけで分けない。分割後も入口から正本へ迷わず到達できるようにする。

## 最終監査

- 一つの判断に複数の正本がないか。
- Verbatim Canonに説明や例が混ざっていないか。
- Decision Canonに候補案や調査ログが残っていないか。
- Referenceの事実、推定、仮説、出典、確認日が区別されているか。
- Workbenchが制作時の正本として参照されない表示になっているか。
- 変更された判断と、それに依存する文言・証拠・チェック項目が整合しているか。
- 新しい制作者が追加説明なしに正しい文書へ到達できるか。

