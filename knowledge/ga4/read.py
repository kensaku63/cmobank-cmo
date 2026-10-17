#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-auth==2.62.0", "requests==2.34.2", "mcp==1.30.0"]
# ///
"""Read-only GA adapter: official MCP for reports; REST for timed funnels/metadata.
Run with uv run --with google-auth --with requests --with mcp read.py ...
No credentials, bearer headers, or raw exceptions are printed.
"""
import argparse
import asyncio
import datetime as dt
import json
import os
from pathlib import Path
import sys

PROPERTY = '559259561'
PIN = '75c0e1be8322e5eaa5c2e3ef7e79cf4760060f9a'
ROOT = Path(__file__).parent

class ReadFailure(Exception):
    pass


def environment():
    env = dict(os.environ)
    env.pop('GOOGLE_CLOUD_QUOTA_PROJECT', None)
    env['GOOGLE_APPLICATION_CREDENTIALS'] = env.get('GOOGLE_APPLICATION_CREDENTIALS', str(Path.home() / '.config/aachat-ga-reader/application_default_credentials.json'))
    return env


async def mcp_read(tool, arguments):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    # This is the official server, unmodified; no private replacement MCP.
    config = json.loads((ROOT.parents[1] / '.agents/plugins/ga4-reader/mcp.json').read_text())['mcpServers']['ga4-reader']
    if PIN not in ' '.join(config['args']):
        raise ReadFailure('MCP configuration pin differs from verified reader')
    params = StdioServerParameters(command=config['command'], args=config['args'], env=environment())
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments)
            if result.isError:
                raise ReadFailure('MCP tool failed (not a zero result)')
            return result.model_dump(mode='json', exclude_none=True)


def rest_read(method, body):
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    creds, _ = google.auth.load_credentials_from_file(environment()['GOOGLE_APPLICATION_CREDENTIALS'], scopes=['https://www.googleapis.com/auth/analytics.readonly'])
    creds = creds.with_quota_project(None)
    session = AuthorizedSession(creds)
    if method == 'metadata':
        response = session.get(f'https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY}/metadata', timeout=30)
    else:
        version = 'v1alpha' if method == 'runFunnelReport' else 'v1beta'
        response = session.post(f'https://analyticsdata.googleapis.com/{version}/properties/{PROPERTY}:{method}', json=body, timeout=30)
    if not response.ok:
        error = response.json().get('error', {})
        raise ReadFailure(f'GA API HTTP {response.status_code} {error.get("status", "error")} (not a zero result)')
    return response.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['property', 'dimensions', 'report', 'funnel', 'metadata', 'compatibility'])
    parser.add_argument('--request', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    body = json.loads(args.request.read_text()) if args.request else {}
    if args.operation in ('report', 'funnel', 'compatibility') and not args.request:
        parser.error('--request is required')
    if args.operation == 'funnel':
        steps = body['funnel']['steps']
        if body['funnel'].get('isOpenFunnel') is not False or len(steps) != 2 or steps[1].get('withinDurationFromPriorStep') != '604800s' or steps[1].get('isDirectlyFollowedBy') is not False:
            raise ValueError('Closed, indirect, seven-day funnel required')
    if args.dry_run:
        print(json.dumps({'property': PROPERTY, 'request': body}, indent=2)); return
    if args.operation in ('property', 'dimensions', 'report'):
        tool = {'property': 'get_property_details', 'dimensions': 'get_custom_dimensions_and_metrics', 'report': 'run_report'}[args.operation]
        if 'property_id' in body:
            raise ValueError('property fixed by reader')
        result = asyncio.run(mcp_read(tool, dict(body, property_id=PROPERTY)))
    else:
        method = {'funnel': 'runFunnelReport', 'metadata': 'metadata', 'compatibility': 'checkCompatibility'}[args.operation]
        result = rest_read(method, body)
    print(json.dumps({'property': PROPERTY, 'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'operation': args.operation, 'request': body, 'result': result}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Never echo library exception text that could contain authentication URLs.
        print(json.dumps({'status': 'failed', 'error_type': type(error).__name__, 'reason': str(error) if isinstance(error, ReadFailure) else 'Read failed; inspect configuration without printing credentials', 'data': None}), file=sys.stderr)
        sys.exit(1)
