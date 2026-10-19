"""Durable P1-C HTTP reservations and single-use native Harbor Trial admission."""
import argparse
from contextlib import contextmanager, closing
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import time
import httpx

ORDER = ('Gold', 'A0', 'A1')
DATABASE = '/opt/harbor-venv/p1-budgets/p1-c-20261019-001.sqlite3'
RECOVERY_DATABASE = '/opt/harbor-venv/p1-budgets/p1-c-20261019-001-recovery-001.sqlite3'


class BudgetStop(BaseException):
    """Never enter SDK/Agent retry handlers after a budget or protocol violation."""


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Ledger:
    def __init__(self, path):
        self.path = Path(path)

    @classmethod
    def create(cls, path, policy):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        with closing(sqlite3.connect(path)) as db:
            db.executescript('''
                PRAGMA synchronous=FULL;
                CREATE TABLE policy (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL, halt TEXT);
                CREATE TABLE arms (arm TEXT PRIMARY KEY, trial TEXT UNIQUE, state TEXT NOT NULL,
                                   lease_hash TEXT, pid INTEGER, evidence TEXT);
                CREATE TABLE attempts (n INTEGER PRIMARY KEY AUTOINCREMENT, arm TEXT NOT NULL,
                    state TEXT NOT NULL, created REAL NOT NULL, input_estimate INTEGER NOT NULL,
                    http_status INTEGER, input_tokens INTEGER, cached_tokens INTEGER, output_tokens INTEGER,
                    error_type TEXT);
            ''')
            db.execute('INSERT INTO policy VALUES (1, ?, NULL)', (json.dumps(policy, sort_keys=True),))
            db.executemany('INSERT INTO arms(arm,trial,state) VALUES (?,?,?)',
                           [(arm, policy['trials'][arm], 'NEW') for arm in ORDER])
            db.commit()
        return cls(path)

    @staticmethod
    def zero_consumption_parent(path):
        path = Path(path)
        digest = sha(path)
        with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
            if (db.execute('SELECT count(*) FROM attempts').fetchone()[0] != 0 or
                db.execute("SELECT count(*) FROM arms WHERE state='RUNNING'").fetchone()[0] or
                db.execute("SELECT state,pid FROM arms WHERE arm='Gold'").fetchone() != ('STOPPED', None) or
                db.execute('SELECT halt FROM policy').fetchone()[0] != 'TRIAL_STOP_CONDITION'):
                raise BudgetStop('Recovery requires the stopped, zero-consumption pre-Agent failure')
            policy = json.loads(db.execute('SELECT data FROM policy').fetchone()[0])
        if sha(path) != digest:
            raise BudgetStop('Parent ledger changed during read-only inspection')
        return {'database': str(path), 'sha256': digest, 'counts': dict.fromkeys(ORDER, 0)}, policy

    @classmethod
    def create_recovery(cls, path, policy, parent):
        lineage, original = cls.zero_consumption_parent(parent)
        if policy.get('scope') != original.get('scope') or policy['budget'] != original['budget']:
            raise BudgetStop('Recovery cannot obtain a different scope or budget')
        return cls.create(path, dict(policy, recovered_from=lineage))

    @staticmethod
    def check_parent(policy):
        parent = policy.get('recovered_from')
        if parent and sha(parent['database']) != parent['sha256']:
            raise BudgetStop('Original ledger changed; cumulative budget cannot be guaranteed')

    @contextmanager
    def transaction(self):
        # mode=rw is deliberate: a missing/corrupt ledger must never recreate an empty budget.
        db = sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, timeout=5, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def policy(db):
        return json.loads(db.execute('SELECT data FROM policy WHERE id=1').fetchone()[0])

    @staticmethod
    def owner(db, arm, trial, lease, attached=True):
        row = db.execute('SELECT * FROM arms WHERE arm=?', (arm,)).fetchone()
        if (not row or row['trial'] != trial or row['state'] != 'RUNNING' or
            row['lease_hash'] != hashlib.sha256(lease.encode()).hexdigest() or
            (attached and row['pid'] != os.getpid())):
            raise BudgetStop('Trial lease is absent, consumed, or owned by another process')
        return row

    def begin(self, arm, trial):
        with self.transaction() as db:
            policy = self.policy(db)
            self.check_parent(policy)
            for path, expected in policy['files'].items():
                if sha(path) != expected:
                    raise BudgetStop('Frozen execution file changed')
            if db.execute('SELECT halt FROM policy').fetchone()[0]:
                raise BudgetStop('Experiment is permanently stopped')
            row = db.execute('SELECT * FROM arms WHERE arm=?', (arm,)).fetchone()
            if not row or row['trial'] != trial or row['state'] != 'NEW':
                raise BudgetStop('Trial already admitted; restart and repeat are forbidden')
            if db.execute("SELECT 1 FROM arms WHERE state='RUNNING'").fetchone():
                raise BudgetStop('Concurrent Trial admission is forbidden')
            for previous in ORDER[:ORDER.index(arm)]:
                if db.execute('SELECT state FROM arms WHERE arm=?', (previous,)).fetchone()[0] != 'DONE':
                    raise BudgetStop('Previous arm did not meet its continuation conditions')
            lease = secrets.token_hex(32)
            db.execute("UPDATE arms SET state='RUNNING',lease_hash=? WHERE arm=?",
                       (hashlib.sha256(lease.encode()).hexdigest(), arm))
        return lease

    def attach(self, arm, trial, lease):
        with self.transaction() as db:
            self.check_parent(self.policy(db))
            row = self.owner(db, arm, trial, lease, attached=False)
            if row['pid'] is not None:
                raise BudgetStop('A process already attached; restarting cannot obtain a new budget')
            db.execute('UPDATE arms SET pid=? WHERE arm=?', (os.getpid(), arm))

    def reserve(self, arm, trial, lease, input_estimate):
        with self.transaction() as db:
            policy = self.policy(db)
            self.check_parent(policy)
            if db.execute('SELECT halt FROM policy').fetchone()[0]:
                raise BudgetStop('Experiment stopped after an unknown or failed request')
            if db.execute('SELECT count(*) FROM attempts').fetchone()[0] >= 18:
                raise BudgetStop('Global HTTP limit 18 reached')
            if db.execute('SELECT count(*) FROM attempts WHERE arm=?', (arm,)).fetchone()[0] >= 6:
                raise BudgetStop('Arm HTTP limit 6 reached')
            self.owner(db, arm, trial, lease)
            if db.execute("SELECT 1 FROM attempts WHERE state='RESERVED'").fetchone():
                raise BudgetStop('Concurrent or unknown in-flight request; no further dispatch allowed')
            used = db.execute('SELECT coalesce(sum(input_estimate),0) FROM attempts WHERE arm=?', (arm,)).fetchone()[0]
            budget = policy['budget']
            if (input_estimate < 0 or input_estimate > budget['max_input_tokens_per_request'] or
                used + input_estimate > budget['max_input_tokens_total']):
                raise BudgetStop('Persistent input Token budget reached')
            cursor = db.execute("INSERT INTO attempts(arm,state,created,input_estimate) VALUES (?,'RESERVED',?,?)",
                                (arm, time.time(), input_estimate))
            number = cursor.lastrowid
        # FULL synchronous commit completes before the caller can enter the network transport.
        return number

    def headers(self, number, status):
        with self.transaction() as db:
            db.execute('UPDATE attempts SET http_status=? WHERE n=?', (status, number))
            if not 200 <= status < 300:
                db.execute('UPDATE policy SET halt=?', ('HTTP_ERROR',))

    def response(self, number, usage):
        with self.transaction() as db:
            db.execute("UPDATE attempts SET state='RESPONDED',input_tokens=?,cached_tokens=?,output_tokens=? WHERE n=?",
                       (usage.prompt_tokens if usage else None, usage.cache_tokens if usage else None,
                        usage.completion_tokens if usage else None, number))

    def fail(self, number, error_type):
        with self.transaction() as db:
            if number is not None:
                db.execute("UPDATE attempts SET state='UNKNOWN',error_type=? WHERE n=?", (error_type, number))
            db.execute('UPDATE policy SET halt=?', (error_type,))

    def finish(self, arm, trial, lease, evidence):
        with self.transaction() as db:
            self.owner(db, arm, trial, lease, attached=False)
            pending = bool(db.execute("SELECT 1 FROM attempts WHERE state='RESERVED'").fetchone())
            halted = bool(db.execute('SELECT halt FROM policy').fetchone()[0])
            proceed = evidence['infra_ok'] and not pending and not halted
            if arm == 'Gold':
                proceed = proceed and evidence['task_success'] and evidence['skill_read']
            state = 'DONE' if proceed else 'STOPPED'
            db.execute('UPDATE arms SET state=?,evidence=? WHERE arm=?', (state, json.dumps(evidence), arm))
            if not proceed:
                db.execute('UPDATE policy SET halt=coalesce(halt,?)', ('TRIAL_STOP_CONDITION',))
        return proceed

    def snapshot(self):
        with self.transaction() as db:
            attempts = [dict(row) for row in db.execute('SELECT * FROM attempts ORDER BY n')]
            arms = [dict(row) for row in db.execute('SELECT arm,trial,state,pid,evidence FROM arms ORDER BY rowid')]
            halt = db.execute('SELECT halt FROM policy').fetchone()[0]
            lineage = self.policy(db).get('recovered_from')
        return {'recovered_from': lineage, 'arms': arms, 'attempts': attempts, 'global_reserved_attempts': len(attempts),
                'counts': {arm: sum(a['arm'] == arm for a in attempts) for arm in ORDER},
                'halt': halt, 'actual_cost': 'UNKNOWN',
                'count_note': 'Committed transport reservations include unknown pre-send/in-flight outcomes; never refunded.'}


