#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-auth==2.62.0", "requests==2.34.2", "mcp==1.30.0"]
# ///
"""Daily dashboard sync: GA4 + product aggregates -> aachat-analytics Project Database.

Contract: Project docs/analytics-database-dashboard-spec.md. Stores aggregate values with
their exact conditions. Failures are recorded as failed runs, never as zero.

  uv run dashboard_sync.py run --project-root <Project root>       # daily update
  uv run dashboard_sync.py run --project-root <root> --skip-ga      # product only
  uv run dashboard_sync.py import-growth --project-root <root> --file growth-report.json
"""
import argparse
import asyncio
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
DEFINITIONS = json.loads((ROOT / 'dashboard_definitions.json').read_text())
PRODUCT_REPO = 'kensaku63/aachat'
PRODUCT_WORKFLOW = 'analytics-daily-usage.yml'
PRODUCT_ARTIFACT = 'analytics-daily-usage'
PRODUCT_SCHEMA = 'aachat-product-daily/v1'
REPORT_CALL_LIMIT = 100
BATCH_CALL_LIMIT = 500
BACKFILL_DAYS = 7
BACKFILL_HORIZON = 56
STATEMENT_BYTES = 80_000


class SyncError(Exception):
    """Safe message: never contains credentials or upstream error text."""


