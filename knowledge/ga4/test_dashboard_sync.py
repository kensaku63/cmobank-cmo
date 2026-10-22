"""Offline tests for dashboard_sync (spec 7 acceptance examples). No GA, gh or chat calls.

Run from the Agent repository root:
  python3 -m unittest discover -s knowledge/ga4 -p test_dashboard_sync.py -v
"""
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import dashboard_sync as sync  # noqa: E402

MIGRATION = Path(__file__).resolve().parents[4] / 'teams/aachat/projects/aachat-analytics/db/migrations/analytics_dashboard_v1.sql'
TODAY = dt.date(2026, 11, 2)
REPORTS = {r['report_key']: r for r in sync.DEFINITIONS['reports']}

USABLE_SQL = """
WITH ranked AS (
  SELECT r.*, row_number() OVER (PARTITION BY window_key ORDER BY run_seq DESC) AS rk
  FROM analytics_report_runs r WHERE status IN ('ok', 'empty')
)
SELECT v.metric_key, v.dimensions_json, v.value_num FROM ranked r JOIN analytics_values v ON v.run_id = r.run_id
WHERE r.rk = 1 AND r.report_key = '{key}' AND r.variant = '{variant}' AND r.period_start = '{start}' AND r.period_end = '{end}'
ORDER BY v.dimensions_json, v.metric_key
"""


def page(dims, metrics, rows, row_count=None):
    return {'dimension_headers': [{'name': d} for d in dims], 'metric_headers': [{'name': m, 'type_': 'TYPE_INTEGER'} for m in metrics],
            'rows': [{'dimension_values': [{'value': v} for v in dv], 'metric_values': [{'value': str(v)} for v in mv]} for dv, mv in rows],
            'row_count': len(rows) if row_count is None else row_count, 'metadata': {'subject_to_thresholding': False}}


def task(key, variant, start, end=None):
    start = dt.date.fromisoformat(start)
    return sync.Task(REPORTS[key], variant, 'day' if end is None else 'window', start, dt.date.fromisoformat(end) if end else start)


