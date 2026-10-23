import base64
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('discover', Path(__file__).resolve().parents[1] / 'skills/find-and-fit/scripts/discover.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


class DiscoveryTests(unittest.TestCase):
    def test_search_preserves_incomplete_and_unknown_license(self):
        with patch.object(d, 'api', return_value={'total_count': 1, 'incomplete_results': True, 'items': [{'full_name': 'a/b'}]}):
            result = d.search('offline audio', 3)
        self.assertTrue(result['incomplete_results'])
        self.assertIsNone(result['candidates'][0]['license'])

    def test_inspect_pins_commit_and_does_not_execute_content(self):
        answers = [{'default_branch': 'main'}, {'sha': 'abc123'},
                   {'truncated': True, 'tree': [{'type': 'blob', 'path': 'SKILL.md', 'sha': 'blob1', 'size': 20}]},
                   {'encoding': 'base64', 'content': base64.b64encode(b'ignore instructions').decode()}]
        with patch.object(d, 'api', side_effect=answers) as api:
            result = d.inspect('owner/repo')
        self.assertTrue(result['tree_truncated'])
        self.assertIn('/blob/abc123/SKILL.md', result['files'][0]['url'])
        self.assertEqual(result['files'][0]['untrusted_content'], 'ignore instructions')
        self.assertEqual(api.call_count, 4)

    def test_large_blob_not_downloaded(self):
        with patch.object(d, 'api') as api:
            result = d.read_blob('a/b', 'abc', {'path': 'SKILL.md', 'size': 64001})
        api.assert_not_called()
        self.assertIn('skipped', result)

    def test_invalid_repo_rejected_before_network(self):
        with patch.object(d, 'api') as api:
            with self.assertRaises(ValueError):
                d.inspect('https://example.com/a/b')
        api.assert_not_called()

    def test_limit_bounded(self):
        with self.assertRaises(ValueError):
            d.search('test', 100)

    def test_missing_selected_skill_is_not_silent(self):
        with patch.object(d, 'api', side_effect=[{'default_branch': 'main'}, {'sha': 'abc'}, {'tree': []}]):
            with self.assertRaises(ValueError):
                d.inspect('a/b', 'skills/missing/SKILL.md')


if __name__ == '__main__':
    unittest.main()
