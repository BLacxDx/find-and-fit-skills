# Find and Fit Skills

**Find an existing tool. Check the fit. Adapt only the gap.**

[中文介绍](README.zh-CN.md)

Find and Fit is an agent skill that helps an AI assistant turn a real requirement into a usable tool choice. It searches for existing skills and open-source tools, checks their source and runtime requirements, and proposes the smallest adaptation for unmet needs.

## What it does

- Extracts constraints such as Windows support, offline use, cost and output format.
- Searches available sources, with a bundled read-only GitHub helper as a fallback.
- Reads actual source evidence and records commit-pinned links and unknowns.
- Distinguishes an installable skill from a standalone library or CLI.
- Verifies package identity, runtime dependencies and actual output before calling a recommendation successful.

It can also conclude that an installed capability already suffices or that no suitable match was established.

## A complete example

**Request:** Convert a public English EPUB into chapter Markdown, in reading order, without a paid API.

The workflow searched GitHub and the web, inspected three candidates, rejected a Windows setup mismatch, and selected npm `epub2md`. The default output included navigation and publisher pages, so a small adapter used the tool's public API to produce 12 chapter files. An independent ZIP/XML-based verifier matched 27,336 normalized word tokens, chapter titles and order against the source EPUB. Deliberately missing text and swapped chapter order were detected.

[Read the discovery-to-execution report and reproduce it](examples/epub-to-markdown/README.md).

This is one assistant-run case, not an independent A/B evaluation or proof of general improvement. The book was external to the tool, but the adapter was developed and verified on that same book.

## Install in Codex

Copy `skills/find-and-fit` into your Codex skills directory, normally `~/.codex/skills/` (or the `skills` directory under your configured CODEX_HOME). Do not overwrite an existing customized copy without comparing it.

```text
git clone https://github.com/BLacxDx/find-and-fit-skills.git
```

Windows PowerShell, using the default skills directory:

```powershell
Copy-Item -Recurse ./find-and-fit-skills/skills/find-and-fit "$env:USERPROFILE/.codex/skills/"
```

In a new conversation:

```text
Use $find-and-fit to find a tool for converting EPUBs into chapter Markdown on Windows. No paid API. Compare candidates, run the best fit, and verify the result against the source.
```

Automatic selection is permitted; actual routing depends on the host. Other SKILL.md-compatible clients have not been individually tested.

## Standalone discovery helper

Python 3.10+, standard library only. Run from the repository root:

```text
python skills/find-and-fit/scripts/discover.py search "epub markdown in:name,description" --limit 5
python skills/find-and-fit/scripts/discover.py inspect uxiew/epub2MD
```

The helper returns public GitHub metadata, license metadata, skill paths, commit-pinned file links and untrusted source text. It does not install or execute candidates. It reads at most three skills and one root README per inspection; oversized files and incomplete trees are reported.

Repository search is not a complete skill index and may return irrelevant results. The assistant must check conversion direction and constraints. Anonymous GitHub API requests can be rate-limited; errors are not empty results. Never include private data in public search queries. Tool discovery requires a network connection; execution requirements depend on the selected tool.

## Validation

```text
python -m unittest discover -s tests -v
```

- Six helper regression tests and Skill format validation passed.
- [Initial live search and repository checks](examples/validation.md).
- [PDF table adaptation](examples/pdf-table/README.md): reuse of an existing skill's tool, not discovery proof.
- [EPUB search-to-execution case](examples/epub-to-markdown/README.md): three candidates, one executed package, one narrow adaptation and source-based output checks.

Example dependencies are separate from the dependency-free discovery helper. Detailed limitations are recorded in each report.

## Related work and scope

[Vercel find-skills](https://github.com/vercel-labs/skills/tree/main/skills/find-skills) already supports skill discovery and installation. This project focuses on requirement fit, evidence, runtime mismatches and small tested adaptations. It does not claim to invent skill search or outperform existing finders.

There is no automatic installer, semantic ranking model, general security auditor or autonomous patch engine. The host assistant performs reasoning and authorized implementation. No funding or promotional eligibility is guaranteed.

## Contribute

Report the task, constraints, expected output and actual failure. For code changes, run the tests above. Keep new discovery sources read-only, bounded and explicit about missing evidence.

MIT License. Maintained by BLacxDx; code and documentation are AI-assisted.
