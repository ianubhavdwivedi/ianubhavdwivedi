"""PromptCheck: a dependency-free static checker for AI prompt templates.

It flags common prompt-quality and safety issues without sending prompt text
to any external service. This is a lightweight review aid, not a model-based
safety classifier.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


RULES: tuple[tuple[str, str, re.Pattern[str], str], ...] = (
    ("warning", "P001", re.compile(r"(?i)\b(ignore|disregard|override)\b.{0,50}\b(previous|prior|above|system|developer)\b"),
     "Potential instruction-override wording. Check whether this is intentional test content."),
    ("warning", "P002", re.compile(r"(?i)\b(reveal|print|show|repeat|expose)\b.{0,50}\b(system prompt|hidden instructions|secret instructions)\b"),
     "Possible request to expose hidden instructions."),
    ("warning", "P003", re.compile(r"(?i)\b(api[_ -]?key|password|access token|client secret)\b"),
     "Prompt mentions credentials. Make sure real secrets are not embedded in the template."),
    ("info", "P004", re.compile(r"(?i)\b(do anything|whatever it takes|no restrictions)\b"),
     "Broad instruction detected. Add specific scope and constraints if appropriate."),
)


def analyze(text: str) -> list[Finding]:
    """Return static prompt review findings; never returns matched text."""
    findings: list[Finding] = []
    stripped = text.strip()
    if not stripped:
        return [Finding("error", "P000", "Prompt is empty.")]

    if len(stripped) < 40:
        findings.append(Finding("info", "P010", "Prompt is very short; add context, goal, and expected output where useful."))
    if not re.search(r"(?i)\b(task|goal|objective|please|create|write|explain|summarize|analyze|generate)\b", stripped):
        findings.append(Finding("info", "P011", "No clear task verb or goal marker detected; verify the requested action is explicit."))
    if not re.search(r"(?i)\b(format|structure|JSON|table|bullet|length|audience|tone|example)\b", stripped):
        findings.append(Finding("info", "P012", "No output format or audience guidance detected; add it if consistency matters."))

    for line_number, line in enumerate(text.splitlines(), start=1):
        for severity, code, pattern, message in RULES:
            if pattern.search(line):
                findings.append(Finding(severity, code, message, line_number))

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review an AI prompt template for common quality and safety issues.")
    parser.add_argument("file", nargs="?", help="UTF-8 text file containing a prompt; omit to read stdin")
    args = parser.parse_args(argv)

    try:
        content = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    except (OSError, UnicodeError) as exc:
        print(f"promptcheck: cannot read input: {exc}", file=sys.stderr)
        return 2

    findings = analyze(content)
    for finding in findings:
        location = f":{finding.line}" if finding.line is not None else ""
        print(f"{finding.severity.upper()} {finding.code}{location}: {finding.message}")

    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    print(f"Review complete: {len(findings)} finding(s), {warnings} warning(s), {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
