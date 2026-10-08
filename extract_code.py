"""Extract the Python and R chunks from each session page into plain code files in code/."""
import re, pathlib
root = pathlib.Path(__file__).parent
for qmd in sorted((root / "sessions").glob("*.qmd")):
    num = qmd.name[:2]
    text = qmd.read_text()
    title = re.search(r'^title:\s*"(.*)"', text, re.M).group(1)
    for lang, ext, comment in [("python", "py", "#"), ("r", "R", "#")]:
        chunks = re.findall(r"```\{?%s\}?\n(.*?)```" % lang, text, re.S)
        # walkthrough chunks come before the "## Exercises" heading; keep only those
        body = text.split("## Exercises")[0]
        chunks = re.findall(r"```\{?%s\}?\n(.*?)```" % lang, body, re.S)
        if not chunks:
            continue
        header = f"{comment} {title}\n{comment} {lang.capitalize()} code extracted from sessions/{qmd.name}\n{comment} Run from the repository root so that data/ paths resolve.\n\n"
        out = header + "\n\n".join(f"{comment} ---- step {i+1} ----\n{c.strip()}" for i, c in enumerate(chunks)) + "\n"
        (root / "code" / f"session{num}.{ext}").write_text(out)
        print(f"wrote code/session{num}.{ext} ({len(chunks)} chunks)")
