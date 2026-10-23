"""Independent ZIP/XML reference versus rendered Markdown. Requires markdown-it-py."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import sys
import unicodedata
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile
from markdown_it import MarkdownIt


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'h1', 'h2', 'h3', 'br', 'li', 'div'): self.parts.append(' ')
    def handle_endtag(self, tag):
        if tag in ('p', 'h1', 'h2', 'h3', 'li', 'div'): self.parts.append(' ')
    def handle_data(self, text):
        self.parts.append(text)


def words(text):
    # Compare word order, retaining case and apostrophe-separated words; typography excluded.
    return re.findall(r'[^\W_]+', unicodedata.normalize('NFKC', text), flags=re.UNICODE)


def verify(source, output):
    expected = []
    with zipfile.ZipFile(source) as z:
        container = ET.fromstring(z.read('META-INF/container.xml'))
        opf = next(x.get('full-path') for x in container.iter() if x.tag.endswith('}rootfile'))
        root = ET.fromstring(z.read(opf))
        manifest = {x.get('id'): x for x in root.iter() if x.tag.endswith('}item')}
        for ref in root.iter():
            if not ref.tag.endswith('}itemref'): continue
            item = manifest[ref.get('idref')]
            filename = posixpath.normpath(posixpath.join(posixpath.dirname(opf), unquote(item.get('href'))))
            doc = ET.fromstring(z.read(filename))
            heading = next((x for x in doc.iter() if x.tag.split('}')[-1] in ('h1','h2','h3')
                            and re.match(r'CHAPTER\s+[IVXLCDM]+[.\s]', ''.join(x.itertext()).strip())), None)
            if heading is None: continue
            body = next(x for x in doc.iter() if x.tag.endswith('}body'))
            expected.append((ref.get('idref'), ' '.join(''.join(heading.itertext()).split()),
                             words(' '.join(body.itertext()))))
    index = json.loads((output / 'index.json').read_text(encoding='utf-8'))
    results = []
    for ref, entry in zip(expected, index):
        md = (output / entry['name']).read_text(encoding='utf-8')
        parser = VisibleText(); parser.feed(MarkdownIt().render(md))
        actual = words(''.join(parser.parts))
        match = actual == ref[2]
        results.append({'title': ref[1], 'source_id': ref[0], 'word_tokens': len(ref[2]),
                        'word_sequence_matches': match, 'title_matches': entry['title'] == ref[1],
                        'spine_order_matches': entry['sourceId'] == ref[0],
                        'navigation_absent': '## Contents' not in md})
        if not match:
            first = next((i for i,(a,b) in enumerate(zip(ref[2],actual)) if a != b), min(len(ref[2]),len(actual)))
            results[-1]['first_difference'] = {'index': first, 'source': ref[2][max(0,first-3):first+4], 'output': actual[max(0,first-3):first+4]}
    passed = len(expected) == len(index) == len(list(output.glob('*.md'))) == 12 and all(
        all(r[k] for k in ('word_sequence_matches','title_matches','spine_order_matches','navigation_absent')) for r in results)
    report = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'expected_chapters': len(expected), 'output_chapters': len(index),
              'status': 'passed' if passed else 'failed', 'chapters': results,
              'scope': 'One external book; exact normalized word sequences, not punctuation/layout equivalence or A/B model evaluation.'}
    (output / 'verification.json').write_text(json.dumps(report, indent=2, ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(verify(Path(sys.argv[1]), Path(sys.argv[2])))
