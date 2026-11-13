#!/usr/bin/env python3
"""Check repository document structure without fetching external sources."""

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
from markdown_it.common.utils import normalizeReference
import yaml


FIELDS = (
    "number", "title", "description", "author", "discussions-to", "status",
    "last-call-deadline", "type", "category", "created", "requires", "withdrawal-reason",
)
STATUSES = {"Draft", "Review", "Last Call", "Final", "Living", "Stagnant", "Withdrawn"}
TYPES = {"Standards Track", "Meta", "Informational"}
SECTIONS = (
    "Abstract", "Motivation", "Specification", "Rationale", "Backwards Compatibility",
    "Test Cases", "Reference Implementation", "Implementation and Activation",
    "Security Considerations", "References", "Copyright",
)
REQUIRED_SECTIONS = {
    "Abstract", "Motivation", "Specification", "Rationale", "Backwards Compatibility",
    "Security Considerations", "Copyright",
}
# Repository visibility is maintained explicitly; CI does not need private-source credentials.
INTERNAL_REPOSITORIES = {
    "to-nexus/cross-contracts", "to-nexus/gasabs", "to-nexus/cross-account-contracts",
    "to-nexus/one-account-contracts", "to-nexus/one-account-sdk",
    "to-nexus/one-account-wallet-sample", "to-nexus/one-paymaster-contracts",
    "to-nexus/stake-one-contracts",
}


@dataclass
class Document:
    """Parsed Markdown information used by the repository checks."""

    text: str
    front: str | None
    headings: list[tuple[str, str, int]]
    anchors: set[str]
    links: list[tuple[str, int]]
    rows: list[tuple[str, ...]]
    errors: list[tuple[str, int]]


def _missing_reference(state, silent):
    # Undefined explicit references otherwise become plain text and escape link validation.
    if state.src[state.pos] != "[":
        return False
    match = re.match(r"\[([^\]\n]+)\]\[([^\]\n]*)\]", state.src[state.pos:])
    if not match:
        return False
    label = match[2] or match[1]
    if normalizeReference(label) in state.env.get("references", {}):
        return False
    if not silent:
        token = state.push("missing_reference", "", 0)
        token.content = label
    state.pos += len(match[0])
    return True


def _read_document(path):
    # shortcut: Add HTML link and anchor parsing if documents start using raw HTML for navigation.
    text = path.read_text(encoding="utf-8")
    front = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    body = text[front.end():] if front else text
    offset = text[:front.end()].count("\n") if front else 0
    env = {}
    parser = MarkdownIt("commonmark").enable("table")
    parser.inline.ruler.before("link", "missing_reference", _missing_reference)
    tokens = parser.parse(body, env)
    headings, anchors, links, rows, errors = [], set(), [], [], []
    row = None
    for i, token in enumerate(tokens):
        line = token.map[0] + offset + 1 if token.map else 1
        if token.type == "tr_open":
            row = []
        elif token.type == "inline" and row is not None:
            row.append(token.content.replace(r"\|", "|"))
        elif token.type == "tr_close":
            rows.append(tuple(row))
            row = None
        if token.type == "heading_open":
            title = "".join(child.content for child in tokens[i + 1].children
                            if child.type in {"text", "code_inline", "image"})
            headings.append((token.tag, title, line))
            slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
            anchor, suffix = slug, 0
            while anchor in anchors:
                suffix += 1
                anchor = f"{slug}-{suffix}"
            anchors.add(anchor)
        for child in token.children or []:
            if child.type in {"link_open", "image"}:
                links.append((child.attrGet("href" if child.type == "link_open" else "src"), line))
            elif child.type == "missing_reference":
                errors.append((f"undefined link reference: {child.content}", line))
    # Also check unused reference definitions, which do not produce inline link tokens.
    for reference in env.get("references", {}).values():
        links.append((reference["href"], reference["map"][0] + offset + 1))
    return Document(text, front.group(1) if front else None, headings, anchors, links, rows, errors)