def canon(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def now_utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def jst_today():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date()


def days(start, end):
    return [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]


# ---------------------------------------------------------------- SQL literals
# chat db params are strings only and capped at 100. Values are validated and written as
# SQLite literals instead: strings by quote doubling, numbers only after finite checks.

def q(value):
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        raise SyncError('boolean literal is not allowed')
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise SyncError('non-finite number')
        return repr(value)
    text = str(value)
    if '\x00' in text:
        raise SyncError('NUL in text')
    return "'" + text.replace("'", "''") + "'"


class ChatDb:
    """`chat db query` from the Project root (target resolved by cwd)."""

    def __init__(self, project_root):
        self.root = Path(project_root)

    def query(self, sql):
        with tempfile.NamedTemporaryFile('w', suffix='.sql', delete=False) as handle:
            handle.write(sql)
            path = handle.name
        try:
            result = subprocess.run(['chat', 'db', 'query', '--file', path], cwd=self.root,
                                    capture_output=True, text=True, timeout=120)
        finally:
            os.unlink(path)
        try:
            body = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise SyncError('chat db query returned no JSON')
        if not body.get('ok'):
            code = (body.get('error') or {}).get('code', 'unknown')
            raise SyncError(f'chat db query failed: {code}')
        rows = body['data']['result_set']
        return [dict(zip(rows['columns'], item)) for item in rows['items']]


class SqliteDb:
    """Same interface over a local SQLite file, for tests and dry runs."""

    def __init__(self, path, migration):
        import sqlite3
        self.connection = sqlite3.connect(path)
        self.connection.execute('PRAGMA foreign_keys = ON')
        if migration:
            self.connection.executescript(Path(migration).read_text())

    def query(self, sql):
        cursor = self.connection.execute(sql)
        columns = [c[0] for c in cursor.description or []]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        self.connection.commit()
        return rows


def insert_many(db, table, columns, rows):
    """Multi-row INSERTs kept under the statement size limit."""
    head = f'INSERT INTO {table} ({", ".join(columns)}) VALUES '
    chunk, size = [], len(head)
    for row in rows:
        literal = '(' + ', '.join(q(row[c]) for c in columns) + ')'
        if chunk and size + len(literal) > STATEMENT_BYTES:
            db.query(head + ', '.join(chunk))
            chunk, size = [], len(head)
        chunk.append(literal)
        size += len(literal) + 2
    if chunk:
        db.query(head + ', '.join(chunk))


# ---------------------------------------------------------------- definitions

def variant_rows(report):
    for variant, dims in report['variants'].items():
        yield variant, dims


def definition_hash(report, variant):
    dims = report['variants'][variant]
    body = {k: report[k] for k in ('report_key', 'definition_version', 'source', 'source_id', 'measurement_version',
                                     'event', 'version_filter', 'host_filter', 'metrics', 'scope', 'periods')}
    body.update(variant=variant, dimensions=dims, timezone=DEFINITIONS['timezone'])
    return sha(canon(body))


def request_template(report, variant):
    if report['source'].startswith('ga4'):
        return ga_request(report, variant, '<start>', '<end>')
    return {'source': report['source'], 'schema': PRODUCT_SCHEMA if report['source'] == 'product_daily' else 'growth-report'}


def ensure_definitions(db):
    existing = {(r['report_key'], r['definition_version'], r['variant']): r['definition_hash']
                for r in db.query('SELECT report_key, definition_version, variant, definition_hash FROM analytics_report_definitions')}
    created = now_utc()
    defs, metrics, coverage = [], [], []
    for report in DEFINITIONS['reports']:
        for variant, dims in variant_rows(report):
            key = (report['report_key'], report['definition_version'], variant)
            digest = definition_hash(report, variant)
            if key in existing:
                if existing[key] != digest:
                    raise SyncError(f'{key[0]} v{key[1]} {variant} changed without a version bump')
                continue
            defs.append(dict(report_key=key[0], definition_version=key[1], variant=variant, label=report['label'],
                             purpose=report['purpose'], source=report['source'], source_id=report['source_id'],
                             measurement_version=report['measurement_version'], timezone=DEFINITIONS['timezone'],
                             scope_json=canon(report['scope']),
                             dimensions_json=canon([{'name': d} for d in dims]),
                             request_template_json=canon(request_template(report, variant)),
                             definition_hash=digest, created_at=created, evidence_ref=report['evidence_ref']))
            for metric in report['metrics']:
                metrics.append(dict(report_key=key[0], definition_version=key[1], variant=variant,
                                    numerator_key=None, denominator_key=None, **metric))
            for index, row in enumerate(report['coverage']):
                coverage.append(dict(coverage_id=f'{key[0]}-v{key[1]}-{variant}-initial-{index}', report_key=key[0],
                                     definition_version=key[1], variant=variant, evidence_ref=report['evidence_ref'],
                                     recorded_at=created, **row))
    if defs:
        insert_many(db, 'analytics_report_definitions', list(defs[0]), defs)
        insert_many(db, 'analytics_metric_definitions', list(metrics[0]), metrics)
        insert_many(db, 'analytics_coverage', list(coverage[0]), coverage)
    return len(defs)


def load_coverage(db):
    rows = db.query('SELECT * FROM analytics_coverage ORDER BY recorded_at, coverage_id')
    table = {}
    for row in rows:
        table.setdefault((row['report_key'], row['definition_version'], row['variant']), []).append(row)
    return table


def coverage_snapshot(rows, start, end):
    """Per-day decision: the latest recorded row covering that day wins."""
    states, used = {}, set()
    for day in days(start, end):
        iso = day.isoformat()
        decision = None
        for row in rows:  # ordered by recorded_at, coverage_id
            if row['valid_from'] <= iso and (row['valid_to'] is None or iso <= row['valid_to']):
                decision = row
        state = decision['state'] if decision else 'unknown'
        states[state] = states.get(state, 0) + 1
        if decision:
            used.add(decision['coverage_id'])
    return {'days': states, 'all_accepted': set(states) == {'accepted'}, 'decisions': sorted(used)}


# ---------------------------------------------------------------- planning

class Task:
    def __init__(self, report, variant, period_kind, start, end, observed_through=None):
        self.report, self.variant, self.period_kind = report, variant, period_kind
        self.start, self.end = start, end
        self.observed_through = observed_through or end
        self.dims = report['variants'][variant]
        self.window_key = sha(canon({'report_key': report['report_key'], 'definition_version': report['definition_version'],
                                     'variant': variant, 'period_start': start.isoformat(), 'period_end': end.isoformat(),
                                     'observed_through': self.observed_through.isoformat()}))


def usable_windows(db):
    return {r['window_key'] for r in db.query("SELECT DISTINCT window_key FROM analytics_report_runs WHERE status IN ('ok', 'empty')")}


def ga_windows(end, floor):
    """Exact rolling windows; never truncate a window that starts before the formal start."""
    windows = [(end - dt.timedelta(days=6), end), (end - dt.timedelta(days=13), end - dt.timedelta(days=7)),
               (end - dt.timedelta(days=27), end), (end - dt.timedelta(days=55), end - dt.timedelta(days=28))]
    chosen = [(s, e) for s, e in windows if s >= floor]
    span = (end - floor).days + 1
    if 1 < span < 28 and (floor, end) not in chosen:
        chosen.append((floor, end))  # "since start" window, shown as its own period
    return chosen


def plan_ga(today, usable):
    end = today - dt.timedelta(days=DEFINITIONS['ga_delay_days'])
    tasks, backfill = [], []
    for report in DEFINITIONS['reports']:
        if not report['source'].startswith('ga4'):
            continue
        floor = dt.date.fromisoformat(report['fetch_start'])
        if end < floor:
            continue
        for variant, _ in variant_rows(report):
            if 'day' in report['periods']:
                recent = [d for d in days(max(floor, end - dt.timedelta(days=2)), end)]
                tasks += [Task(report, variant, 'day', d, d) for d in recent]
                older = [d for d in days(max(floor, end - dt.timedelta(days=BACKFILL_HORIZON)), end - dt.timedelta(days=3))]
                backfill += [t for t in (Task(report, variant, 'day', d, d) for d in older) if t.window_key not in usable]
            if 'window' in report['periods']:
                for start, stop in ga_windows(end, floor):
                    task = Task(report, variant, 'window', start, stop)
                    if task.window_key not in usable:
                        tasks.append(task)
    backfill.sort(key=lambda t: t.start)
    allowed = sorted({t.start for t in backfill})[:BACKFILL_DAYS]
    return tasks + [t for t in backfill if t.start in allowed]


# ---------------------------------------------------------------- GA

def ga_request(report, variant, start, end):
    expressions = []
    if report['host_filter']:
        expressions.append({'filter': {'field_name': 'hostName', 'string_filter': {'match_type': 'EXACT', 'value': report['host_filter']}}})
    if report['event']:
        expressions.append({'filter': {'field_name': 'eventName', 'string_filter': {'match_type': 'EXACT', 'value': report['event']}}})
        for field, value in (('customEvent:surface', 'web'), ('customEvent:measurement_version', report['version_filter'])):
            expressions.append({'filter': {'field_name': field, 'string_filter': {'match_type': 'EXACT', 'value': value}}})
    dims = report['variants'][variant]
    body = {'date_ranges': [{'start_date': str(start), 'end_date': str(end)}], 'dimensions': dims,
            'metrics': [m['source_field'] for m in report['metrics']], 'limit': 10000, 'offset': 0,
            'return_property_quota': True}
    if expressions:
        body['dimension_filter'] = expressions[0] if len(expressions) == 1 else {'and_group': {'expressions': expressions}}
    if dims:
        body['order_bys'] = [{'dimension': {'dimension_name': d}} for d in dims]
    if report['source'] == 'ga4_funnel':
        body = json.loads((ROOT / 'queries/seven-day-funnel.json').read_text())
        body['dateRanges'] = [{'startDate': str(start), 'endDate': str(end)}]
    return body


def payload_from_mcp(result):
    """The official MCP returns proto_to_dict(response) as structured or text JSON."""
    candidates = []
    structured = result.get('structuredContent')
    if isinstance(structured, dict):
        candidates += [structured, structured.get('result')]
    for block in result.get('content', []):
        if block.get('type') == 'text':
            try:
                candidates.append(json.loads(block['text']))
            except (KeyError, json.JSONDecodeError):
                pass
    for candidate in candidates:
        if isinstance(candidate, dict) and ('row_count' in candidate or 'rows' in candidate or 'dimension_headers' in candidate):
            return candidate
    raise SyncError('report payload missing')


def pick(obj, *names, default=None):
    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj[name]
    return default


def parse_number(text, value_type):
    try:
        value = float(text)
    except (TypeError, ValueError):
        raise SyncError('metric value is not a number')
    if not math.isfinite(value) or value < 0:
        raise SyncError('metric value must be finite and non-negative')
    if value_type == 'integer':
        if value != int(value) or abs(value) > 2 ** 53:
            raise SyncError('integer metric is not an exact integer')
        return int(value)
    return value


def cells_from_report(task, pages):
    """Validate headers, rows and pagination; return (cells, source_row_count, quality)."""
    report, dims = task.report, task.dims
    metrics = report['metrics']
    rows, row_count, quality = [], None, {}
    for page in pages:
        dim_headers = [pick(h, 'name') for h in pick(page, 'dimension_headers', 'dimensionHeaders', default=[])]
        met_headers = [pick(h, 'name') for h in pick(page, 'metric_headers', 'metricHeaders', default=[])]
        page_rows = pick(page, 'rows', default=[]) or []
        if page_rows and (dim_headers != dims or met_headers != [m['source_field'] for m in metrics]):
            raise SyncError('response headers differ from the definition')
        rows += page_rows
        row_count = int(pick(page, 'row_count', 'rowCount', default=0) or 0)
        metadata = pick(page, 'metadata', default={}) or {}
        quality = {'metadata': metadata, 'property_quota': pick(page, 'property_quota', 'propertyQuota', default=None),
                    'note': 'MCP proto_to_dict may materialize default fields; absent wire fields are not proven false'}
    if row_count is not None and len(rows) < row_count:
        return None, row_count, quality
    cells, seen = [], set()
    for row in rows:
        values = [pick(v, 'value') for v in pick(row, 'dimension_values', 'dimensionValues', default=[])]
        metric_values = [pick(v, 'value') for v in pick(row, 'metric_values', 'metricValues', default=[])]
        if len(values) != len(dims) or len(metric_values) != len(metrics):
            raise SyncError('row shape differs from headers')
        dims_json = canon(dict(zip(dims, values)))
        if dims_json in seen:
            raise SyncError('duplicate dimension row')
        seen.add(dims_json)
        for metric, text in zip(metrics, metric_values):
            cells.append(dict(dimensions_json=dims_json, metric_key=metric['metric_key'],
                              value_num=parse_number(text, metric['value_type'])))
    return cells, row_count, quality


def cells_from_funnel(response):
    """RUNBOOK bounded reading: visualization step1/step2 activeUsers only."""
    visual = pick(response, 'funnelVisualization', 'funnel_visualization')
    if not isinstance(visual, dict):
        raise SyncError('funnel visualization missing')
    dim_headers = [pick(h, 'name') for h in pick(visual, 'dimensionHeaders', 'dimension_headers', default=[])]
    met_headers = pick(visual, 'metricHeaders', 'metric_headers', default=[])
    if dim_headers != ['funnelStepName'] or not met_headers or any(
            pick(h, 'name') != 'activeUsers' or pick(h, 'type', 'type_') not in ('TYPE_INTEGER', None) for h in met_headers):
        raise SyncError('funnel visualization headers differ from the accepted shape')
    names = [step['name'] for step in json.loads((ROOT / 'queries/seven-day-funnel.json').read_text())['funnel']['steps']]
    values = {}
    for row in pick(visual, 'rows', default=[]) or []:
        dims = pick(row, 'dimensionValues', 'dimension_values', default=[])
        mets = pick(row, 'metricValues', 'metric_values', default=[])
        if len(dims) != 1 or len(mets) != 1:
            raise SyncError('funnel row shape differs')
        label = pick(dims[0], 'value')
        matched = [i for i, name in enumerate(names) if label == name or label == f'{i + 1}. {name}']
        if len(matched) != 1 or matched[0] in values:
            raise SyncError('funnel step names differ')
        values[matched[0]] = parse_number(pick(mets[0], 'value'), 'integer')
    if not values:
        return [], {'metadata': pick(response, 'metadata', default={})}
    if set(values) != {0, 1} or values[1] > values[0]:
        raise SyncError('funnel steps violate step2 <= step1')
    cells = [dict(dimensions_json='{}', metric_key='step1_users', value_num=values[0]),
             dict(dimensions_json='{}', metric_key='step2_users', value_num=values[1])]
    return cells, {'metadata': pick(response, 'metadata', default={}), 'note': 'table headers are redundant upstream; visualization only'}


class GaClient:
    """One official MCP session for all report calls; REST only for the timed funnel."""

    def __init__(self):
        import read
        self.read = read
        self.calls = 0

    async def __aenter__(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        config = json.loads((ROOT.parents[1] / '.agents/plugins/ga4-reader/mcp.json').read_text())['mcpServers']['ga4-reader']
        if self.read.PIN not in ' '.join(config['args']):
            raise SyncError('MCP configuration pin differs from verified reader')
        params = StdioServerParameters(command=config['command'], args=config['args'], env=self.read.environment())
        self._stdio = stdio_client(params)
        reader, writer = await self._stdio.__aenter__()
        self._session = ClientSession(reader, writer)
        await self._session.__aenter__()
        await self._session.initialize()
        return self

    async def __aexit__(self, *exc):
        await self._session.__aexit__(*exc)
        await self._stdio.__aexit__(*exc)

    async def report(self, body):
        self.calls += 1
        result = await self._session.call_tool('run_report', dict(body, property_id=self.read.PROPERTY))
        checked = self.read.checked_mcp_result(result.model_dump(mode='json', exclude_none=True))
        return payload_from_mcp(checked)

    async def property(self):
        self.calls += 1
        result = await self._session.call_tool('get_property_details', {'property_id': self.read.PROPERTY})
        self.read.checked_mcp_result(result.model_dump(mode='json', exclude_none=True))

    def funnel(self, body):
        self.calls += 1
        return self.read.rest_read('runFunnelReport', body)


async def fetch_ga(task, client):
    """Return a result dict: status, cells, request, quality, counts."""
    body = ga_request(task.report, task.variant, task.start, task.end)
    if task.report['source'] == 'ga4_funnel':
        response = await asyncio.to_thread(client.funnel, body)
        cells, quality = cells_from_funnel(response)
        return dict(status='ok' if cells else 'empty', cells=cells, request=body, quality=quality,
                    source_row_count=len(cells) // 2, page_count=1, payload_hash=sha(canon(response)))
    pages, offset = [], 0
    while True:
        if len(pages) >= REPORT_CALL_LIMIT:
            return dict(status='incomplete', cells=[], request=body, quality={}, source_row_count=None,
                        page_count=len(pages), payload_hash=None, reason_code='call_limit')
        page = await client.report(dict(body, offset=offset))
        pages.append(page)
        returned = len(pick(page, 'rows', default=[]) or [])
        total = int(pick(page, 'row_count', 'rowCount', default=0) or 0)
        offset += returned
        if offset >= total or returned == 0:
            break
    cells, row_count, quality = cells_from_report(task, pages)
    if cells is None:
        return dict(status='incomplete', cells=[], request=body, quality=quality, source_row_count=row_count,
                    page_count=len(pages), payload_hash=sha(canon(pages)), reason_code='rows_short_of_row_count')
    return dict(status='ok' if cells else 'empty', cells=cells, request=body, quality=quality,
                source_row_count=row_count, page_count=len(pages), payload_hash=sha(canon(pages)))


# ---------------------------------------------------------------- product aggregates

def latest_product_artifact(workdir):
    """Download the newest successful daily-usage artifact. Returns (report, run_id) or raises."""
    listing = subprocess.run(['gh', 'run', 'list', '-R', PRODUCT_REPO, '--workflow', PRODUCT_WORKFLOW, '--status', 'success',
                              '--limit', '1', '--json', 'databaseId'], capture_output=True, text=True, timeout=60)
    if listing.returncode:
        raise SyncError('product workflow not available')
    runs = json.loads(listing.stdout or '[]')
    if not runs:
        raise SyncError('no successful product aggregate run yet')
    run_id = str(runs[0]['databaseId'])
    download = subprocess.run(['gh', 'run', 'download', run_id, '-R', PRODUCT_REPO, '-n', PRODUCT_ARTIFACT, '-D', str(workdir)],
                              capture_output=True, text=True, timeout=120)
    if download.returncode:
        raise SyncError('product artifact download failed')
    raw = (Path(workdir) / 'analytics-daily-usage.json').read_text()
    return raw, run_id


def product_results(raw, evidence, usable, today):
    """Turn the daily-usage JSON into run results. Days already stored keep their first complete snapshot."""
    report = json.loads(raw)
    if report.get('schema') != PRODUCT_SCHEMA:
        raise SyncError('unexpected product aggregate schema')
    start, end = dt.date.fromisoformat(report['start_date']), dt.date.fromisoformat(report['end_date'])
    if end >= today:
        raise SyncError('product aggregate includes an incomplete day')
    defs = {r['report_key']: r for r in DEFINITIONS['reports']}
    common = dict(source_retrieved_at=report['retrieved_at'], payload_hash=sha(raw), evidence_ref=evidence,
                  request={'workflow': PRODUCT_WORKFLOW, 'schema': PRODUCT_SCHEMA, 'start_date': str(start), 'end_date': str(end)},
                  quality={'scope': report.get('scope'), 'limitations': report.get('limitations')}, page_count=1)
    by_day = {}
    for section in ('signups', 'direct_requests_daily', 'automatic_daily'):
        for row in report[section]:
            by_day.setdefault((section, row['date']), []).append(row)
    results = []

    def add(key, variant, kind, period_start, period_end, rows, metric_fields, dims):
        task = Task(defs[key], variant, kind, period_start, period_end)
        if task.window_key in usable:
            return
        cells = []
        if variant == 'total':
            for field in metric_fields:  # disjoint partitions of an exact count; absence is zero
                cells.append(dict(dimensions_json='{}', metric_key=field, value_num=sum(r[field] for r in rows)))
        else:
            for row in rows:
                dims_json = canon({d: row[d] for d in dims})
                for field in metric_fields:
                    cells.append(dict(dimensions_json=dims_json, metric_key=field, value_num=row[field]))
        status = 'ok' if cells else 'empty'
        results.append((task, dict(common, status=status, cells=cells, source_row_count=len(rows))))

    for day in days(max(start, dt.date.fromisoformat(defs['P01']['fetch_start'])), end):
        iso = day.isoformat()
        signups = by_day.get(('signups', iso), [])
        requests = by_day.get(('direct_requests_daily', iso), [])
        automatic = by_day.get(('automatic_daily', iso), [])
        for variant in ('total', 'breakdown'):
            add('P01', variant, 'day', day, day, signups, ['accounts'], ['audience', 'auth_kind'])
            add('P02', variant, 'day', day, day, requests, ['accounts', 'requests'], ['audience', 'auth_kind'])
        add('P03', 'breakdown', 'day', day, day, automatic, ['events'], ['kind', 'audience'])
    windows = {}
    for row in report['direct_requests_windows']:
        windows.setdefault((row['window_start'], row['window_end']), []).append(row)
    for offset_start, offset_end in ((6, 0), (13, 7), (27, 0), (55, 28)):
        window = ((end - dt.timedelta(days=offset_start)).isoformat(), (end - dt.timedelta(days=offset_end)).isoformat())
        rows = windows.get(window, [])
        for variant in ('total', 'breakdown'):
            add('P02', variant, 'window', dt.date.fromisoformat(window[0]), dt.date.fromisoformat(window[1]), rows,
                ['accounts', 'requests'], ['audience', 'auth_kind'])
    return results


def growth_results(raw, evidence):
    """Operator growth-report JSON (C01 cohorts, C02 coverage counters)."""
    report = json.loads(raw)
    defs = {r['report_key']: r for r in DEFINITIONS['reports']}
    c01 = defs['C01']
    dims = c01['variants']['breakdown']
    metric_keys = [m['metric_key'] for m in c01['metrics']]
    counts = [m['metric_key'] for m in c01['metrics'] if m['unit'] == 'users']
    start, end = dt.date.fromisoformat(report['cohort_start']), dt.date.fromisoformat(report['cohort_end'])
    observed = dt.date.fromisoformat(report['observed_through'])
    quality = {k: report.get(k) for k in ('collection_start', 'excluded_dates', 'coverage_window_start', 'coverage_status', 'scope', 'limitations')}
    common = dict(source_retrieved_at=report['retrieved_at'], payload_hash=sha(raw), evidence_ref=evidence, quality=quality,
                  request={'source': 'analytics-growth-report.py', 'cohort_start': str(start), 'cohort_end': str(end),
                           'observed_through': str(observed), 'measurement_version': report.get('measurement_version')},
                  page_count=1)
    cells, seen = [], set()
    for row in report['cohorts']:
        dims_json = canon({d: row[d] for d in dims})
        if dims_json in seen:
            raise SyncError('duplicate cohort path')
        seen.add(dims_json)
        for key in counts:
            value = row[key]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise SyncError('cohort counts must be non-negative integers')
        for horizon in ('7', '14', '28'):
            if row['denominator' + horizon] + row['immature' + horizon] + row['consent_unavailable' + horizon] != row['registrations_observed']:
                raise SyncError('cohort partitions do not add up')
        for numerator, denominator in (('first_use7', 'denominator7'), ('first_result_ready7', 'denominator7'), ('first_result7', 'denominator7'),
                                       ('distinct_day_reuse7', 'denominator7'), ('next_week_use', 'denominator14'), ('retained28', 'denominator28')):
            if row[numerator] > row[denominator]:
                raise SyncError('cohort behaviour exceeds its denominator')
        for key in metric_keys:
            value = row.get(key)
            if value is None:
                cells.append(dict(dimensions_json=dims_json, metric_key=key, value_num=None, value_state='not_observed'))
            else:
                cells.append(dict(dimensions_json=dims_json, metric_key=key, value_num=parse_number(value, 'real' if key.endswith('seconds') else 'integer')))
    results = [(Task(c01, 'breakdown', 'cohort', start, end, observed), dict(common, status='ok' if cells else 'empty', cells=cells, source_row_count=len(report['cohorts'])))]
    by_day = {}
    for row in report.get('coverage', []):
        by_day.setdefault(row['date'], []).append(row)
    for iso, rows in sorted(by_day.items()):
        day_cells = [dict(dimensions_json=canon({'event_name': r['event_name'], 'outcome': r['outcome']}), metric_key='count',
                          value_num=parse_number(r['count'], 'integer')) for r in rows]
        day = dt.date.fromisoformat(iso)
        results.append((Task(defs['C02'], 'breakdown', 'day', day, day), dict(common, status='ok', cells=day_cells, source_row_count=len(rows))))
    return results


# ---------------------------------------------------------------- storage

def period_state(task, today):
    if task.report['source'].startswith('ga4'):
        excluded = set(DEFINITIONS['excluded_dates'])  # GA validation days only
        if any(d.isoformat() in excluded for d in days(task.start, task.end)):
            return 'validation'
        return 'eligible' if task.end <= today - dt.timedelta(days=DEFINITIONS['ga_delay_days']) else 'provisional'
    return 'eligible' if task.observed_through < today else 'provisional'


def store(db, results, batch_id, today, coverage):
    """writing -> values -> read back -> one UPDATE to terminal (spec 5.2)."""
    if not results:
        return {}
    requested = now_utc()
    runs, values, expected = [], [], {}
    for task, result in results:
        run_id = str(uuid.uuid4())
        key = (task.report['report_key'], task.report['definition_version'], task.variant)
        cov = coverage_snapshot(coverage.get(key, []), task.start, task.end)
        runs.append(dict(run_id=run_id, batch_id=batch_id, report_key=key[0], definition_version=key[1], variant=key[2],
                         window_key=task.window_key, period_kind=task.period_kind, period_start=task.start.isoformat(),
                         period_end=task.end.isoformat(), observed_through=task.observed_through.isoformat(),
                         requested_at=requested, finished_at=None, source_retrieved_at=result.get('source_retrieved_at'),
                         status='writing', period_state=period_state(task, today), coverage_snapshot_json=canon(cov),
                         request_json=canon(result.get('request', {})), quality_json=canon(result.get('quality', {})),
                         source_row_count=result.get('source_row_count'), page_count=result.get('page_count', 0),
                         payload_hash=result.get('payload_hash'), evidence_ref=result.get('evidence_ref'),
                         reason_code=result.get('reason_code'), safe_message=result.get('safe_message')))
        cells = result['cells'] if result['status'] in ('ok', 'empty') else []
        expected[run_id] = (result['status'], len(cells))
        for cell in cells:
            observed = cell.get('value_state', 'observed') == 'observed'
            values.append(dict(run_id=run_id, dimensions_key=sha(cell['dimensions_json']), metric_key=cell['metric_key'],
                               dimensions_json=cell['dimensions_json'], value_state='observed' if observed else cell['value_state'],
                               value_num=cell['value_num'] if observed else None, reason_code=cell.get('reason_code'), sample_size=None))
    insert_many(db, 'analytics_report_runs', list(runs[0]), runs)
    if values:
        insert_many(db, 'analytics_values', list(values[0]), values)
    ids = list(expected)
    stored = {}
    for i in range(0, len(ids), 200):
        part = ids[i:i + 200]
        for row in db.query('SELECT run_id, count(*) AS n FROM analytics_values WHERE run_id IN (' + ', '.join(q(x) for x in part) + ') GROUP BY run_id'):
            stored[row['run_id']] = row['n']
    final = {}
    for run_id, (status, count) in expected.items():
        final[run_id] = (status if stored.get(run_id, 0) == count else 'incomplete', stored.get(run_id, 0))
    finished = now_utc()
    for i in range(0, len(ids), 200):
        part = ids[i:i + 200]
        status_case = ' '.join(f'WHEN {q(r)} THEN {q(final[r][0])}' for r in part)
        count_case = ' '.join(f'WHEN {q(r)} THEN {final[r][1]}' for r in part)
        db.query(f"UPDATE analytics_report_runs SET status = CASE run_id {status_case} END, stored_cell_count = CASE run_id {count_case} END, "
                 f"finished_at = {q(finished)} WHERE status = 'writing' AND run_id IN ({', '.join(q(r) for r in part)})")
    summary = {}
    for status, _ in final.values():
        summary[status] = summary.get(status, 0) + 1
    return summary


def abandon_stale_writing(db):
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).isoformat(timespec='seconds').replace('+00:00', 'Z')
    db.query(f"UPDATE analytics_report_runs SET status = 'incomplete', finished_at = {q(now_utc())}, reason_code = 'abandoned_writing' "
             f"WHERE status = 'writing' AND requested_at < {q(cutoff)}")


def prune(db, today):
    """14-month retention (C02: 30 days). Values first, then runs."""
    month = today.month - DEFINITIONS['retention_months']
    year = today.year + (month - 1) // 12
    cutoff = dt.date(year, (month - 1) % 12 + 1, min(today.day, 28)).isoformat()
    c02 = (today - dt.timedelta(days=DEFINITIONS['c02_retention_days'])).isoformat()
    where = f"(period_end < {q(cutoff)} OR (report_key = 'C02' AND period_end < {q(c02)}))"
    db.query(f'DELETE FROM analytics_values WHERE run_id IN (SELECT run_id FROM analytics_report_runs WHERE {where})')
    db.query(f'DELETE FROM analytics_report_runs WHERE {where}')


def failed_result(reason, message):
    return dict(status='failed', cells=[], request={}, quality={}, reason_code=reason, safe_message=message)


# ---------------------------------------------------------------- commands

async def run_ga(tasks, results):
    """Preflight once; on auth failure record one failed run per report/variant instead of 100+."""
    try:
        async with GaClient() as client:
            await client.property()
            for task in tasks:
                if client.calls >= BATCH_CALL_LIMIT:
                    results.append((task, failed_result('batch_call_limit', 'Daily API call budget reached; retried next run')))
                    continue
                try:
                    results.append((task, await fetch_ga(task, client)))
                except SyncError as error:
                    results.append((task, failed_result('invalid_response', str(error))))
                except Exception as error:  # upstream text may contain credentials; keep only the type
                    results.append((task, failed_result('read_failed', f'{type(error).__name__}; not zero')))
    except Exception as error:
        seen = set()
        for task in tasks:
            key = (task.report['report_key'], task.variant)
            if key not in seen:
                seen.add(key)
                results.append((task, failed_result('ga_unavailable', f'GA reader unavailable ({type(error).__name__}); reauthentication may be required')))


def command_run(args):
    db = ChatDb(args.project_root) if not args.sqlite else SqliteDb(args.sqlite, args.migration)
    today = dt.date.fromisoformat(args.today) if args.today else jst_today()
    batch_id = str(uuid.uuid4())
    created = ensure_definitions(db)
    abandon_stale_writing(db)
    coverage = load_coverage(db)
    usable = usable_windows(db)
    results, notes = [], []
    if not args.skip_product:
        try:
            if args.product_file:
                raw, evidence = Path(args.product_file).read_text(), f'file:{Path(args.product_file).name}'
            else:
                with tempfile.TemporaryDirectory() as workdir:
                    raw, run_id = latest_product_artifact(workdir)
                evidence = f'github-actions:{PRODUCT_REPO}/{PRODUCT_WORKFLOW}#{run_id}'
            results += product_results(raw, evidence, usable, today)
        except SyncError as error:
            notes.append(f'product: {error}')
    if not args.skip_ga:
        tasks = plan_ga(today, usable)
        asyncio.run(run_ga(tasks, results))
    summary = store(db, results, batch_id, today, coverage)
    prune(db, today)
    print(json.dumps({'batch_id': batch_id, 'today_jst': str(today), 'definitions_created': created,
                      'runs': summary, 'notes': notes}, ensure_ascii=False))
    return 1 if summary.get('failed') or summary.get('incomplete') else 0


def command_import_growth(args):
    db = ChatDb(args.project_root) if not args.sqlite else SqliteDb(args.sqlite, args.migration)
    ensure_definitions(db)
    raw = Path(args.file).read_text()
    usable = usable_windows(db)
    results = [(t, r) for t, r in growth_results(raw, f'file:{Path(args.file).name}') if t.window_key not in usable]
    summary = store(db, results, str(uuid.uuid4()), jst_today(), load_coverage(db))
    print(json.dumps({'runs': summary}))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('run', 'import-growth'):
        command = sub.add_parser(name)
        command.add_argument('--project-root', type=Path)
        command.add_argument('--sqlite', help='local SQLite file instead of chat db (tests)')
        command.add_argument('--migration', help='migration to apply to a new SQLite file')
    sub.choices['run'].add_argument('--today', help='JST date override')
    sub.choices['run'].add_argument('--skip-ga', action='store_true')
    sub.choices['run'].add_argument('--skip-product', action='store_true')
    sub.choices['run'].add_argument('--product-file', help='daily-usage JSON instead of the GitHub artifact')
    sub.choices['import-growth'].add_argument('--file', required=True)
    args = parser.parse_args()
    if not args.sqlite and not args.project_root:
        parser.error('--project-root is required')
    return command_run(args) if args.command == 'run' else command_import_growth(args)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SyncError as error:
        print(json.dumps({'status': 'failed', 'reason': str(error)}), file=sys.stderr)
        sys.exit(1)
