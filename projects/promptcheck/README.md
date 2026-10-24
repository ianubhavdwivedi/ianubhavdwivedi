# PromptCheck

A dependency-free, local-first static checker for AI prompt templates. It helps prompt authors spot a few common quality and safety concerns before using a prompt in an application.

## What it checks

- Potential instruction-override wording
- Possible requests to expose hidden/system instructions
- Mentions of credentials that may need review
- Overly broad instructions
- Missing task, output-format, or audience guidance
- Empty or very short prompts

PromptCheck reports finding categories and line numbers; it does not print the matched text or send prompt contents to an external service.

## Requirements

- Python 3.10+
- No third-party dependencies

## Usage

Analyze a UTF-8 text file:

```bash
python projects/promptcheck/promptcheck.py prompt.txt
```

Read a prompt from standard input:

```bash
cat prompt.txt | python projects/promptcheck/promptcheck.py
```

Run tests:

```bash
python -m unittest discover -s projects/promptcheck -p 'test_*.py' -v
```

## Limitations

PromptCheck uses static pattern matching, not an AI model. It can produce false positives and miss issues that require context. A warning does not prove a prompt is unsafe, and a clean report does not prove a prompt is safe or effective. Review findings in context and do not use this tool as the sole safety control for production systems.

## License

MIT. See the repository's root license file, if present, for project-wide licensing terms.
