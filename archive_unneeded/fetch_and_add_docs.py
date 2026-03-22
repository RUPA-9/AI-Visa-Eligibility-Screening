"""
Simple fetcher that reads `data/cleaned_policies/MISSING_DOCS_TO_FETCH.txt`,
attempts to GET each URL with a browser user-agent, extracts plain text,
and saves successful fetches into `data/cleaned_policies/` with sanitized filenames.
It also appends a fetch log to `data/cleaned_policies/FETCH_NOTES_urls_to_add.txt`.

Run from repository root: `python src/fetch_and_add_docs.py`
"""
import os
import re
import sys
import time
from urllib.parse import urlparse

try:
    import requests
except Exception:
    print("The 'requests' library is required. Install it in your environment and retry.")
    sys.exit(2)

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except Exception:
    BS4_AVAILABLE = False

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CLEANED_DIR = os.path.join(BASE_DIR, 'data', 'cleaned_policies')
MISSING_FILE = os.path.join(CLEANED_DIR, 'MISSING_DOCS_TO_FETCH.txt')
FETCH_NOTES = os.path.join(CLEANED_DIR, 'FETCH_NOTES_urls_to_add.txt')

os.makedirs(CLEANED_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

TIMEOUT = 20


def sanitize_filename(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'https?://', '', s)
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s)
    s = s.strip('_')
    return s[:150] + '.txt'


def html_to_text(html: str) -> str:
    if BS4_AVAILABLE:
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(['script', 'style', 'noscript']):
            script.extract()
        text = soup.get_text(separator='\n')
        lines = [line.strip() for line in text.splitlines()]
        text = '\n'.join([l for l in lines if l])
        return text
    # fallback: crude tag stripper
    text = re.sub(r'<(script|style).*?>.*?</\1>', '', html, flags=re.S|re.I)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'\n\s+\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def append_fetch_note(url, status, note=''):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(FETCH_NOTES, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {url} -> {status}\n")
        if note:
            f.write(f"    {note}\n")


def main():
    if not os.path.exists(MISSING_FILE):
        print('Missing file not found:', MISSING_FILE)
        sys.exit(1)

    with open(MISSING_FILE, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

    urls = lines
    if not urls:
        print('No URLs to fetch in', MISSING_FILE)
        sys.exit(0)

    successes = []
    failures = []

    for url in urls:
        print('\nFetching:', url)
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        except Exception as e:
            print('  Request failed:', e)
            append_fetch_note(url, 'REQUEST_FAILED', str(e))
            failures.append((url, str(e)))
            continue

        status = r.status_code
        if status != 200:
            note = f'Status {status}';
            # log the final URL in case of redirects
            final = r.url
            if final and final != url:
                note += f' (final: {final})'
            print('  Non-200 status:', status)
            append_fetch_note(url, 'NON_200', note)
            failures.append((url, note))
            continue

        content_type = r.headers.get('content-type', '')
        if 'text' not in content_type and 'html' not in content_type:
            note = f'Content-Type: {content_type}'
            print('  Unexpected content-type:', content_type)
            append_fetch_note(url, 'UNEXPECTED_CONTENT_TYPE', note)
            failures.append((url, note))
            continue

        text = html_to_text(r.text)
        if len(text) < 200:
            note = 'Fetched content too short after cleaning'
            print('  Warning:', note)
            append_fetch_note(url, 'TOO_SHORT', note)
            # still save for manual inspection

        filename = sanitize_filename(url)
        outpath = os.path.join(CLEANED_DIR, filename)
        try:
            with open(outpath, 'w', encoding='utf-8') as out:
                out.write(text)
            print('  Saved to', outpath)
            append_fetch_note(url, 'SAVED', outpath)
            successes.append((url, outpath))
        except Exception as e:
            print('  Failed to save file:', e)
            append_fetch_note(url, 'SAVE_FAILED', str(e))
            failures.append((url, str(e)))

    # Summary
    print('\nFetch summary:')
    print('  Successes:', len(successes))
    for u, p in successes:
        print('   -', u, '->', p)
    print('  Failures:', len(failures))
    for u, note in failures:
        print('   -', u, '->', note)


if __name__ == '__main__':
    main()
