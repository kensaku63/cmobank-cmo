# aachat(agentic company builder)

## 現在地の一文分解(最終更新: 2026-07-18)
今この事業は、「思いついた構想が薄れないうちに動き出してほしい。作ることに集中し続けたい founder」(N=1 確定・3 人インタビューで検証中)に、Agentic Company Builder(最初の 5 分で専門 agent が誕生し仕事が動き出す)を当て、「Build your agentic company — 思いついた構想が、薄れる前に動き出す会社をつくる」というカテゴリ創造のコミュニケーションで取引を成立させようとしている。

## ビジネスゴール
- 未確認(kensaku から明示されていない)。dogfooding → community → 初期ユーザーの順で立ち上げる方針。

## 確定事項(意思決定済み)
- キーコンセプトマップの正本: aachat-key-concept project の key-concepts.md(v5、2026-07-18)
- v5 確定(kensaku 承認 2026-07-18): A1「Build your agentic company — 思いついた構想が、薄れる前に動き出す会社をつくる」/ C1 需要 = 鮮度と集中(第4案)/ D2 = 最初の5分で専門 agent が誕生し最初の仕事が動き出す(覚えることゼロ)。registry へ change revision 3 件 propose 済み(A1: d362a50f / C1: 556a287b / D2: c620f896)、publish 待ち
- registry への propose は aachat-mcp への stdio JSON-RPC で可能(initialize → notifications/initialized → tools/call。helper パターンは検証済み)
- 需要は「実現したい状態」で切る(決定 2026-07-10)
- 戦略の背骨: B2「Agent work should become company assets」(registry 唯一の endorsement)、B1 カテゴリ創造、B5 dogfooding
- キーコンセプトの高度基準: 事業判断を変えるものだけ。製品の手触り(同僚性・体験で分かる)は製品設計指針に降格(2026-07-17)
- kensaku の言葉の好み: 翻訳調・metaphor(共犯者・複利)・説明訳(AIエージェントが働く会社)は嫌う。シンプルで主語が立つ言葉。上位コンセプトほど文言にこだわる

## 未検証の重要仮説
- 狙う需要 = 「鮮度と集中」(C1 第4案)が kensaku 以外の founder にも通じる(検証: 実在 3 人インタビュー / 成功: 3 人中 2 人以上から誘導なしで「薄れる・冷める・集中が切れる」系の固有の言葉 / 失敗: 全員が前進・拡大の言葉のみ→C1 を前進・拡大側へ戻し A1 も再検討 / 状態: 未着手。3 人の欲求は現状「言語化して組織に落とす・まるっと任せる・売上3倍」で鮮度の言葉は未観測)
- A0→C1 接続(想像起点の欲求)は N=1 で支持済み(「頭の中のイメージ」「具現化できない」が誘導なしに出た)。他 founder での再現は上記インタビューで確認
- 「agent が作成された = 資産が残った」が初見ユーザーにも通じる(検証: prototype。dogfooding 済み founder の実感かもしれない / 状態: 未着手)
- 鮮度のモノサシで立っている競合は不在(検証: 魚の目 research / 状態: 未着手)

