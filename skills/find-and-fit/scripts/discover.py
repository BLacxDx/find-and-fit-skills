"""Read-only GitHub discovery. Python 3.10+, standard library only."""
import argparse
import base64
from datetime import datetime, timezone
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

MAX_RESPONSE = 8_000_000
MAX_FILE = 64_000


def api(path):
    request = Request('https://api.github.com' + path, headers={
        'User-Agent': 'find-and-fit-skills/0.1',
        'Accept': 'application/vnd.github+json',
    })
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read(MAX_RESPONSE + 1)
        if len(raw) > MAX_RESPONSE:
            raise ValueError('GitHub response exceeds size limit; use a narrower candidate.')
        return json.loads(raw)
    except HTTPError as exc:
        raise ValueError(f'GitHub HTTP {exc.code}; evidence unavailable. '
                         'Check repository visibility or rate limits; no automatic retry.') from None
    except (URLError, TimeoutError) as exc:
        raise ValueError('GitHub unavailable; no conclusions about candidate absence.') from exc


def summary(repo):
    return {key: repo.get(key) for key in (
        'full_name', 'html_url', 'description', 'stargazers_count',
        'pushed_at', 'archived', 'license', 'default_branch')}


def search(query, limit):
    if not 1 <= limit <= 10:
        raise ValueError('limit must be between 1 and 10')
    result = api('/search/repositories?' + urlencode({'q': query, 'per_page': limit}))
    return {'query': query, 'total_count': result['total_count'],
            'incomplete_results': result.get('incomplete_results', False),
            'candidates': [summary(item) for item in result['items']]}


def read_blob(repo, sha, entry):
    path = entry['path']
    result = {'path': path, 'url': f'https://github.com/{repo}/blob/{sha}/{quote(path)}'}
    if entry.get('size', MAX_FILE + 1) > MAX_FILE:
        return {**result, 'skipped': 'file exceeds 64 KB limit'}
    blob = api(f'/repos/{repo}/git/blobs/{entry["sha"]}')
    if blob.get('encoding') != 'base64':
        return {**result, 'skipped': 'unsupported encoding'}
    data = base64.b64decode(blob['content'], validate=False)
    if len(data) > MAX_FILE:
        return {**result, 'skipped': 'decoded file exceeds 64 KB limit'}
    return {**result, 'untrusted_content': data.decode('utf-8', errors='replace')}


def inspect(repo, skill_path=None):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('repository must be owner/name, not a URL')
    metadata = api(f'/repos/{repo}')
    commit = api(f'/repos/{repo}/commits/{quote(metadata["default_branch"], safe="")}')
    sha = commit['sha']
    tree = api(f'/repos/{repo}/git/trees/{sha}?recursive=1')
    files = [item for item in tree['tree'] if item.get('type') == 'blob'
             and item.get('mode') != '120000']
    skills = [item for item in files if item['path'].split('/')[-1] == 'SKILL.md']
    selected = [item for item in skills if item['path'] == skill_path] if skill_path else skills[:3]
    if skill_path and not selected:
        raise ValueError('Requested SKILL.md not found in returned tree (which may be truncated).')
    readme = next((item for item in files if item['path'].lower() == 'readme.md'), None)
    return {'repository': summary(metadata), 'commit': sha,
            'tree_truncated': tree.get('truncated', False),
            'skill_paths': [item['path'] for item in skills],
            'skills_not_read': len(skills) - len(selected),
            'files': [read_blob(repo, sha, item) for item in selected + ([readme] if readme else [])],
            'notice': 'Source evidence only; no candidate code executed. Missing license or truncated tree is not proof of absence.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    find = commands.add_parser('search')
    find.add_argument('query')
    find.add_argument('--limit', type=int, default=5)
    check = commands.add_parser('inspect')
    check.add_argument('repo')
    check.add_argument('--skill-path')
    args = parser.parse_args()
    try:
        result = search(args.query, args.limit) if args.command == 'search' else inspect(args.repo, args.skill_path)
        result['checked_at'] = datetime.now(timezone.utc).isoformat()
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (ValueError, KeyError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