def _metadata(doc, report):
    if doc.front is None:
        report("missing front matter")
        return {}
    try:
        node = yaml.compose(doc.front, Loader=yaml.BaseLoader)
    except yaml.YAMLError as error:
        report(f"invalid YAML metadata: {error}")
        return {}
    if not isinstance(node, yaml.MappingNode):
        report("metadata must be a mapping of key: value lines")
        return {}
    fields = {}
    for key, value in node.value:
        if not isinstance(key, yaml.ScalarNode) or not isinstance(value, yaml.ScalarNode):
            report("metadata fields must be scalar key: value lines")
            continue
        if key.value in fields:
            report(f"duplicate metadata field: {key.value}", key.start_mark.line + 2)
        if not value.value.strip() or value.start_mark.line != value.end_mark.line:
            report(f"metadata field must have a nonempty single-line value: {key.value}")
        fields[key.value] = value.value
    return fields


def _check_proposal(path, doc, report):
    prefix = "oip" if path.parent.name == "OIPs" else "orc"
    name = re.fullmatch(rf"{prefix}-([1-9][0-9]*)\.md", path.name)
    if not name:
        report(f"assign a number before merge; expected {prefix}-N.md")
        return None
    number = int(name[1])
    meta = _metadata(doc, report)
    fields = [prefix if field == "number" else field for field in FIELDS]
    for field in (prefix, "title", "description", "author", "status", "type", "created"):
        if not meta.get(field):
            report(f"missing required metadata field: {field}")
    if meta.get(prefix) != str(number):
        report("filename and metadata number differ")
    for field in meta.keys() - set(fields):
        report(f"unknown metadata field: {field}")
    ordered = [fields.index(field) for field in meta if field in fields]
    if ordered != sorted(ordered):
        report("metadata fields are out of OIP-1 order")
    status, kind = meta.get("status"), meta.get("type")
    if status not in STATUSES:
        report(f"invalid status: {status}")
    if kind not in TYPES or (prefix == "orc" and kind != "Standards Track"):
        report(f"invalid type for {prefix.upper()}: {kind}")
    if prefix == "oip" and kind == "Standards Track":
        if meta.get("category") not in {"Core", "Networking", "Interface"}:
            report("Standards Track OIPs require a valid category")
    elif "category" in meta:
        report("category must be omitted for ORCs and non-Standards Track OIPs")
    if status == "Living" and kind not in {"Meta", "Informational"}:
        report("Living is limited to Meta and Informational proposals")
    for field, required in (("last-call-deadline", status == "Last Call"),
                            ("withdrawal-reason", status == "Withdrawn")):
        if (field in meta) != required:
            report(f"{field} is required only for its corresponding status")
    for field in ("created", "last-call-deadline"):
        if field in meta:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta[field]):
                    raise ValueError
                date.fromisoformat(meta[field])
            except ValueError:
                report(f"{field} must be a valid YYYY-MM-DD date")
    heading = f"{prefix.upper()}-{number}: {meta.get('title', '')}"
    if [title for tag, title, _ in doc.headings if tag == "h1"] != [heading]:
        report(f"expected one top-level heading: # {heading}")
    sections = [title for tag, title, _ in doc.headings if tag == "h2"]
    for section in sorted(REQUIRED_SECTIONS - set(sections)):
        report(f"missing required section: {section}")
    ordered = [SECTIONS.index(section) for section in sections if section in SECTIONS]
    if ordered != sorted(set(ordered)):
        report("proposal sections are duplicated or out of OIP-1 order")
    dependencies = []
    if "requires" in meta:
        if not re.fullmatch(r"[1-9][0-9]*(?:,\s*[1-9][0-9]*)*", meta["requires"]):
            report("requires must be a comma-separated list of positive integers")
        else:
            dependencies = [int(value) for value in meta["requires"].split(",")]
            if len(dependencies) != len(set(dependencies)) or number in dependencies:
                report("requires contains duplicate numbers or a self-dependency")
    return (prefix, number), meta, dependencies


