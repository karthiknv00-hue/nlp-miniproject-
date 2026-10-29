"""A small, beginner-friendly spelling corrector using edit distance."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

WORD_PATTERN = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")


def levenshtein_distance(first: str, second: str) -> int:
    """Return the minimum insertions, deletions, and substitutions needed."""
    if len(first) < len(second):
        first, second = second, first
    previous = list(range(len(second) + 1))
    for row, char1 in enumerate(first, start=1):
        current = [row]
        for column, char2 in enumerate(second, start=1):
            current.append(min(current[-1] + 1, previous[column] + 1,
                               previous[column - 1] + (char1 != char2)))
        previous = current
    return previous[-1]


def load_vocabulary(path: str | Path) -> set[str]:
    """Load one word per line, normalized to lowercase."""
    vocabulary_path = Path(path)
    try:
        return {line.strip().lower() for line in vocabulary_path.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")}
    except OSError as exc:
        raise FileNotFoundError(f"Could not read vocabulary file: {vocabulary_path}") from exc


def _case_like(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source.istitle():
        return replacement.capitalize()
    return replacement


def _is_single_transposition(first: str, second: str) -> bool:
    """Identify a likely adjacent-letter swap, such as teh -> the."""
    if len(first) != len(second):
        return False
    differences = [index for index, (left, right) in enumerate(zip(first, second)) if left != right]
    return (len(differences) == 2 and differences[1] == differences[0] + 1
            and first[differences[0]] == second[differences[1]]
            and first[differences[1]] == second[differences[0]])


class SpellingCorrector:
    """Detect unknown words and rank vocabulary candidates by edit distance."""
    def __init__(self, vocabulary: Iterable[str], max_edit_distance: int = 2):
        if max_edit_distance < 0:
            raise ValueError("max_edit_distance must be zero or greater")
        self.vocabulary = {word.strip().lower() for word in vocabulary if word.strip()}
        self.max_edit_distance = max_edit_distance

    def suggestions(self, word: str, limit: int = 5) -> list[str]:
        """Return up to five close vocabulary words, nearest first."""
        normalized = word.lower()
        if normalized in self.vocabulary or limit <= 0:
            return []
        matches: list[tuple[int, int, str]] = []
        for candidate in self.vocabulary:
            if abs(len(candidate) - len(normalized)) > self.max_edit_distance:
                continue
            distance = levenshtein_distance(normalized, candidate)
            if distance <= self.max_edit_distance:
                transposition_rank = 0 if _is_single_transposition(normalized, candidate) else 1
                matches.append((distance, transposition_rank, candidate))
        # An adjacent swap is a common typo; keep it visible in the short list.
        matches.sort(key=lambda item: (item[1], item[0], item[2]))
        return [_case_like(word, candidate) for _, _, candidate in matches[:min(limit, 5)]]

    def check_text(self, text: str) -> dict[str, object]:
        """Analyze text and group repeated misspellings into one entry each."""
        errors: dict[str, dict[str, object]] = {}
        for match in WORD_PATTERN.finditer(text):
            original = match.group()
            normalized = original.lower()
            if normalized in self.vocabulary:
                continue
            if normalized not in errors:
                errors[normalized] = {"word": original, "count": 0,
                                      "suggestions": self.suggestions(original)}
            errors[normalized]["count"] = int(errors[normalized]["count"]) + 1
        return {"original_text": text, "misspellings": errors}

    def correct_text(self, text: str, choices: dict[str, str] | None = None) -> str:
        """Apply chosen corrections while leaving unmatched text untouched."""
        choices = choices or {}

        def replace(match: re.Match[str]) -> str:
            original = match.group()
            replacement = choices.get(original.lower())
            return _case_like(original, replacement) if replacement else original

        return WORD_PATTERN.sub(replace, text)
