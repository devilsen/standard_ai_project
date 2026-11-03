#!/usr/bin/env python3
"""Bug JSON records: validate local facts and export summary/detail CSV without network writes."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from zoneinfo import ZoneInfo

STAGES = ('received', 'reproducing', 'diagnosing', 'fixing', 'targeted_verification',
          'pr_delivery', 'batch_verification', 'user_acceptance', 'staging_verification', 'delivered')
MILESTONES = ('targeted_verified', 'regression_added', 'case_verified', 'pr_created',
              'source_written', 'batch_verified', 'user_accepted', 'staging_verified', 'delivered')
EVENTS = ('stage_entered', 'blocked', 'unblocked', 'milestone', 'reopened')


def timestamp(value):
    """Require an explicit timezone; ambiguous local times would corrupt daily counts."""
    if not isinstance(value, str):
        raise ValueError('timestamp must be an ISO string')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timestamp must include timezone')
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(record):
    """Reject incomplete/malformed fact records rather than silently dropping them from totals."""
    require(isinstance(record, dict), 'record must be an object')
    require(record.get('schema_version') == 1, 'unsupported schema_version')
    for key in ('id', 'title', 'project', 'created_at'):
        require(isinstance(record.get(key), str) and bool(record[key].strip()), f'missing {key}')
    timestamp(record['created_at'])
    source = record.get('source')
    require(isinstance(source, dict) and bool(source.get('ref')) and bool(source.get('record_id')),
            'source.ref and source.record_id required')
    require(isinstance(record.get('reproduction'), dict), 'reproduction must be an object')
    require(record['reproduction'].get('level') in (None, 'A', 'B', 'C', 'D', 'E', 'F'),
            'invalid reproduction level')
    attribution = record.get('attribution')
    require(isinstance(attribution, dict), 'attribution required')
    for kind in ('technical', 'process'):
        items = attribution.get(kind)
        require(isinstance(items, list), f'attribution.{kind} must be a list')
        for item in items:
            require(isinstance(item, dict) and bool(item.get('category')), 'cause category required')
            require(item.get('status') in ('hypothesis', 'confirmed'), 'cause status required')
            require(isinstance(item.get('evidence'), list), 'cause evidence must be a list')
            require(item['status'] != 'confirmed' or bool(item['evidence']),
                    'confirmed attribution needs evidence')
    attempts = record.get('attempts')
    require(isinstance(attempts, list), 'attempts must be a list')
    rounds = set()
    for attempt in attempts:
        require(isinstance(attempt, dict), 'attempt must be an object')
        number = attempt.get('round')
        require(type(number) is int and number > 0 and number not in rounds, 'invalid/duplicate round')
        rounds.add(number)
        require(attempt.get('status') in ('running', 'failed', 'passed', 'unknown'), 'invalid attempt status')
        require(bool(attempt.get('hypothesis')) and bool(attempt.get('revision_ref')), 'attempt context required')
        if attempt.get('started_at') is None:
            require(bool(attempt.get('historical_evidence')), 'unknown start requires historical evidence')
            timestamp(attempt['observed_at'])
        else:
            timestamp(attempt['started_at'])
    events = record.get('events')
    require(isinstance(events, list) and bool(events), 'events required')
    ids = set()
    previous = timestamp(record['created_at'])
    for event in events:
        require(isinstance(event, dict) and event.get('id') and event['id'] not in ids, 'duplicate/missing event id')
        ids.add(event['id'])
        at = timestamp(event['at'])
        require(at >= previous, 'events must be chronological and not precede creation')
        previous = at
        kind = event.get('type')
        require(kind in EVENTS, 'invalid event type')
        if kind == 'stage_entered':
            require(event.get('stage') in STAGES, 'invalid stage')
        elif kind == 'blocked':
            require(bool(event.get('reason')) and bool(event.get('next_action')), 'blocker context required')
        elif kind == 'milestone':
            require(event.get('name') in MILESTONES, 'invalid milestone')
            require(event.get('result') in ('passed', 'failed', 'revoked'), 'invalid milestone result')
            require(isinstance(event.get('evidence'), list) and bool(event['evidence']), 'milestone evidence required')
        elif kind == 'reopened':
            require(bool(event.get('reason')), 'reopen reason required')
    require(events[0].get('type') == 'stage_entered' and events[0].get('stage') == 'received',
            'first event must enter received')
    require(isinstance(record.get('links'), dict), 'links object required')
    return record


def load_records(root):
    """Read all bug.json files; duplicate IDs and any bad record fail the complete report."""
    records = []
    ids = set()
    for path in sorted(Path(root).rglob('bug.json')):
        try:
            record = validate(json.loads(path.read_text(encoding='utf-8')))
            require(record['id'] not in ids, f'duplicate Bug ID: {record["id"]}')
        except (ValueError, KeyError, TypeError) as exc:
            raise ValueError(f'{path}: {exc}') from exc
        ids.add(record['id'])
        records.append((path, record))
    return records


def snapshot(record, as_of):
    """Derive current stage/blocker independently; reopening invalidates current success claims."""
    stage = 'received'
    entered = timestamp(record['created_at'])
    blocker = ''
    next_action = ''
    milestones = {}
    reopens = 0
    last = entered
    for event in record['events']:
        at = timestamp(event['at'])
        if at > as_of:
            continue
        last = at
        kind = event['type']
        if kind == 'stage_entered':
            stage, entered = event['stage'], at
        elif kind == 'blocked':
            blocker, next_action = event['reason'], event['next_action']
        elif kind == 'unblocked':
            blocker, next_action = '', ''
        elif kind == 'milestone':
            milestones[event['name']] = event
        elif kind == 'reopened':
            stage, entered = 'diagnosing', at
            blocker, next_action = '', ''
            milestones = {}
            reopens += 1
    attempts = [a for a in record['attempts']
                if timestamp(a.get('started_at') or a['observed_at']) <= as_of]
    def passed(name):
        return milestones.get(name, {}).get('result') == 'passed'
    return {'stage': stage, 'entered': entered, 'blocker': blocker, 'next_action': next_action,
            'milestones': milestones, 'reopens': reopens, 'attempts': attempts,
            'last': last, 'passed': passed}


def report(records, as_of, tz_name):
    """Expose all-Bug denominator alongside attempted-fix rates; never equate PRs with fixes."""
    zone = ZoneInfo(tz_name)
    today = as_of.astimezone(zone).date()
    rows, states = [], []
    for path, record in records:
        if timestamp(record['created_at']) > as_of:
            continue
        state = snapshot(record, as_of)
        states.append(state)
        rows.append({'bug_id': record['id'], 'title': record['title'], 'project': record['project'],
                     'stage': state['stage'], 'stage_entered_at': state['entered'].isoformat(),
                     'stage_hours': round((as_of-state['entered']).total_seconds()/3600, 2),
                     'blocker': state['blocker'], 'next_action': state['next_action'],
                     'attempts': len(state['attempts']), 'reopens': state['reopens'],
                     'targeted_verified': state['passed']('targeted_verified'),
                     'user_accepted': state['passed']('user_accepted'),
                     'staging_verified': state['passed']('staging_verified'),
                     'technical_causes': json.dumps(record['attribution']['technical'], ensure_ascii=False),
                     'process_causes': json.dumps(record['attribution']['process'], ensure_ascii=False),
                     'reproduction_level': record['reproduction'].get('level'),
                     'pr': record['links'].get('pr'), 'source': record['source']['ref'],
                     'source_record_id': record['source']['record_id'], 'local_record': str(path),
                     'updated_at': state['last'].isoformat()})
    total = len(states)
    verified = sum(s['passed']('targeted_verified') for s in states)
    attempted = sum(bool(s['attempts']) for s in states)
    fixed_attempted = sum(bool(s['attempts']) and s['passed']('targeted_verified') for s in states)
    metrics = []
    def add(metric, count, denominator=None):
        metrics.append({'metric': metric, 'count': count, 'denominator': denominator,
                        'rate': count/denominator if denominator else None,
                        'as_of': as_of.isoformat(), 'timezone': tz_name})
    add('total_bugs', total)
    add('targeted_verified_current', verified, total)
    add('targeted_verified_among_attempted', fixed_attempted, attempted)
    for milestone in ('user_accepted', 'staging_verified', 'delivered'):
        add(milestone+'_current', sum(s['passed'](milestone) for s in states), total)
    for milestone in ('targeted_verified', 'delivered'):
        count = 0
        for state in states:
            event = state['milestones'].get(milestone)
            if event and event['result'] == 'passed' and timestamp(event['at']).astimezone(zone).date() == today:
                count += 1
        add('today_'+milestone+'_still_valid', count)
    add('blocked_current', sum(bool(s['blocker']) for s in states))
    add('attempt_budget_exhausted_unverified', sum(len(s['attempts']) >= 5 and not s['passed']('targeted_verified') for s in states))
    add('reopened_bugs', sum(s['reopens'] > 0 for s in states), total)
    for stage in STAGES:
        add('stage:'+stage, sum(s['stage'] == stage for s in states))
    return {'summary': metrics, 'details': rows}


def write_csv(path, rows):
    """Escape spreadsheet formulas in user-supplied strings while preserving raw JSON facts."""
    headers = list(rows[0]) if rows else ['bug_id', 'title', 'stage']
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "'"+v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v
                             for k, v in row.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Existing Bug jobs root')
    parser.add_argument('--output', type=Path, help='New private export directory; never overwrites')
    parser.add_argument('--as-of', help='ISO timestamp with timezone; default now')
    parser.add_argument('--timezone', default='Asia/Shanghai')
    args = parser.parse_args()
    require(args.root.is_dir(), 'root must be an existing directory')
    data = report(load_records(args.root), timestamp(args.as_of) if args.as_of else datetime.now(timezone.utc), args.timezone)
    if args.output:
        require(not args.output.exists(), 'output already exists; choose a new directory')
        args.output.mkdir(parents=True)
        (args.output/'funnel.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        write_csv(args.output/'summary.csv', data['summary'])
        write_csv(args.output/'details.csv', data['details'])
    print(json.dumps({'bugs': len(data['details']), 'output': str(args.output) if args.output else None,
                      'summary': data['summary']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