class MeteredTransport(httpx.AsyncBaseTransport):
    """The only admitted model transport: reserve durably before httpcore handles the request."""
    def __init__(self, ledger, arm, trial, lease, inner=None):
        self.ledger, self.arm, self.trial, self.lease = ledger, arm, trial, lease
        self.inner = inner if inner is not None else httpx.AsyncHTTPTransport(
            retries=0, trust_env=False, http2=False, limits=httpx.Limits(max_connections=1, max_keepalive_connections=0))
        self.input_estimate = 0
        self.last_number = None

    async def handle_async_request(self, request):
        if request.method != 'POST' or str(request.url) != 'https://api.zhizengzeng.com/v1/chat/completions':
            raise BudgetStop('Unmetered model destination or method')
        data = json.loads(await request.aread())
        if (data.get('model') != 'gpt-5.4-mini-2026-03-17' or data.get('max_completion_tokens') != 2048 or
            data.get('temperature') != 0 or data.get('reasoning_effort') != 'none'):
            raise BudgetStop('Wire model or approved parameters changed')
        self.last_number = self.ledger.reserve(self.arm, self.trial, self.lease, self.input_estimate)
        try:
            response = await self.inner.handle_async_request(request)
        except BaseException as error:
            self.ledger.fail(self.last_number, type(error).__name__)
            raise BudgetStop('HTTP transport failed; reservation consumed') from None
        self.ledger.headers(self.last_number, response.status_code)
        return response

    async def aclose(self):
        await self.inner.aclose()


