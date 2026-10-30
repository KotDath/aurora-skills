"""Exercise server failures and package identity without network access."""
import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/flutter/aurora-flutter-add-dependency/scripts/check_dependency.py'
spec = importlib.util.spec_from_file_location('dependency_check', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class AdmissionTests(unittest.TestCase):
    def check(self, payload=None, error=None, offline=False):
        out = io.StringIO()
        response = io.StringIO(json.dumps(payload))
        with patch.object(sys, 'argv', [str(SCRIPT), '--package', 'yaml'] + (['--offline'] if offline else [])), patch.object(checker, 'urlopen', side_effect=error, return_value=response) as request, contextlib.redirect_stdout(out):
            checker.main()
        return json.loads(out.getvalue()), request

    def test_original_name_on_server_is_accepted(self):
        result, request = self.check({'name':'yaml','versions':[{'version':'3.1.4'}]})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['versions'], ['3.1.4'])
        self.assertEqual(request.call_args.args[0].full_url, checker.AURORA_PACKAGE_API+'yaml')

    def test_not_found_requires_source_review(self):
        result, _ = self.check(error=HTTPError('url',404,'not found',{},None))
        self.assertEqual(result['status'], 'needs_source_review')
        self.assertFalse(result['allowed'])

    def test_outage_is_unknown_not_absence(self):
        for error in [HTTPError('url',503,'unavailable',{},None), URLError('offline'), TimeoutError()]:
            with self.subTest(error=type(error).__name__):
                result, _ = self.check(error=error)
                self.assertEqual(result['status'], 'server_check_failed')
                self.assertIsNone(result['allowed'])

    def test_wrong_identity_or_empty_versions_are_unknown(self):
        for data in [{'name':'other','versions':[{'version':'1'}]}, {'name':'yaml','versions':[]}]:
            with self.subTest(data=data):
                result, _ = self.check(data)
                self.assertIsNone(result['allowed'])
                self.assertEqual(result['status'], 'server_check_failed')

    def test_offline_history_never_grants_admission(self):
        result, request = self.check(offline=True)
        self.assertIsNone(result['allowed'])
        request.assert_not_called()
