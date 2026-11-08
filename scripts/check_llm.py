"""Check one loopback OpenAI-compatible model route without fallback."""
import argparse
import json
import os
import urllib.request
from urllib.parse import urlsplit


def local_url(value):
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or parsed.hostname not in ('127.0.0.1', 'localhost', '::1') or parsed.username or parsed.query or parsed.fragment:
        raise ValueError('Only a plain loopback URL is allowed')
    return value.rstrip('/')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Local API redirects are refused')


def request(base, path, data=None):
    headers = {'Content-Type': 'application/json'}
    key = os.getenv('LOCAL_LLM_API_KEY')
    if key:
        headers['Authorization'] = 'Bearer ' + key
    req = urllib.request.Request(local_url(base) + path,
                                 data=json.dumps(data).encode() if data is not None else None, headers=headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(req, timeout=120) as response:
        return json.load(response)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-url', default='http://127.0.0.1:18765/v1')
    ap.add_argument('--model')
    ap.add_argument('--chat', action='store_true')
    ap.add_argument('--tool-test', action='store_true')
    args = ap.parse_args()
    models = request(args.base_url, '/models')
    ids = [m['id'] for m in models.get('data', [])]
    if not ids:
        raise ValueError('No served models returned')
    print(json.dumps({'model_ids': ids}))
    if not (args.chat or args.tool_test):
        return
    if args.model not in ids:
        raise ValueError('Select an exact served model ID')
    messages = [{'role': 'user', 'content': 'Reply with a short greeting.'}]
    common = {'model': args.model, 'max_tokens': 256, 'temperature': 0}
    if args.chat:
        result = request(args.base_url, '/chat/completions', {**common, 'messages': messages})
        if not result['choices'][0]['message'].get('content'):
            raise ValueError('No text response')
        print('Text inference PASS')
    if args.tool_test:
        messages = [{'role': 'user', 'content': 'Call add_numbers once with a=2 and b=3, then report the tool result.'}]
        tools = [{'type': 'function', 'function': {'name': 'add_numbers', 'description': 'Add two integers',
                  'parameters': {'type': 'object', 'properties': {'a': {'type': 'integer'}, 'b': {'type': 'integer'}},
                                 'required': ['a', 'b'], 'additionalProperties': False}}}]
        result = request(args.base_url, '/chat/completions', {**common, 'messages': messages, 'tools': tools,
                         'tool_choice': {'type': 'function', 'function': {'name': 'add_numbers'}}})
        message = result['choices'][0]['message']
        calls = message.get('tool_calls', [])
        if len(calls) != 1 or calls[0]['function']['name'] != 'add_numbers':
            raise ValueError('Missing or unexpected structured tool call')
        values = json.loads(calls[0]['function']['arguments'])
        if values != {'a': 2, 'b': 3} or any(type(v) is not int for v in values.values()):
            raise ValueError('Unexpected tool arguments')
        messages += [message, {'role': 'tool', 'tool_call_id': calls[0]['id'], 'content': '5'}]
        result = request(args.base_url, '/chat/completions', {**common, 'messages': messages})
        if '5' not in (result['choices'][0]['message'].get('content') or ''):
            raise ValueError('Final answer does not contain the executed result')
        print('Structured tool round trip PASS')


if __name__ == '__main__':
    main()
