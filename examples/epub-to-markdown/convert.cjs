// Narrow adapter for chapter-based English EPUBs; rejects books without CHAPTER headings.
// Dependencies are resolved from the caller's isolated npm project.
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const local = createRequire(path.join(process.cwd(), 'package.json'));
const { parseEpub } = local('epub2md');
const { JSDOM } = local('jsdom');
const [source, output] = process.argv.slice(2);
if (!source || !output) throw new Error('Usage: node convert.cjs book.epub new-output-directory');
if (fs.existsSync(output)) throw new Error('Use a new output directory; existing output will not be overwritten.');
const book = parseEpub(source);
const chapters = [];
for (const section of book.sections) {
  const doc = new JSDOM(section.htmlString).window.document;
  const heading = [...doc.querySelectorAll('h1,h2,h3')].find(h => /^CHAPTER\s+[IVXLCDM]+[.\s]/i.test(h.textContent.trim()));
  if (!heading) continue;
  const title = heading.textContent.replace(/\s+/g, ' ').trim();
  const name = String(chapters.length + 1).padStart(2, '0') + '-' + title.replace(/[^a-z0-9]+/gi, '-').replace(/-$/, '') + '.md';
  chapters.push({ sourceId: section.id, title, name, markdown: section.toMarkdown() });
}
if (!chapters.length) throw new Error('No supported chapter headings; refusing to guess.');
fs.mkdirSync(output, { recursive: true });
for (const ch of chapters) fs.writeFileSync(path.join(output, ch.name), ch.markdown, 'utf8');
fs.writeFileSync(path.join(output, 'index.json'), JSON.stringify(chapters.map(({markdown, ...rest}) => rest), null, 2));
console.log(`Wrote ${chapters.length} chapters in EPUB spine order. Cover, navigation and publisher boilerplate excluded.`);
