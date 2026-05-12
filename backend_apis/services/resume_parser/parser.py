import io
import re
from datetime import datetime

import fitz   # PyMuPDF

from .skill_extractor import extract_skills_from_resume


# ─────────────────────────────────────────────────────────────────────────────
# 1. Text extraction from PDF bytes (no temp files)
# ─────────────────────────────────────────────────────────────────────────────

def extract_text(file_bytes: bytes) -> str:
    """Extract text from PDF bytes. sort=True is critical for two-column resumes
    (keeps section headings with their body content)."""
    try:
        parts = []
        with fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf") as doc:
            for page in doc:
                parts.append(page.get_text(sort=True))
        return "\n".join(parts)
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# 2. Email
# ─────────────────────────────────────────────────────────────────────────────

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def extract_email(text: str):
    m = EMAIL_RE.search(text)
    return m.group(0) if m else None


# ─────────────────────────────────────────────────────────────────────────────
# 3. Phone — match loose, filter by digit count (10-13)
# ─────────────────────────────────────────────────────────────────────────────

PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}(?:[-.\s]?\d{3,5})?"
)


def extract_phone(text: str):
    for m in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 10 <= len(digits) <= 13:
            return m.group(0).strip()
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 4. Experience years — "X years" phrases first, fallback to date ranges
# ─────────────────────────────────────────────────────────────────────────────

EXP_RE = re.compile(
    r"(\d{1,2}(?:\.\d)?)\s*\+?\s*(?:years?|yrs?)\b",
    re.IGNORECASE,
)

_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}

_DATE_TOKEN_RE = re.compile(
    r"(?:"
    r"(?P<month_word>[A-Za-z]+)\.?\s+(?P<year_w>\d{4})"
    r"|(?P<month_num>\d{1,2})[/\-](?P<year_n>\d{4})"
    r"|(?P<year_only>(?:19|20)\d{2})"
    r")"
)

_PRESENT_RE = re.compile(
    r"\b(?:present|current|now|till\s+date|to\s+date|ongoing|today)\b",
    re.IGNORECASE,
)


def _parse_date_token(s: str):
    s = s.strip()
    if not s:
        return None
    m = _DATE_TOKEN_RE.fullmatch(s)
    if not m:
        return None
    if m.group("month_word"):
        mw = m.group("month_word").lower()
        if mw not in _MONTHS:
            return None
        return int(m.group("year_w")), _MONTHS[mw]
    if m.group("month_num"):
        return int(m.group("year_n")), max(1, min(12, int(m.group("month_num"))))
    if m.group("year_only"):
        return int(m.group("year_only")), 1
    return None


def estimate_experience_from_date_ranges(text: str) -> float:
    """Sum every detected <date> – <date|Present> span; return years."""
    if not text:
        return 0.0
    now = datetime.now()
    now_y, now_m = now.year, now.month

    range_re = re.compile(
        r"("
        r"(?:[A-Za-z]+\.?\s+\d{4})"
        r"|(?:\d{1,2}[/\-]\d{4})"
        r"|(?:(?:19|20)\d{2})"
        r")"
        r"\s*(?:[-–—]|to)\s*"
        r"("
        r"(?:[A-Za-z]+\.?\s+\d{4})"
        r"|(?:\d{1,2}[/\-]\d{4})"
        r"|(?:(?:19|20)\d{2})"
        r"|(?:present|current|now|till\s+date|to\s+date|ongoing|today)"
        r")",
        re.IGNORECASE,
    )

    intervals = []
    for m in range_re.finditer(text):
        start = _parse_date_token(m.group(1))
        if not start:
            continue
        end_raw = m.group(2)
        if _PRESENT_RE.fullmatch(end_raw.strip()):
            end = (now_y, now_m)
        else:
            end = _parse_date_token(end_raw)
            if not end:
                continue
        s_total = start[0] * 12 + start[1]
        e_total = end[0] * 12 + end[1]
        if e_total <= s_total:
            continue
        if e_total - s_total > 50 * 12:
            continue
        intervals.append((s_total, e_total))

    if not intervals:
        return 0.0

    # Merge overlapping intervals so concurrent jobs aren't double-counted
    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))

    total_months = sum(e - s for s, e in merged)
    return round(total_months / 12.0, 1)


def extract_experience(text: str) -> float:
    years = []
    for m in EXP_RE.finditer(text):
        try:
            years.append(float(m.group(1)))
        except ValueError:
            continue
    if years:
        return max(years)
    return estimate_experience_from_date_ranges(text)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Name — heuristic from first 8 lines
# ─────────────────────────────────────────────────────────────────────────────

URL_RE = re.compile(r"https?://|www\.|linkedin\.com|github\.com", re.IGNORECASE)
NAME_RE = re.compile(r"^[A-Z][a-zA-Z'.\-]+(?:\s+[A-Z][a-zA-Z'.\-]+){1,3}$")


def extract_name(text: str):
    """First non-empty line in first 8 that looks like 2-4 capitalized words,
    no digits, no email/phone/URL markers."""
    if not text:
        return None

    for raw in text.splitlines()[:8]:
        line = raw.strip()
        if not line:
            continue
        # Strip a "Name:" / "Name -" prefix if present
        line = re.sub(r"^(?:name|full\s+name)\s*[:\-]\s*", "", line, flags=re.IGNORECASE)
        if EMAIL_RE.search(line):
            continue
        if URL_RE.search(line):
            continue
        if "@" in line or "+" in line:
            continue
        if any(ch.isdigit() for ch in line):
            continue
        if NAME_RE.match(line):
            return line.title()
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 6. Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def parse_resume(file_bytes: bytes) -> dict:
    text = extract_text(file_bytes)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "experience_years": extract_experience(text),
        "skills": extract_skills_from_resume(text),
    }
