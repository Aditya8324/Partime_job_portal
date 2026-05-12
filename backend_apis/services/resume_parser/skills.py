import re

from . import bc_skills


def get_corpus_vocab() -> frozenset:
    """Vocabulary used to scan text for skill mentions."""
    return bc_skills.get_scan_vocab()


def find_skills(text: str, vocab: frozenset = None) -> set:
    """Word-boundary scan against the whitelist.

    Returns canonical skill forms only. Custom boundaries respect
    +, #, ., -, _ so tokens like 'c++' / 'node.js' match correctly.
    """
    if not text:
        return set()
    if vocab is None:
        vocab = get_corpus_vocab()
    if not vocab:
        return set()

    lower = text.lower()
    found = set()
    for skill in vocab:
        pattern = rf"(?<![a-z0-9+#._-]){re.escape(skill)}(?![a-z0-9+#._-])"
        if re.search(pattern, lower):
            found.add(bc_skills.canonicalize(skill))
    return found
