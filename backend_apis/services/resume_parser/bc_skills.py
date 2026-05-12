import json
from functools import lru_cache
from pathlib import Path


_JSON_PATH = Path(__file__).parent / "blue_collar_skills.json"


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def get_canonical_set() -> frozenset:
    """Emit-side vocabulary: lowercase canonical skill names."""
    data = _load()
    out = set()
    for skills in data.get("categories", {}).values():
        for s in skills:
            s = (s or "").strip().lower()
            if s:
                out.add(s)
    return frozenset(out)


@lru_cache(maxsize=1)
def get_alias_map() -> dict:
    """alias_lower -> canonical_lower."""
    raw = _load().get("aliases", {}) or {}
    return {
        k.lower().strip(): v.lower().strip()
        for k, v in raw.items()
        if isinstance(v, str) and v.strip() and not k.startswith("_")
    }


@lru_cache(maxsize=1)
def get_scan_vocab() -> frozenset:
    """Vocabulary used when scanning text: canonicals + aliases."""
    return get_canonical_set() | frozenset(get_alias_map().keys())


def canonicalize(skill: str) -> str:
    """Map alias -> canonical, or pass through if already canonical."""
    s = (skill or "").lower().strip()
    return get_alias_map().get(s, s)