def validate(root):
    """Return diagnostics for tracked and non-ignored new files in a Git checkout."""
    root = root.resolve()
    filenames = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root,
    ).decode().split("\0")
    files = {Path(filename) for filename in filenames if filename}
    errors, documents, proposals = [], {}, {}

    def report(path, message, line=1):
        errors.append(f"{path}:{line}: {message}")

    for filename in sorted(set(filenames)):
        path = Path(filename)
        if path.suffix != ".md":
            continue
        try:
            documents[path] = _read_document(root / path)
        except (OSError, UnicodeError) as error:
            report(path, f"cannot read Markdown: {error}")
    for path, doc in documents.items():
        for message, line in doc.errors:
            report(path, message, line)
        for url, line in doc.links:
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc:
                repo = "/".join(parsed.path.strip("/").split("/")[:2])
                if parsed.hostname == "github.com" and repo in INTERNAL_REPOSITORIES:
                    if "[internal verification sources]" not in doc.text:
                        report(path, f"mark {repo} as internal verification sources", line)
                continue
            target = ((root / path.parent / unquote(parsed.path)) if parsed.path else root / path).resolve()
            if not target.is_relative_to(root):
                report(path, f"relative link escapes the repository: {url}", line)
            elif not target.exists():
                report(path, f"missing link target: {url}", line)
            elif target.is_file() and target.relative_to(root) not in files:
                report(path, f"link target is not a repository file: {url}", line)
            elif parsed.fragment and target.suffix == ".md":
                target_doc = documents.get(target.relative_to(root))
                if target_doc is None:
                    report(path, f"link target is not a repository document: {url}", line)
                elif unquote(parsed.fragment) not in target_doc.anchors:
                    report(path, f"missing heading anchor: {url}", line)
        if path.parent in (Path("OIPs"), Path("ORCs")) and path.name != "README.md":
            result = _check_proposal(path, doc, lambda message, line=1: report(path, message, line))
            if result:
                key, meta, dependencies = result
                proposals[key] = (path, meta, dependencies)

    numbers = {}
    for (prefix, number), (path, meta, dependencies) in proposals.items():
        if number in numbers:
            report(path, f"proposal number {number} is already assigned to {numbers[number]}")
        numbers[number] = path
        for dependency in dependencies:
            target = proposals.get((prefix, dependency))
            if target is None:
                report(path, f"missing dependency in the same namespace: {prefix.upper()}-{dependency}")
            elif meta.get("status") in {"Final", "Living"} and target[1].get("status") not in {"Final", "Living"}:
                report(path, f"{prefix.upper()}-{dependency} must be Final or Living before this proposal")

    visited, active = set(), []

    def visit(key):
        if key in active:
            cycle = " -> ".join(f"{prefix.upper()}-{number}" for prefix, number in active + [key])
            report(proposals[key][0], f"dependency cycle: {cycle}")
            return
        if key in visited or key not in proposals:
            return
        active.append(key)
        for number in proposals[key][2]:
            visit((key[0], number))
        active.pop()
        visited.add(key)

    for key in proposals:
        visit(key)
    for prefix, index in (("oip", Path("README.md")), ("orc", Path("ORCs/README.md"))):
        if index not in documents:
            report(index, "missing proposal index")
            continue
        expected = []
        for (namespace, number), (path, meta, _) in proposals.items():
            if namespace != prefix:
                continue
            target = path.as_posix() if prefix == "oip" else path.name
            cells = [f"[{prefix.upper()}-{number}]({target})", meta.get("title", ""), meta.get("type", "")]
            if prefix == "oip":
                cells.append(meta.get("category", "—"))
            expected.append(tuple(cells + [meta.get("status", "")]))
        actual = [row for row in documents[index].rows if re.match(r"\[(?:OIP|ORC)-", row[0])]
        for row in (Counter(expected) - Counter(actual)).elements():
            report(index, f"missing or outdated index row: {' | '.join(row)}")
        for row in (Counter(actual) - Counter(expected)).elements():
            report(index, f"unexpected or duplicate index row: {' | '.join(row)}")
    return errors


def main():
    """Run the same validation locally and in CI, returning a nonzero code on errors."""
    errors = validate(Path(__file__).resolve().parents[1])
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Document validation failed: {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Document validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