def ledger_for_profile(profile):
    path = profile['hard_http_budget']['database']
    if path not in (DATABASE, RECOVERY_DATABASE) or profile['budget']['max_requests'] != 6:
        raise BudgetStop('P1-C frozen six-request profile required')
    ledger = Ledger(path)
    with ledger.transaction() as db:
        policy = ledger.policy(db)
        ledger.check_parent(policy)
        if path == RECOVERY_DATABASE:
            parent = policy.get('recovered_from', {})
            if parent.get('database') != DATABASE or parent.get('counts') != dict.fromkeys(ORDER, 0):
                raise BudgetStop('Recovery ledger lacks the original zero-consumption allocation')
    return ledger


def trial_context(config_path):
    config = json.loads(Path(config_path).read_text())
    profile_path = Path(config['agent']['kwargs']['p1_profile'])
    profile = json.loads(profile_path.read_text())
    ledger = ledger_for_profile(profile)
    arm = json.loads(Path(config['agent']['kwargs']['p1_manifest']).read_text())['arm']
    return config, profile_path.parent, ledger, arm


def trial_evidence(config, root, arm):
    trial = Path(config['trials_dir']) / config['trial_name']
    try:
        native = json.loads((trial / 'result.json').read_text())
        summary = json.loads((trial / 'p1-observer/p1-summary.json').read_text())
        oracle = json.loads((trial / 'verifier/assertions.json').read_text())
        reward = native['verifier_result']['rewards']['reward']
        assertions = oracle['assertion_results']
        infra = (not native.get('exception_info') and native['verifier_environment_mode'] == 'separate' and
                 oracle.get('reason') is None and len(assertions) == 9 and reward in (0.0, 1.0) and
                 bool(all(assertions.values())) == (reward == 1.0) and not summary['stopped_before_model'])
        observed = []
        actions = trial / 'p1-observer/p1-tool-actions.jsonl'
        for line in actions.read_text().splitlines() if actions.exists() else []:
            event = json.loads(line)
            if event.get('actor') == 'model_tool' and event.get('stage') == 'observed':
                observed.extend(item['skill_id'] for item in event['read_events'])
        skill_read = bool(set(summary['model_read_ids']) & set(observed))
        return {'infra_ok': infra, 'task_success': reward == 1.0 and all(assertions.values()),
                'skill_read': skill_read, 'oracle_reward': reward, 'assertions': assertions,
                'trial_path': str(trial)}
    except (OSError, KeyError, ValueError, TypeError):
        return {'infra_ok': False, 'task_success': False, 'skill_read': False,
                'reason': 'Native result, observer evidence or Oracle is incomplete', 'trial_path': str(trial)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['begin', 'finish'])
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    config, root, ledger, arm = trial_context(args.config)
    if args.action == 'begin':
        if os.environ.get('P1_ALLOW_PAID') != '1':
            raise BudgetStop('Paid gate is unset')
        # Machine-readable lease is captured by the existing PowerShell launcher, never printed there.
        print(json.dumps({'lease': ledger.begin(arm, config['trial_name'])}))
        return 0
    evidence = trial_evidence(config, root, arm)
    proceed = ledger.finish(arm, config['trial_name'], os.environ.get('P1_BUDGET_LEASE', ''), evidence)
    (root / (arm + '-continuation.json')).write_text(json.dumps(evidence, indent=2) + '\n')
    snapshot = ledger.snapshot()
    (root / 'http-budget-ledger.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    print(json.dumps({'arm': arm, 'continuation_allowed': proceed, 'counts': snapshot['counts'],
                      'global_reserved_attempts': snapshot['global_reserved_attempts'], 'evidence': evidence}))
    return 0 if proceed else 3


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except BudgetStop as error:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(error)}))
        raise SystemExit(3)