## 検証結果ログ
- 2026-07-21: okr project で kensaku/sotaooo が戦略メモを投稿(seq 1-16)。新事実: (1) 根本思想 =「トークン費用対効果の最大化」、aachat の価値 =「1 セッション当たりの価値がいかに増えるか」 (2) 勝ち筋 = 無料提供 → Discovery ネットワーク効果で moat → 有料化 (3) マーケ大方針 = web 上の露出面最大化を狙うコンテンツマーケ中心(kensaku 確定方針) (4) 課題認識 = コンセプト作成が難しすぎる・最適な OKR が作れない・ブランドメッセージ未確定(seq 16)。私の考察を seq 17 に投稿: 「セッション当たり価値」は需要の言葉ではなく Right to Win のモノサシの発明 / 無料期の成功指標は代替行動からの乗り換え観測 / コンテンツの狙う面は検索順位より AI の引用(GEO。AI 経由流入 +357% YoY、ChatGPT 最頻引用の 28.3% は Google 上位不在) / エージェント自身による一次情報量産 = dogfooding として構造的 Right to Win / センターピンは引き続き実在 3 人インタビュー
- 2026-07-18: N=1 インタビュー(Asks 17 問)完了。全回答と読み取りは aachat-key-concept の research-raw-voices.md。5 大発見: (1) 需要の言葉は「鮮度(イメージが薄れる前に)と集中(認知コストを増やさない)」で、「人を増やさず」は本音でない (2) coordination pain の言葉は 17 問で一度も自発的に出ず、入口需要は「前進・実現」側の可能性大 (3) 資産の第一級は agent 自身。最初の 5 分 = agent を作る (4) A5 の主語は「事業化できなかった人たち」= 民主化。wedge は founder、vision は未創業者の二段構え (5) 断り文句は「覚えるのが大変そう」= 学習コストの見た目。A1 再出し方向は「ベネフィット or ユニークな示唆」。flagship story = 特許申請 agent(80 候補→先行調査→23 件文書化→ブラウザで申請完了)。虫の目候補 3 人: イングリッド黒川・icra 鴻上・とーる
- 2026-07-13: registry 登録 14 件中 13 publish / 1 decline(Build with us、「共犯者」という言葉が理由)
- 2026-07-14〜17: kensaku が concern 8 件・endorsement 1 件(B2)・D1 削除・A2/A3 を contextual に調整。文言懸念(A1/B3/B4)、高度不足(B6/旧C2)、需要のずれ(C1)
- 2026-07-17: v4 反映。registry へ 8 件の pending revision 提案(A1・B3・B4・C1需要・D2 change + Build with us 言い換え + A0 想像を創造する new + A3 改訂)と link candidate 1 本(A1 realizes A0)。A0/A3 は kensaku 承認済み(「いいですね」)、他 6 件は review 待ち

## 撤退・変更条件
- C1 需要の research で生の言葉・代替行動が取れなければ、切り方(実現したい状態)ごと再検討に戻る

## 次回への申し送り
- kensaku のマーケ大方針は「web 露出面最大化のコンテンツマーケ」で確定。ただしブランドメッセージ確定は 3 人インタビュー結果の後に置くべきと提案済み(okr seq 17)。コンテンツのモノサシ提案 = 本数ではなく AI 引用率・AI 経由流入
- 「1 セッション当たり価値」モノサシは今後の Right to Win 論の中核候補。コンセプト化する際は「モノサシの教育」設計(入口は需要の言葉 → モノサシを渡す → aachat が No.1)を崩さない
- まず v5 の pending revision 3 件(A1: d362a50f / C1: 556a287b / D2: c620f896)の publish / decline を registry で確認してから動く(concern は chat に流れないので registry を直接読む)
- 次の実働は 2 本: (1) 実在 3 人(イングリッド黒川 / icra 鴻上 / とーる)への虫の目インタビュー設計(persona-empathy.md の手順。観測照準: 鮮度・集中の言葉、断り文句の実物) (2) 特許申請 agent story の 5 分 demo / community story 脚本化(story 原文は research-raw-voices.md の回答 10)
- research 後に docs/strategy/concept.md の更新提案(入口需要 = 鮮度と集中 / 継続理由 = coordination cost 解消の二層構造)と D1 語り口の再導出(教育コピー候補「会社は、雇わなくてもつくれる」)
- N=1 の全原文と 5 大発見は aachat-key-concept の research-raw-voices.md が正本。マップ正本は key-concepts.md v5
- kensaku の言葉のインプット済みリスト: 好きなコピー参照点は「特になし」。口語は「マルチエージェントをマネジメントして、AIカンパニーを作れるサービス」(ただし「マネジメント」語彙は断り文句を誘発するため messaging では使わない)
- registry へは aachat-mcp に stdio JSON-RPC で直接アクセスできる(initialize → notifications/initialized → tools/call の 3 行を stdin に流す。MCP tool としては未接続)
