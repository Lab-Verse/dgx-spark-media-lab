"""Finite loopback ComfyUI client. Validation is default; execution is explicit."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.request
import uuid
from check_llm import local_url, NoRedirect


def call(base, path, payload=None):
    request = urllib.request.Request(local_url(base) + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={'Content-Type': 'application/json'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=60) as response:
        return json.load(response)


def is_link(value):
    return isinstance(value, list) and len(value) == 2 and isinstance(value[0], str) and type(value[1]) is int


def validate_graph(graph, info=None):
    if not isinstance(graph, dict) or not graph or not all(isinstance(k, str) and k.isdigit() for k in graph):
        raise ValueError('Expected an API graph with numeric-string node IDs')
    dependencies = {}
    for key, node in graph.items():
        if not isinstance(node, dict) or not isinstance(node.get('inputs'), dict) or not isinstance(node.get('class_type'), str):
            raise ValueError('Malformed node: ' + key)
        deps = []
        if info is not None:
            if node['class_type'] not in info:
                raise ValueError('Node unavailable: ' + node['class_type'])
            schema = info[node['class_type']]['input']
            specs = {**schema.get('required', {}), **schema.get('optional', {})}
            if set(schema.get('required', {})) - set(node['inputs']):
                raise ValueError('Required inputs missing: ' + key)
            if set(node['inputs']) - set(specs):
                raise ValueError('Unknown inputs: ' + key)
        for name, value in node['inputs'].items():
            if is_link(value):
                if value[0] not in graph or value[1] < 0:
                    raise ValueError('Dangling/invalid link')
                deps.append(value[0])
                if info is not None:
                    source = graph[value[0]]['class_type']
                    if source not in info or value[1] >= len(info[source]['output']):
                        raise ValueError('Invalid source output slot')
            elif info is not None and isinstance(specs[name][0], list) and value not in specs[name][0]:
                raise ValueError(f'Unavailable choice at node {key}.{name}: {value}')
        dependencies[key] = deps
    visited, active = set(), set()
    def visit(key):
        if key in active:
            raise ValueError('Cyclic graph')
        if key in visited:
            return
        active.add(key)
        for dep in dependencies[key]:
            visit(dep)
        active.remove(key)
        visited.add(key)
    for key in dependencies:
        visit(key)


def save(path, receipt):
    temp = path.with_suffix('.incoming')
    temp.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    temp.replace(path)


def observe(base, prompt_id, path, receipt, timeout):
    deadline = time.monotonic() + timeout
    try:
        while time.monotonic() < deadline:
            result = call(base, '/history/' + prompt_id).get(prompt_id)
            if result:
                receipt['history'] = result
                status = result.get('status', {})
                if status.get('status_str') == 'success' and status.get('completed'):
                    receipt['state'] = 'completed'
                elif status.get('status_str') == 'error':
                    receipt['state'] = 'failed'
                else:
                    time.sleep(3)
                    continue
                save(path, receipt)
                print(json.dumps({'receipt': str(path), 'state': receipt['state'], 'outputs': result.get('outputs', {})}, indent=2))
                if receipt['state'] != 'completed':
                    raise SystemExit('Native job failed; inspect saved history.')
                return
            time.sleep(3)
    except (Exception, KeyboardInterrupt):
        receipt['state'] = 'outcome_unknown'
        save(path, receipt)
        raise
    receipt['state'] = 'outcome_unknown'
    save(path, receipt)
    raise SystemExit(f'Timed out. Job may still be running; observe {prompt_id}. Do not resubmit.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-url', default='http://127.0.0.1:8188')
    sub = ap.add_subparsers(dest='action', required=True)
    sub.add_parser('status')
    submit = sub.add_parser('submit')
    submit.add_argument('graph', type=Path)
    submit.add_argument('--receipts', type=Path, required=True)
    submit.add_argument('--execute', action='store_true')
    submit.add_argument('--timeout', type=int, default=3600)
    watch = sub.add_parser('observe')
    watch.add_argument('prompt_id')
    watch.add_argument('--receipt', type=Path, required=True)
    watch.add_argument('--timeout', type=int, default=3600)
    args = ap.parse_args()
    local_url(args.base_url)
    if args.action == 'status':
        queue = call(args.base_url, '/queue')
        print(json.dumps({'running': len(queue['queue_running']), 'pending': len(queue['queue_pending']),
                          'system': call(args.base_url, '/system_stats')}, indent=2))
        return
    if not 1 <= args.timeout <= 86400:
        ap.error('Timeout must be 1–86400 seconds')
    if args.action == 'observe':
        uuid.UUID(args.prompt_id)
        receipt = json.loads(args.receipt.read_text(encoding='utf-8'))
        if receipt.get('prompt_id') != args.prompt_id or receipt.get('base_url') != args.base_url:
            raise ValueError('Receipt does not match this job/endpoint')
        observe(args.base_url, args.prompt_id, args.receipt, receipt, args.timeout)
        return
    graph = json.loads(args.graph.read_text(encoding='utf-8'))
    validate_graph(graph, call(args.base_url, '/object_info'))
    if not args.execute:
        print('Schema/model choices validated. No job submitted. Add --execute to generate.')
        return
    queue = call(args.base_url, '/queue')
    if queue['queue_running'] or queue['queue_pending']:
        raise SystemExit('Queue busy. No job submitted.')
    args.receipts.mkdir(parents=True, exist_ok=True)
    path = args.receipts / (uuid.uuid4().hex + '.json')
    client_id = uuid.uuid4().hex
    receipt = {'base_url': args.base_url, 'graph': graph, 'client_id': client_id,
               'graph_sha256': hashlib.sha256(json.dumps(graph, sort_keys=True).encode()).hexdigest(),
               'state': 'prepared', 'submitted_unix': time.time()}
    save(path, receipt)
    # Mark uncertain before POST: a lost response must never trigger an automatic retry.
    receipt['state'] = 'submission_outcome_unknown'
    save(path, receipt)
    print(json.dumps({'receipt': str(path), 'client_id': client_id, 'state': receipt['state']}), flush=True)
    result = call(args.base_url, '/prompt', {'prompt': graph, 'client_id': client_id})
    if result.get('node_errors') or not result.get('prompt_id'):
        receipt.update(state='rejected', response=result)
        save(path, receipt)
        raise SystemExit('ComfyUI rejected the graph; see receipt.')
    receipt.update(prompt_id=result['prompt_id'], state='submitted')
    save(path, receipt)
    print(json.dumps({'prompt_id': receipt['prompt_id'], 'receipt': str(path)}), flush=True)
    observe(args.base_url, receipt['prompt_id'], path, receipt, args.timeout)


if __name__ == '__main__':
    main()
