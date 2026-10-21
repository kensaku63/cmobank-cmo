"""Offline regression for MCP envelopes and the reader's CLI failure boundary.

Run: python3 -m unittest discover -s knowledge/ga4 -p 'test_read.py' -v
No credentials or network are used; authentication text is synthetic/redacted.
"""
import contextlib
import io
import json
import runpy
import sys
import unittest
from unittest.mock import patch

import read


def envelope(payload, **extra):
    return {'isError': False, 'content': [{'type': 'text', 'text': json.dumps(payload)}], **extra}


class ReaderTests(unittest.TestCase):
    def cli(self, result):
        out, err = io.StringIO(), io.StringIO()

        def invoke(coroutine):
            namespace = coroutine.cr_frame.f_globals
            coroutine.close()
            return namespace['checked_mcp_result'](result)

        code = 0
        with patch.object(sys, 'argv', ['read.py', 'property']), patch('asyncio.run', side_effect=invoke), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                runpy.run_path(read.__file__, run_name='__main__')
            except SystemExit as failure:
                code = failure.code
        return code, out.getvalue(), err.getvalue()

    def assert_failure(self, result):
        code, out, err = self.cli(result)
        self.assertEqual(code, 1)
        self.assertEqual(out, '')
        failure = json.loads(err)
        self.assertEqual(failure['status'], 'failed')
        self.assertIsNone(failure['data'])
        self.assertEqual(failure['error_type'], 'ReadFailure')
        self.assertNotIn('sensitive-auth-marker', err)
        self.assertIn('not a zero result', failure['reason'])

    def test_observed_503_reauthentication_shape(self):
        self.assert_failure(envelope({'error': '503 Reauthentication is needed. sensitive-auth-marker'}))

    def test_protocol_is_error(self):
        self.assert_failure(envelope({'message': 'sensitive-auth-marker'}, isError=True))

    def test_structured_error(self):
        self.assert_failure(envelope({}, structuredContent={'error': 'sensitive-auth-marker'}))

    def test_later_content_error(self):
        result = envelope({'rows': []})
        result['content'] += envelope({'error': 'sensitive-auth-marker'})['content']
        self.assert_failure(result)

    def test_normal_response(self):
        result = envelope({'rows': [{'metric_values': [{'value': '4'}]}], 'row_count': 1})
        code, out, err = self.cli(result)
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(json.loads(out)['result'], result)

    def test_normal_empty_rows(self):
        result = envelope({'rows': [], 'row_count': 0, 'metadata': {'empty_reason': 'NO_DATA'}})
        code, out, err = self.cli(result)
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(json.loads(out)['result'], result)


if __name__ == '__main__':
    unittest.main()
