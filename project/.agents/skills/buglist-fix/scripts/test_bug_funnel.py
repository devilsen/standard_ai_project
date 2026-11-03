"""Verify funnel denominators, reopens, daily boundaries, invalid data and safe exports."""
import copy
import csv
from pathlib import Path
import tempfile
import unittest
from bug_funnel import validate, report, timestamp, load_records, write_csv


def bug(name='B1'):
    return {'schema_version': 1, 'id': name, 'title': 'Export', 'project': 'bidding',
            'created_at': '2026-11-02T15:00:00Z',
            'source': {'ref': 'https://example.invalid/bugs', 'record_id': name},
            'reproduction': {'level': None}, 'attribution': {'technical': [], 'process': []},
            'attempts': [], 'links': {},
            'events': [{'id': 'e1', 'type': 'stage_entered', 'stage': 'received', 'at': '2026-11-02T15:00:00Z'}]}


def milestone(r, name, at='2026-11-02T16:30:00Z'):
    r['events'].append({'id': str(len(r['events'])), 'type': 'milestone', 'name': name,
                        'result': 'passed', 'at': at, 'evidence': ['test-result']})


class FunnelTests(unittest.TestCase):
    def test_imported_attempts_preserve_budget_without_invented_start_or_success(self):
        r = bug()
        r['attempts'] = [{'round': i, 'status': 'unknown', 'started_at': None,
                          'observed_at': '2026-11-03T03:00:00Z', 'historical_evidence': ['old-pr'],
                          'hypothesis': 'historical repair', 'revision_ref': str(i)} for i in (1, 2)]
        result, metrics = self.summarize([r])
        self.assertEqual(result['details'][0]['attempts'], 2)
        self.assertEqual(metrics['attempt_budget_exhausted_unverified']['count'], 1)
        self.assertEqual(metrics['targeted_verified_current']['count'], 0)
        past = report([(Path('bug.json'), validate(r))], timestamp('2026-11-03T02:00:00Z'), 'Asia/Shanghai')
        self.assertEqual(past['details'][0]['attempts'], 0)
        r['attempts'][0]['historical_evidence'] = []
        with self.assertRaises(ValueError): validate(r)

    def summarize(self, records):
        result = report([(Path(str(i)), validate(r)) for i, r in enumerate(records)],
                        timestamp('2026-11-03T04:00:00Z'), 'Asia/Shanghai')
        return result, {m['metric']: m for m in result['summary']}

    def test_all_bug_denominator_and_pr_not_fix(self):
        records = [bug(str(i)) for i in range(11)]
        records[0]['attempts'] = [{'round': 1, 'status': 'passed', 'started_at': '2026-11-02T16:00:00Z',
                                   'hypothesis': 'state error', 'revision_ref': 'abc'}]
        milestone(records[0], 'targeted_verified')
        milestone(records[1], 'pr_created')
        _, metrics = self.summarize(records)
        self.assertEqual(metrics['targeted_verified_current']['denominator'], 11)
        self.assertAlmostEqual(metrics['targeted_verified_current']['rate'], 1/11)
        self.assertEqual(metrics['targeted_verified_among_attempted']['rate'], 1)
        self.assertEqual(metrics['staging_verified_current']['count'], 0)

    def test_reopen_invalidates_old_success_without_resetting_attempts(self):
        r = bug()
        r['attempts'] = [{'round': i, 'status': 'failed', 'started_at': '2026-11-02T16:00:00Z',
                          'hypothesis': 'cause', 'revision_ref': str(i)} for i in (1, 2)]
        milestone(r, 'targeted_verified')
        r['events'].extend([{'id': 'reopen', 'type': 'reopened', 'at': '2026-11-02T17:00:00Z', 'reason': 'same bug'},
                            {'id': 'stage2', 'type': 'stage_entered', 'stage': 'diagnosing', 'at': '2026-11-02T17:00:00Z'}])
        result, metrics = self.summarize([r])
        self.assertEqual(metrics['targeted_verified_current']['count'], 0)
        self.assertEqual(metrics['attempt_budget_exhausted_unverified']['count'], 1)
        self.assertEqual(result['details'][0]['attempts'], 2)

    def test_reopen_alone_returns_delivered_bug_to_diagnosis(self):
        r = bug()
        r['events'].append({'id': 'done', 'type': 'stage_entered', 'stage': 'delivered',
                            'at': '2026-11-02T16:00:00Z'})
        milestone(r, 'delivered')
        r['events'].append({'id': 'reopen', 'type': 'reopened',
                            'at': '2026-11-02T17:00:00Z', 'reason': 'regression'})
        result, metrics = self.summarize([r])
        self.assertEqual(result['details'][0]['stage'], 'diagnosing')
        self.assertEqual(metrics['delivered_current']['count'], 0)

    def test_blocker_does_not_replace_stage(self):
        r = bug()
        r['events'].append({'id': 'block', 'type': 'blocked', 'reason': 'missing_sample',
                            'next_action': 'read authorized sample', 'at': '2026-11-02T16:00:00Z'})
        result, metrics = self.summarize([r])
        self.assertEqual(metrics['stage:received']['count'], 1)
        self.assertEqual(metrics['blocked_current']['count'], 1)
        self.assertEqual(result['details'][0]['blocker'], 'missing_sample')

    def test_daily_shanghai_boundary_and_deduplicated_bug_count(self):
        r = bug()
        milestone(r, 'targeted_verified', '2026-11-02T15:59:00Z')
        _, old = self.summarize([r])
        self.assertEqual(old['today_targeted_verified_still_valid']['count'], 0)
        milestone(r, 'targeted_verified', '2026-11-02T16:01:00Z')
        milestone(r, 'targeted_verified', '2026-11-02T16:02:00Z')
        _, now = self.summarize([r])
        self.assertEqual(now['today_targeted_verified_still_valid']['count'], 1)

    def test_bad_record_and_unproven_attribution_rejected(self):
        for mutate in [lambda r: r['events'].append(copy.deepcopy(r['events'][0])),
                       lambda r: r.update(reproduction=[]),
                       lambda r: r.update(attempts=[None]),
                       lambda r: r.update(created_at='2026-11-02T00:00:00'),
                       lambda r: r['attribution']['technical'].append({'category': 'logic', 'status': 'confirmed', 'evidence': []})]:
            r = bug(); mutate(r)
            with self.assertRaises(ValueError): validate(r)

    def test_duplicate_ids_fail_report_instead_of_shrinking_denominator(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('a', 'b'):
                p = Path(tmp)/name; p.mkdir(); (p/'bug.json').write_text(json.dumps(bug()))
            with self.assertRaises(ValueError): load_records(tmp)

    def test_csv_does_not_execute_formula(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'rows.csv'
            write_csv(p, [{'title': '=HYPERLINK("bad")', 'count': 2}])
            with p.open(encoding='utf-8-sig') as f: row = next(csv.DictReader(f))
            self.assertTrue(row['title'].startswith("'="))
            self.assertEqual(row['count'], '2')


if __name__ == '__main__':
    unittest.main()
