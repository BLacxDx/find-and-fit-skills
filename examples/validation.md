# Validation record

Date: 2026-10-23. Environment: Windows, Python 3.12.10.

Scope: six offline unit tests and live public GitHub API smoke checks. These are not independent agent evaluations or proof of better recommendations.

## Live checks

### Find a reusable skill-discovery workflow

- Repository: vercel-labs/skills
- Commit: `a80e4c9d12d607631249d4d7d059f835d4b2f13a`
- Tree truncated: False
- Skill files discovered: 3
- Result: Selected the requested nested SKILL.md; candidate exists. Compare its workflow against user constraints before installation.
- Evidence: [skills/find-skills/SKILL.md](https://github.com/vercel-labs/skills/blob/a80e4c9d12d607631249d4d7d059f835d4b2f13a/skills/find-skills/SKILL.md), [README.md](https://github.com/vercel-labs/skills/blob/a80e4c9d12d607631249d4d7d059f835d4b2f13a/README.md)

### Find Windows CPU audio-transcription support

- Repository: ThePlasmak/faster-whisper
- Commit: `1c8d6a682c56813a540640babe49d9b270ea708c`
- Tree truncated: False
- Skill files discovered: 1
- Result: Root SKILL.md found; README documents Windows and CPU paths. Offline runtime and dependency compatibility still require implementation inspection and execution; not declared a verified direct fit.
- Evidence: [SKILL.md](https://github.com/ThePlasmak/faster-whisper/blob/1c8d6a682c56813a540640babe49d9b270ea708c/SKILL.md), [README.md](https://github.com/ThePlasmak/faster-whisper/blob/1c8d6a682c56813a540640babe49d9b270ea708c/README.md)

### Find a tool for local PDF processing

- Repository: pymupdf/PyMuPDF
- Commit: `5c51397c79ff087563ae6914a3546f2664fbd3b2`
- Tree truncated: False
- Skill files discovered: 0
- Result: No SKILL.md in the returned complete tree; classify as a library candidate, not an installable skill. GitHub reports AGPL-3.0; inspect licensing terms before adaptation.
- Evidence: [README.md](https://github.com/pymupdf/PyMuPDF/blob/5c51397c79ff087563ae6914a3546f2664fbd3b2/README.md)

## Live search

Query: `pdf translation skill in:readme`. Returned 3 candidates; incomplete_results=False. Search plumbing passed; relevance is not inferred from this count.

- [microsoft/ML-For-Beginners](https://github.com/microsoft/ML-For-Beginners)
- [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)
- [career-ops-hq/career-ops](https://github.com/career-ops-hq/career-ops)

## Limitations

No candidate was installed or executed during these checks. No claim of audio/PDF correctness or security certification. Raw fetched third-party content is not redistributed in this repository. The bundled skill validator passed using an existing environment containing PyYAML; the discovery script itself needs no external packages.
