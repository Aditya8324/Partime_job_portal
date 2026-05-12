import re

from . import bc_skills
from .skills import find_skills, get_corpus_vocab


# Heading regex parts
_HEAD_PFX = r"^[^A-Za-z\n]*"                # leading bullets/emoji/whitespace
_HEAD_SFX = r"[\s:.\-–—…]*$"                # trailing punctuation
_HEAD_QUALIFIER = r"(?:(?:[A-Za-z][A-Za-z\-]{0,15})\s+){0,2}"
_HEAD_TRAILER = r"(?:\s+section)?(?:\s+\([^)]*\))?"


_SKILL_HEADING = re.compile(
    rf"""
    {_HEAD_PFX}
    {_HEAD_QUALIFIER}
    (?:
        technical\s+skills?
      | core\s+(?:technical\s+)?skills?
      | key\s+skills?
      | skills?\s*(?:\&|and)\s*(?:tools?|technologies)
      | tools?\s*(?:\&|and)\s*technologies
      | tech(?:nical)?\s+stack
      | technologies
      | areas?\s+of\s+expertise
      | expertise
      | competencies
      | skills?
    )
    {_HEAD_TRAILER}
    {_HEAD_SFX}
    """,
    re.IGNORECASE | re.VERBOSE,
)


_NEXT_HEADING = re.compile(
    rf"""
    {_HEAD_PFX}
    {_HEAD_QUALIFIER}
    (?:
        (?:professional\s+|work\s+)?experience
      | employment(?:\s+history)?
      | work\s+history
      | (?:job\s+)?responsibilities
      | (?:job\s+)?duties
      | education(?:al\s+qualifications?)?
      | academic(?:\s+(?:background|qualifications?))?
      | projects?
      | (?:key\s+)?achievements?
      | awards?
      | certifications?
      | publications?
      | languages?(?:\s+known)?
      | hobbies(?:\s+(?:and|&)\s+interests?)?
      | interests?
      | references?
      | profile
      | summary
      | objective
      | personal\s+(?:details?|information|profile)
      | contact(?:\s+(?:details|information))?
      | declaration
      | strengths
      | training
      | accomplishments
    )
    {_HEAD_TRAILER}
    {_HEAD_SFX}
    """,
    re.IGNORECASE | re.VERBOSE,
)


_INLINE_SKILL_RE = re.compile(
    r"""
    ^
    [^A-Za-z\n]*
    (?:[A-Za-z][A-Za-z\-]{0,15}\s+){0,2}
    (?:
        technical\s+skills?
      | core\s+(?:technical\s+)?skills?
      | key\s+skills?
      | tech(?:nical)?\s+stack
      | technologies
      | areas?\s+of\s+expertise
      | expertise
      | competencies
      | tools?\s*(?:\&|and)\s*technologies
      | skills?\s*(?:\&|and)\s*(?:tools?|technologies)
      | skills?
    )
    \s*[:\-]\s*
    (?P<body>.+?)
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE | re.MULTILINE,
)


_DELIMITERS = re.compile(r"[•·▪◦●○■►▸•●\|;,/]+|\s{2,}|\n")
_LABEL_STRIP = re.compile(r"^[A-Za-z][A-Za-z &/+\-]{0,40}\s*:\s*", re.IGNORECASE)
_LABEL_ONLY = re.compile(r"^\s*[A-Za-z][A-Za-z &/+\-]{0,40}\s*[:\-]\s*$", re.IGNORECASE)

_JUNK_TOKENS = {
    "etc", "and", "or", "with", "in", "on", "of", "the", "a", "an",
    "&", "/", "-", "—", "–",
    "from", "to", "till", "by", "for", "as", "at",
    "i", "ii", "iii", "iv", "v",
    "et", "al", "etc.",
}

_NUMBERED_LIST_RE = re.compile(r"^\s*\d{1,3}[.)]\s*")
_DATE_RANGE_RE = re.compile(
    r"^\s*\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|^(?:19|20)\d{2}\s*[-–to]+\s*(?:19|20)\d{2}|^from\s|\bto\s+\d{4}",
    re.IGNORECASE,
)
_PROFICIENCY_SUFFIX = re.compile(
    r"\s*[-–—:]\s*(?:expert|beginner|intermediate|advanced|proficient|master|"
    r"skilled|novice|basic|fluent|native|professional|excellent|good|fair|"
    r"working\s+knowledge|hands[\s\-]on)\s*$",
    re.IGNORECASE,
)


def _clean_token(tok: str) -> str:
    tok = tok.strip(" \t-:.;'\"()[]")
    tok = _LABEL_STRIP.sub("", tok)
    tok = _NUMBERED_LIST_RE.sub("", tok)
    tok = _PROFICIENCY_SUFFIX.sub("", tok)
    tok = re.sub(r"\s+", " ", tok)
    return tok.strip().lower()


def find_skills_section(text: str):
    """Find the Skills section body, or None.

    Mode A (inline): 'Technical Skills: Python, Java, AWS' on one line.
    Mode B (block):  heading on its own line, body until next heading.
    """
    MAX_BODY_LINES = 30
    if not text:
        return None

    # Mode A: inline
    for m in _INLINE_SKILL_RE.finditer(text):
        body = m.group("body").strip()
        if len(body) >= 5 and re.search(r"[,/|;•·●▪]|\s\s", body):
            return body

    # Mode B: block
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if _SKILL_HEADING.match(line):
            start = i + 1
            break
    if start is None:
        return None

    end = min(len(lines), start + MAX_BODY_LINES)
    for j in range(start, end):
        if _NEXT_HEADING.match(lines[j]):
            end = j
            break

    body = "\n".join(lines[start:end]).strip()
    return body or None


def tokenize_skills(section_body: str) -> list:
    if not section_body:
        return []
    section_body = re.sub(r"[()\[\]{}]", ",", section_body)
    pieces = _DELIMITERS.split(section_body)
    out, seen = [], set()
    for raw in pieces:
        if _DATE_RANGE_RE.match(raw):
            continue
        if _LABEL_ONLY.match(raw):
            continue
        t = _clean_token(raw)
        if not t or len(t) < 2 or len(t) > 60:
            continue
        if t in _JUNK_TOKENS:
            continue
        if re.fullmatch(r"[0-9.+\-/\s]+(?:years?|yrs?)?", t):
            continue
        if re.search(r"\b(?:19|20)\d{2}\b", t):
            continue
        if t.startswith(("from ", "to ", "till ")):
            continue
        if t.count(" ") > 4:
            continue
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def extract_skills_from_resume(text: str) -> list:
    """Two-pass extraction against the whitelist.

    Pass 1: tokenize the Skills section, keep tokens that canonicalize to whitelist.
    Pass 2: scan section text for whitelist phrases (catches multi-word skills).
    """
    section = find_skills_section(text)
    if section is None:
        return []

    out = []
    seen = set()

    # Pass 1: tokenize → canonicalize → whitelist filter
    for tok in tokenize_skills(section):
        canonical = bc_skills.canonicalize(tok)
        if canonical in seen:
            continue
        if canonical in bc_skills.get_canonical_set():
            out.append(canonical)
            seen.add(canonical)

    # Pass 2: phrase scan on the section text
    for skill in find_skills(section, vocab=get_corpus_vocab()):
        if skill not in seen:
            out.append(skill)
            seen.add(skill)

    return out