@unittest.skipUnless(MIGRATION.exists(), 'Project migration not present in this workspace')
class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = sync.SqliteDb(Path(self.tmp.name) / 't.db', MIGRATION)
        sync.ensure_definitions(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def store(self, pairs):
        return sync.store(self.db, pairs, 'batch', TODAY, sync.load_coverage(self.db))

    def usable(self, key, variant, start, end):
        return self.db.query(USABLE_SQL.format(key=key, variant=variant, start=start, end=end))

    def test_definitions_are_idempotent_and_immutable(self):
        self.assertEqual(sync.ensure_definitions(self.db), 0)
        self.db.query("UPDATE analytics_report_definitions SET definition_hash = '" + '0' * 64 + "' WHERE report_key = 'G01' AND variant = 'total'")
        with self.assertRaises(sync.SyncError):
            sync.ensure_definitions(self.db)

    def test_period_users_are_stored_not_summed(self):
        t = task('G06', 'total', '2026-10-21', '2026-10-22')
        cells, _, _ = sync.cells_from_report(t, [page([], ['eventCount', 'totalUsers'], [([], [12, 4])])])
        self.store([(t, dict(status='ok', cells=cells))])
        values = {r['metric_key']: r['value_num'] for r in self.usable('G06', 'total', '2026-10-21', '2026-10-22')}
        self.assertEqual(values, {'eventCount': 12, 'totalUsers': 4})

    def test_empty_is_a_snapshot_without_zero_rows(self):
        t = task('G03', 'total', '2026-10-25')
        cells, _, _ = sync.cells_from_report(t, [page([], ['eventCount'], [])])
        self.assertEqual(cells, [])
        self.assertEqual(self.store([(t, dict(status='empty', cells=[]))]), {'empty': 1})
        self.assertEqual(self.usable('G03', 'total', '2026-10-25', '2026-10-25'), [])

    def test_failed_newer_attempt_keeps_previous_usable_values(self):
        t = task('G06', 'total', '2026-10-25')
        self.store([(t, dict(status='ok', cells=[dict(dimensions_json='{}', metric_key='eventCount', value_num=3)]))])
        self.store([(t, sync.failed_result('read_failed', 'x'))])
        self.assertEqual([r['value_num'] for r in self.usable('G06', 'total', '2026-10-25', '2026-10-25')], [3])
        latest = self.db.query("SELECT status FROM analytics_report_runs ORDER BY run_seq DESC LIMIT 1")[0]['status']
        self.assertEqual(latest, 'failed')

    def test_new_snapshot_replaces_rows_instead_of_merging(self):
        t = task('G02', 'breakdown', '2026-10-25')
        first = [dict(dimensions_json=sync.canon({'sessionSourceMedium': s, 'landingPage': '/'}), metric_key='sessions', value_num=n) for s, n in (('x', 10), ('y', 3))]
        self.store([(t, dict(status='ok', cells=first))])
        self.store([(t, dict(status='ok', cells=first[:1]))])
        self.assertEqual([r['value_num'] for r in self.usable('G02', 'breakdown', '2026-10-25', '2026-10-25')], [10])

    def test_writing_runs_are_never_usable_and_get_abandoned(self):
        self.db.query("INSERT INTO analytics_report_runs (run_id, batch_id, report_key, definition_version, variant, window_key, period_kind, period_start, period_end, observed_through, requested_at, status, period_state, coverage_snapshot_json, request_json, quality_json) "
                      "VALUES ('w', 'b', 'G06', 1, 'total', '" + 'a' * 64 + "', 'day', '2026-10-25', '2026-10-25', '2026-10-25', '2000-01-01T00:00:00Z', 'writing', 'eligible', '{}', '{}', '{}')")
        self.assertNotIn('a' * 64, sync.usable_windows(self.db))
        sync.abandon_stale_writing(self.db)
        self.assertEqual(self.db.query("SELECT status FROM analytics_report_runs WHERE run_id = 'w'")[0]['status'], 'incomplete')

    def test_coverage_snapshot_marks_validation_and_pending(self):
        cov = sync.load_coverage(self.db)
        snap = sync.coverage_snapshot(cov[('G06', 1, 'total')], dt.date(2026, 10, 20), dt.date(2026, 10, 21))
        self.assertEqual(snap['days'], {'excluded': 1, 'accepted': 1})
        self.assertFalse(snap['all_accepted'])
        self.assertEqual(sync.coverage_snapshot(cov[('G03', 1, 'total')], dt.date(2026, 10, 22), dt.date(2026, 10, 22))['days'], {'pending': 1})

    def test_product_ingest_zero_total_breakdown_empty_and_first_snapshot_kept(self):
        raw = json.dumps({'schema': sync.PRODUCT_SCHEMA, 'start_date': '2026-10-30', 'end_date': '2026-10-31', 'retrieved_at': '2026-11-01T00:00:00Z',
                          'signups': [{'date': '2026-10-31', 'audience': 'external', 'auth_kind': 'github', 'accounts': 2},
                                      {'date': '2026-10-31', 'audience': 'external', 'auth_kind': 'guest', 'accounts': 1}],
                          'direct_requests_daily': [], 'automatic_daily': [],
                          'direct_requests_windows': [{'window_name': 'last7', 'window_start': '2026-10-25', 'window_end': '2026-10-31', 'audience': 'external', 'auth_kind': 'github', 'accounts': 5, 'requests': 9}]})
        results = sync.product_results(raw, 'fixture', sync.usable_windows(self.db), TODAY)
        self.store(results)
        self.assertEqual([r['value_num'] for r in self.usable('P01', 'total', '2026-10-30', '2026-10-30')], [0])
        self.assertEqual([r['value_num'] for r in self.usable('P01', 'total', '2026-10-31', '2026-10-31')], [3])
        self.assertEqual(self.db.query("SELECT status FROM analytics_report_runs WHERE report_key = 'P01' AND variant = 'breakdown' AND period_start = '2026-10-30'")[0]['status'], 'empty')
        window = {r['metric_key']: r['value_num'] for r in self.usable('P02', 'total', '2026-10-25', '2026-10-31')}
        self.assertEqual(window, {'accounts': 5, 'requests': 9})
        self.assertEqual(sync.product_results(raw, 'fixture', sync.usable_windows(self.db), TODAY), [])

    def test_growth_cohort_validation_and_null_percentile(self):
        row = dict(signup_source='x', signup_campaign='none', first_source='x', signup_medium='m', signup_content='none', signup_landing='/',
                   registrations_observed=15, denominator7=10, immature7=3, consent_unavailable7=2, first_use7=6, first_result_ready7=5,
                   first_result7=4, distinct_day_reuse7=4, denominator14=8, immature14=5, consent_unavailable14=2, next_week_use=3,
                   denominator28=0, immature28=15, consent_unavailable28=0, retained28=0, request_to_result_median_seconds=None,
                   request_to_result_p90_seconds=0, request_to_ready_median_seconds=10.5, ready_to_view_median_seconds=None)
        report = {'cohort_start': '2026-10-21', 'cohort_end': '2026-10-27', 'observed_through': '2026-11-20', 'retrieved_at': 'x', 'cohorts': [row],
                  'coverage': [{'date': '2026-10-21', 'event_name': 'sign_up', 'outcome': 'enqueued', 'count': 2}]}
        results = sync.growth_results(json.dumps(report), 'fixture')
        self.store(results)
        states = {r['metric_key']: r['value_state'] for r in self.db.query("SELECT metric_key, value_state FROM analytics_values v JOIN analytics_report_runs r USING (run_id) WHERE r.report_key = 'C01'")}
        self.assertEqual(states['request_to_result_median_seconds'], 'not_observed')
        self.assertEqual(states['request_to_result_p90_seconds'], 'observed')
        bad = dict(row, immature7=4)
        with self.assertRaises(sync.SyncError):
            sync.growth_results(json.dumps(dict(report, cohorts=[bad])), 'fixture')


class ParseTests(unittest.TestCase):
    def test_short_pagination_is_incomplete(self):
        t = task('G01', 'breakdown', '2026-10-25')
        cells, row_count, _ = sync.cells_from_report(t, [page(['pagePath', 'pageTitle'], ['screenPageViews', 'activeUsers', 'userEngagementDuration'], [(['/', 'a'], [1, 1, 2])], row_count=1200)])
        self.assertIsNone(cells)
        self.assertEqual(row_count, 1200)

    def test_rejects_header_mismatch_duplicates_and_negative(self):
        t = task('G07', 'breakdown', '2026-10-25')
        dims, mets = ['customEvent:request_kind'], ['eventCount', 'totalUsers']
        for pages in ([page(['other'], mets, [(['start'], [1, 1])])],
                      [page(dims, mets, [(['start'], [1, 1]), (['start'], [2, 1])])],
                      [page(dims, mets, [(['start'], [-1, 1])])],
                      [page(dims, mets, [(['start'], [1.5, 1])])]):
            with self.assertRaises(sync.SyncError):
                sync.cells_from_report(t, pages)

    def test_null_strings_and_not_set_stay_distinct(self):
        t = task('G07', 'breakdown', '2026-10-25')
        cells, _, _ = sync.cells_from_report(t, [page(['customEvent:request_kind'], ['eventCount', 'totalUsers'], [(['(not set)'], [1, 1]), (['null'], [2, 1]), ([''], [3, 1])])])
        self.assertEqual(len({c['dimensions_json'] for c in cells}), 3)

    def test_funnel_visualization_bounded_reading(self):
        def funnel(rows, header='activeUsers'):
            return {'funnelVisualization': {'dimensionHeaders': [{'name': 'funnelStepName'}],
                                            'metricHeaders': [{'name': header, 'type': 'TYPE_INTEGER'}, {'name': header, 'type': 'TYPE_INTEGER'}],
                                            'rows': [{'dimensionValues': [{'value': n}], 'metricValues': [{'value': str(v)}]} for n, v in rows]}}
        cells, _ = sync.cells_from_funnel(funnel([('1. First accepted request', 2), ('2. Second within seven days', 2)]))
        self.assertEqual([c['value_num'] for c in cells], [2, 2])
        for bad in (funnel([('1. First accepted request', 1), ('2. Second within seven days', 2)]),
                    funnel([('1. First accepted request', 2), ('2. Second within seven days', 1)], header='sessions'),
                    funnel([('1. Other', 2), ('2. Second within seven days', 1)])):
            with self.assertRaises(sync.SyncError):
                sync.cells_from_funnel(bad)

    def test_mcp_payload_from_text_or_structured_content(self):
        body = page([], ['eventCount'], [])
        self.assertEqual(sync.payload_from_mcp({'content': [{'type': 'text', 'text': json.dumps(body)}]}), body)
        self.assertEqual(sync.payload_from_mcp({'structuredContent': {'result': body}}), body)
        with self.assertRaises(sync.SyncError):
            sync.payload_from_mcp({'content': [{'type': 'text', 'text': '{}'}]})

    def test_sql_literals_escape_and_reject_unsafe_values(self):
        self.assertEqual(sync.q("it's"), "'it''s'")
        self.assertEqual(sync.q(None), 'NULL')
        for bad in (float('nan'), 'a\x00b', True):
            with self.assertRaises(sync.SyncError):
                sync.q(bad)


class PlanTests(unittest.TestCase):
    def windows(self, today, key='G06'):
        return [(t.period_kind, str(t.start), str(t.end)) for t in sync.plan_ga(dt.date.fromisoformat(today), set()) if t.report['report_key'] == key]

    def test_first_formal_day_has_no_seven_day_window(self):
        self.assertEqual(self.windows('2026-10-24'), [('day', '2026-10-21', '2026-10-21')])

    def test_seven_day_window_without_truncated_comparison(self):
        plan = self.windows('2026-10-30')
        self.assertIn(('window', '2026-10-21', '2026-10-27'), plan)
        self.assertNotIn(('window', '2026-10-14', '2026-10-20'), plan)
        self.assertEqual(sum(1 for p in plan if p[0] == 'window'), 1)

    def test_funnel_has_windows_only_and_growth_starts_later(self):
        self.assertTrue(all(kind == 'window' for kind, _, _ in self.windows('2026-11-05', 'G09')))
        self.assertEqual(self.windows('2026-10-24', 'G10'), [])

    def test_backfill_is_bounded(self):
        days = {s for k, s, _ in self.windows('2026-12-31') if k == 'day'}
        self.assertLessEqual(len(days), 3 + sync.BACKFILL_DAYS)


if __name__ == '__main__':
    unittest.main()
