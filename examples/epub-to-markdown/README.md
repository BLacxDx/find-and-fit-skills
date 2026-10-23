# Discovery-to-execution: EPUB to chapter Markdown

Tested on 2026-10-23, Windows, Node.js 22.16.0 and Python 3.12.10.

## Request and acceptance criteria

Convert a public English EPUB into chapter Markdown, in reading order, with chapter headings and body text preserved, excluding navigation pages. Conversion must run locally without a paid API. Installed skills did not directly cover EPUB chapter conversion. This is a representative task selected by the assistant, not external user feedback.

Input: [Project Gutenberg's Alice's Adventures in Wonderland](https://www.gutenberg.org/ebooks/11), [EPUB3 download](https://www.gutenberg.org/ebooks/11.epub3.images). This is an external book, not a selected tool's demonstration fixture. SHA-256 of the tested download: `4f81245d31380ac1d6eafb9a321e3691369bc70985736ae4bccf849a4f784036`. Gutenberg downloads can change; the verifier records the hash. The original EPUB is kept locally with its attribution and license information; neither the book nor its converted text is redistributed here.

## Search evidence

The current conversation explicitly read and followed Find and Fit. Search started without a named converter:

- Web query: `EPUB to markdown offline command line open source github`.
- Bundled helper query: `epub markdown in:name,description`, limit 5. GitHub returned 959 total matches, incomplete_results=false. Its first five results were uxiew/epub2MD, elixir-lang/ex_doc, johnpaulada/pandoc-markdown-book-template, firecrawl/anydoc and overcuriousity/pdf2epub.
- The web search surfaced mefengl/epub2md and danielcorsano/convertext among other tools. Only three candidate repositories were inspected in depth.

The reverse-direction book template and documentation generator were not treated as valid converters merely because their names matched the query.

| Candidate | Evidence and constraints | Decision |
| --- | --- | --- |
| [uxiew/epub2MD](https://github.com/uxiew/epub2MD/tree/f1a32a0cfc0213c7ede4fd79419b1dd4d08d26b4) | MIT; Node CLI; numbered section files; remote image downloads disabled by default. Windows behavior and navigation removal were unverified before execution. | Selected provisionally; registry identity checked, then executed. |
| [mefengl/epub2md](https://github.com/mefengl/epub2md/tree/2ba7a821094c1d5060516eec4b898c4febad65ff) | MIT; README requires Pandoc. Source also invokes external `unzip`; neither command was found on this Windows PATH. | Rejected for this low-setup task; not inherently unusable on Windows. |
| [danielcorsano/convertext](https://github.com/danielcorsano/convertext/tree/10ed05dd8605c8e423e73081b8dc9b6a9d79abdc) | MIT; native EPUB parser and Markdown conversion advertised. Separate chapter output not established from reviewed docs. | Not executed; less direct evidence for the requested output. |

Important registry distinction: PyPI `epub2md` and npm `epub2md` refer to different projects. `npm view epub2md repository version` linked the selected package to uxiew/epub2MD, version 1.6.4. Dependencies were installed locally with scripts disabled. No global package install or paid model call was needed. Network access was used for discovery, package installation and source download.

## What failed and how it was adapted

The unmodified npm CLI completed, but emitted an EPUB3 TOC parsing warning and wrote 15 Markdown files, including navigation and publisher material. Chapter filenames fell back to generated source names. This did not satisfy the chapter-only requirement.

The small [adapter](convert.cjs) uses the selected tool's public `parseEpub` and `section.toMarkdown()` APIs. It follows its spine-ordered sections, selects sections with English `CHAPTER` headings, and writes 12 clearly named files plus an index. It leaves the source EPUB unchanged. It does not patch or claim to repair the upstream TOC parser. This is a narrow adaptation, not a general EPUB cleanup solution; books without that heading convention need separate handling.

Before and after here means **unmodified tool versus adapted tool**, not model-without-skill versus model-with-skill.

## Independent output verification

[verify.py](verify.py) does not call epub2md. It reads the original ZIP container, OPF manifest/spine and XHTML with Python's standard library, renders the saved Markdown using markdown-it-py, and compares:

- Exactly 12 output chapter files and 12 chapter index entries.
- Chapter titles and sequence against the original EPUB spine.
- Exact normalized word-token sequences for every chapter: 27,336 tokens total.
- Navigation absence in the chapter output.

All passed. Two deliberate corruptions were rejected with nonzero exit codes: deleting one body word and swapping the first two chapter index entries. These negative checks show the verifier can detect those errors, not every possible defect.

Both the CLI run and adapted run used [block-network.cjs](block-network.cjs) to reject Node socket, HTTP(S), TLS and fetch calls. This is application-level blocking, not an OS firewall or a security audit. It supports the offline execution claim for these runs.

See [machine-readable results](result.json). Word comparison retains word order and case but normalizes Unicode and ignores punctuation/layout differences. It is not a pixel/layout comparison; illustration fidelity and arbitrary EPUB structures were not evaluated. The adapter and verifier were developed on this book, so there is no separate held-out validation set.

## Reproduce

Keep the repository checkout separate from a new evaluation directory. Run the following in that evaluation directory, substituting the path to this checkout's `examples/epub-to-markdown` folder for `CASE`:

```powershell
npm.cmd install --ignore-scripts --no-audit --no-fund --save-exact epub2md@1.6.4
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install markdown-it-py==4.2.0
Invoke-WebRequest https://www.gutenberg.org/ebooks/11.epub3.images -OutFile alice.epub
node --require CASE/block-network.cjs node_modules/epub2md/lib/bin/cli.cjs alice.epub
node --require CASE/block-network.cjs CASE/convert.cjs alice.epub chapters
.\.venv\Scripts\python.exe CASE/verify.py alice.epub chapters
```

Use a new `chapters` directory: the adapter refuses to overwrite an existing output. The original download and converted chapters are local artifacts; check the source's terms before redistribution. The repository pins direct package versions; transitive dependency resolution may change.

## What this demonstrates

In this conversation, the workflow found candidates through search, rejected a hidden runtime-dependency mismatch, selected and installed a registry-verified package, detected unsuitable output, and completed the task with a small adapter and source-derived checks. No installed skill supplied the EPUB converter.

This does not demonstrate statistically better recommendations than an ordinary assistant, independent users, broad adoption or general reliability. No separate agent sessions or paid API evaluations were run. Search relevance remains imperfect. The Skill gained one narrowly supported instruction: verify registry identity and inspect undeclared executable dependencies before installation.
