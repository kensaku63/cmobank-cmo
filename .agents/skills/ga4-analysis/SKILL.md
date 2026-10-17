---
name: ga4-analysis
description: aachatのGA4でWebアクセス・登録・直接依頼・資料閲覧を読む。通常は公式MCP、7日条件付きファネルは保存request付きCLIを使う。製品DBの全登録数や自動実行の分析とは区別する。
---

# aachat GA4 analysis

[RUNBOOK](../../../knowledge/ga4/RUNBOOK.md)を読み、対象property・正式集計開始日・検証除外日・権限と品質metadataを確認する。[指標辞書](../../../knowledge/ga4/measurement-plan.md)を採用する。

Agent専用設定の公式MCPでproperty詳細、custom dimensions、run_reportを取得する。現在のSessionにtoolが注入されていなければRUNBOOKのread.pyが同じ設定の公式MCPをstdioで呼べる。7日ファネルは同scriptのfunnelと保存済みJSONを使い、時間条件・Web/v1フィルターを削らない。API失敗や未登録parameterを0へ変換しない。

[接続確認記録](../../../knowledge/ga4/connection-evidence.md)は2026-10-17時点の履歴。分析時は実取得を優先し、未再確認の設定は未確認と表示する。ADCを表示・commitせず、読取にMP secretを要求しない。同一macOSユーザー下のAgent設定限定はOS隔離ではない。
